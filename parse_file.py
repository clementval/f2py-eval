#!/usr/bin/env python

import sys, getopt, re
import fparser
from fparser import parsefortran
from fparser import api
from fparser import readfortran
from fparser import block_statements

def enum(**enums):
    return type('Enum', (), enums)

class loop_fusion:
    def __init__(self, start_line, depth = 0, stop_line = 0, group_label = ''):
        self.__start_line = start_line
        self.__stop_line = stop_line
        self.__depth = depth
        self.__group_label = group_label

        self.translated = False

    def set_stop_line(self, stop_line):
        self.__stop_line = stop_line

    def get_start_line(self):
        return self.__start_line

    def print_info(self):
        print 'loop-fusion ' + self.__group_label
        print '  start: ' + str(self.__start_line)
        print '  stop:  ' + str(self.__stop_line)
        print '  depth: ' + str(self.__depth)



class claw_parser:
    def __init__(self, infile, outfile, keep_pragma=True):
        self.infile = infile
        self.outfile = outfile
        self.keep_pragma = keep_pragma
        self.directives = enum(LOOP_FUSION=1, LOOP_INTERCHANGE=2)
        self.__crt_line = 1
        self.__crt_depth = 0
        self.__code_map = {}
        self.__code_map_printed = {}
        self.__loop_hunting = False # Tells the translator to find next loop
        self.__crt_loop_fusion = None
        self.__loop_fusions = {}


    def __parse(self):
        reader = api.get_reader(self.infile, True, False, None, None)
        parser = parsefortran.FortranParser(reader, False)
        parser.parse()
        return parser.block

    def translate(self):
        main_block = self.__parse()
        self.__process_main_block(main_block)
        self.__print_code_map()
        #for loop in sorted(self.__loop_fusions):
        #    print self.__loop_fusions[loop].print_info()


    def __print_code_map(self):
        for linenum in self.__code_map:
            if not self.__code_map_printed[linenum]:
                print self.__code_map[linenum]
                self.__code_map_printed[linenum] = True

    def print_block_info(block):
        print '####### BLOCK INFORMATION #######'
        print 'Root blocktype: ' + block.blocktype
        print '  name:   ' + block.blocktype
        print '  content:'
        print block.content

    def __process_main_block(self, block):
        for stmt in block.content:
            self.__process_stmt(stmt)

    def __process_stmt(self, stmt):
        self.__process_item(stmt)
        if hasattr(stmt, 'content'):
            self.__crt_depth += 1
            for s in stmt.content:
                self.__process_stmt(s)
            self.__crt_depth -= 1


    # Possible item types: Line, SyntaxErrorLine, Comment, MultiLine,
    # SyntaxErrorMultiLine
    def __process_item(self, stmt):
        if hasattr(stmt, 'item'):
            if isinstance(stmt.item, readfortran.Comment):
                self.__process_comment(stmt.item)
            elif isinstance(stmt.item, readfortran.Line):
                if self.__loop_hunting and isinstance(stmt, block_statements.Do):
                    linenum = self.__get_stmt_line(stmt)
                    self.__crt_loop_fusion = loop_fusion(linenum, depth = self.__crt_depth)
                if self.__loop_hunting and isinstance(stmt, block_statements.EndDo):
                    linenum = self.__get_stmt_line(stmt)
                    self.__crt_loop_fusion.set_stop_line(linenum)
                    self.__loop_fusions[self.__crt_loop_fusion.get_start_line()] = self.__crt_loop_fusion
                    self.__loop_hunting = False
                self.__process_line(stmt.item)

    def __get_stmt_line(self, stmt):
        return stmt.item.span[0]

    def __process_comment(self, comment):
        if not isinstance(comment, readfortran.Comment):
            return
        if self.__is_pragma(comment):
            if self.__is_claw_pragma(comment):
                # process claw pragma
                if self.__is_valid_claw_pragma(comment):
                    claw_dir = self.__get_claw_directive(comment)
                    if(claw_dir == self.directives.LOOP_FUSION):
                        self.__loop_hunting = True
                    elif(claw_dir == self.directives.LOOP_INTERCHANGE):
                        print '! LOOP_INTERCHANGE'

                    # just output pragma if option is to keep them
                    if self.keep_pragma:
                        self.__add_to_buffer(comment.comment)
                else:
                    # Error
                    self.__exit_error(directive = comment.comment, linenum = comment.span[0])
            else: # other pragma are kept in the output
                self.__add_to_buffer(comment.comment)
        else:
            self.__add_to_buffer(comment.comment)

    def __process_line(self, line):
        if not isinstance(line, readfortran.Line):
            return
        self.__add_to_buffer(line.line)



    def __add_to_buffer(self, line):
        self.__code_map[self.__crt_line] = line
        self.__code_map_printed[self.__crt_line] = False
        self.__crt_line += 1

    # Check if the comment is a pragma statement (starts with !$)
    def __is_pragma(self, comment_stmt):
        if(comment_stmt.comment != ''):
            p_pragma = re.compile('^!\$')
            if(p_pragma.match(comment_stmt.comment)):
                return True
        return False

    # Check if the pragma statement starts with !$claw
    def __is_claw_pragma(self, comment_stmt):
        if(comment_stmt.comment != ''):
            p_pragma = re.compile('^!\$claw')
            if(p_pragma.match(comment_stmt.comment)):
                return True
        return False

    # Validate the structure of a claw pragma statement
    # For the moment accepting loop-fusion and loop-interchange wuthout option
    def __is_valid_claw_pragma(self, pragma_stmt):
        p_claw = re.compile('^!\$claw\s*(loop\-fusion|loop\-interchange)')
        if p_claw.match(pragma_stmt.comment):
            return True
        else:
            return False

    # Return the type of claw pragma statement
    def __get_claw_directive(self, pragma_stmt):
        p_claw_fusion = re.compile('^!\$claw\s*loop\-fusion')
        p_claw_interchange = re.compile('^!\$claw\s*loop\-fusion')
        if(p_claw_fusion.match(pragma_stmt.comment)):
            return self.directives.LOOP_FUSION
        if(p_claw_interchange.match(pragma_stmt.comment)):
            return self.directives.LOOP_INTERCHANGE

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


def print_help():
   print 'parse_file.py -i <inputfile> -o <outputfile>'

def main(argv):
   inputfile = ''
   outputfile = ''
   analyze = False
   try:
      opts, args = getopt.getopt(argv,"hai:o:")
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
   if inputfile == '':
      print_help()
      sys.exit()
   else:
      claw = claw_parser(inputfile, outputfile)
      claw.translate()

if __name__ == "__main__":
   main(sys.argv[1:])
