#!/usr/bin/env python

import sys, getopt, re
import fparser
from fparser import parsefortran
from fparser import api
from fparser import readfortran
from fparser import block_statements, statements

def enum(**enums):
    return type('Enum', (), enums)

class claw_parser:
    def __init__(self, infile, outfile, keep_pragma=True):
        self.infile = infile
        self.outfile = outfile
        self.keep_pragma = keep_pragma
        self.directives = enum(LOOP_FUSION=1, LOOP_INTERCHANGE=2)
        self.__crt_block_content = None

    def __parse(self):
        reader = api.get_reader(self.infile, True, False, None, None)
        parser = parsefortran.FortranParser(reader, False)
        parser.parse()
        return parser.block

    def translate(self):
        main_block = self.__parse()
        self.__process_main_block(main_block)
        data = str(main_block).splitlines(True)
        if not self.outfile == '':
            f = open(self.outfile, 'w')
            f.writelines(data[1:])
            f.close()
        else:
            print main_block

    def __process_main_block(self, block):
        self.__crt_block_content = block.content
        for i, s in enumerate(block.content):
            self.__process_stmt(s, i, block.content)

    def __process_stmt(self, stmt, id, parent_block):
        self.__process_item(stmt, id, parent_block)
        if hasattr(stmt, 'content'):
            for i, s in enumerate(stmt.content):
                self.__process_stmt(s, i, stmt.content)

    # Possible item types: Line, SyntaxErrorLine, Comment, MultiLine,
    # SyntaxErrorMultiLine
    def __process_item(self, stmt, id, parent_block):
        if hasattr(stmt, 'item'):
            if isinstance(stmt.item, readfortran.Comment):
                self.__process_comment(stmt.item, id, parent_block)

    def __get_stmt_line(self, stmt):
        return stmt.item.span[0]

    def __is_loop_fusion(self, comment):
        if self.__is_pragma(comment) and self.__is_claw_pragma(comment) and\
        self.__is_valid_claw_pragma(comment):
           claw_dir = self.__get_claw_directive(comment)
           if(claw_dir == self.directives.LOOP_FUSION):
               return True
           return False


    def __process_comment(self, comment, id, parent_block):
        if not isinstance(comment, readfortran.Comment):
            return
        if self.__is_pragma(comment):
            if self.__is_claw_pragma(comment):
                # process claw pragma
                if self.__is_valid_claw_pragma(comment):
                    claw_dir = self.__get_claw_directive(comment)

                    # loop-fusion directive detected
                    if(claw_dir == self.directives.LOOP_FUSION):
                        #TODO verbose print 'loop-fusion detected index:' + str(id)
                        # find the loop associated with it
                        pragma_position = id;
                        base_group = self.__get_group_option_value(comment)
                        base_loop_position = self.__next_loop_index(id, parent_block)
                        for i, s in enumerate(parent_block):
                            if i <= pragma_position:
                                continue
                            else:
                                if isinstance(s, statements.Comment):
                                    if self.__is_loop_fusion(s.item):
                                        slave_group = self.__get_group_option_value(s.item)
                                        if slave_group == base_group:
                                            # loop can be merge
                                            # TODO compare iteration range
                                            loop_position = self.__next_loop_index(i, parent_block)

                                            if(loop_position == -1):
                                                print 'loop not found'
                                            else:
                                                del parent_block[i] # delete pragma
                                                loop_position = loop_position - 1
                                                del parent_block[loop_position].content[-1]
                                                body = []
                                                for j, stmt in enumerate(parent_block[base_loop_position].content):
                                                    if(j == len(parent_block[base_loop_position].content) - 1):
                                                        continue
                                                    else:
                                                        body.append(stmt)
                                                for s in parent_block[loop_position].content:
                                                    body.append(s)

                                                body.append(parent_block[base_loop_position].content[-1])
                                                parent_block[base_loop_position].content = body
                                                del parent_block[loop_position]


                    # loop-interchange directive detected
                    elif(claw_dir == self.directives.LOOP_INTERCHANGE):
                        print 'loop-interchange detected index:' + str(id)

                # Invalid claw pragma
                else:
                    # Error
                    self.__exit_error(directive = comment.comment, linenum = comment.span[0])

    def __next_loop_index(self, crt_position, parent_block):
        for i, s in enumerate(parent_block):
            if i <= crt_position:
                continue
            else:
                if isinstance(s, block_statements.Do):
                    return i
        return -1

    def __process_line(self, line):
        if not isinstance(line, readfortran.Line):
            return
        self.__add_to_code_map(line.line)

    # Check if the comment is a pragma statement (starts with !$)
    def __is_pragma(self, comment_stmt):
        if(comment_stmt.comment != ''):
            p_pragma = re.compile('^\s*!\$')
            if(p_pragma.match(comment_stmt.comment)):
                return True
        return False

    # Check if the pragma statement starts with !$claw
    def __is_claw_pragma(self, comment_stmt):
        if(comment_stmt.comment != ''):
            p_pragma = re.compile('^\s*!\$claw', flags=re.IGNORECASE)
            if(p_pragma.match(comment_stmt.comment)):
                return True
        return False

    # Validate the structure of a claw pragma statement
    # For the moment accepting loop-fusion and loop-interchange wuthout option
    def __is_valid_claw_pragma(self, pragma_stmt):
        p_claw = re.compile('^\s*!\$claw\s*(loop\-fusion|loop\-interchange)', \
        flags=re.IGNORECASE)
        if p_claw.match(pragma_stmt.comment):
            return True
        else:
            return False

    # Return the type of claw pragma statement
    def __get_claw_directive(self, pragma_stmt):
        p_claw_fusion = re.compile('^\s*!\$claw\s*loop\-fusion', \
        flags=re.IGNORECASE)
        p_claw_interchange = re.compile('^\s*!\$claw\s*loop\-interchange', \
        flags=re.IGNORECASE)
        if(p_claw_fusion.match(pragma_stmt.comment)):
            return self.directives.LOOP_FUSION
        if(p_claw_interchange.match(pragma_stmt.comment)):
            return self.directives.LOOP_INTERCHANGE

    def __get_group_option_value(self, pragma_stmt):
        p_loop_fusion_group = re.compile( \
          '^\s*!\$claw\s*loop\-fusion\s*group\s*\((.*)\)', \
          flags=re.IGNORECASE)
        m = p_loop_fusion_group.match(pragma_stmt.comment)
        if m:
            return m.group(1).strip()
        return ''

    def __get_reorder_option_value(self, pragma_stmt):
        p_loop_interchange_reorder = re.compile( \
          '^\s*!\$claw\s*loop\-interchange\s*\((.*)\)', \
          flags=re.IGNORECASE)
        m = p_loop_interchange_reorder.match(pragma_stmt.comment)
        if m:
            return m.group(1).strip()
        return ''

    # error handling
    def __exit_error(self, directive = '', msg = '', linenum = 0):
        print('File: "' + self.infile + '", line ' + str(linenum))
        if directive:
            print('SyntaxError: Invalid claw directive - ' + directive)
        if msg:
            print('Message: ' + msg)
        if not linenum == 0:
            print('Line :' + str(linenum))
        sys.exit(1)

# end of class claw_parser



def print_help():
    print 'claw_c.py -i <inputfile> [-o <outputfile>] [-p]'
    print '  -p : Remove the claw directives in transformed code'

def main(argv):
    inputfile = ''
    outputfile = ''
    keep_pragma = True
    try:
        opts, args = getopt.getopt(argv,"hpi:o:")
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt == "-i":
            inputfile = arg
        elif opt == "-o":
            outputfile = arg
        elif opt == "-p":
            keep_pragma = False
    if inputfile == '':
        print_help()
        sys.exit()
    else:
        claw = claw_parser(inputfile, outputfile, keep_pragma=keep_pragma)
        claw.translate()

if __name__ == "__main__":
    main(sys.argv[1:])
