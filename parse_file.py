#!/usr/bin/env python

import sys, getopt, re
import fparser
from fparser import parsefortran
from fparser import api
from fparser import readfortran
from fparser import block_statements

def enum(**enums):
    return type('Enum', (), enums)

class claw_parser:
    def __init__(self, infile, outfile, keep_pragma=True):
        self.infile = infile
        self.outfile = outfile
        self.keep_pragma = keep_pragma
        self.directives = enum(LOOP_FUSION=1, LOOP_INTERCHANGE=2)
        self.__outputBuffer = ''

    def __parse(self):
        reader = api.get_reader(self.infile, True, False, None, None)
        parser = parsefortran.FortranParser(reader, False)
        parser.parse()
        return parser.block

    def translate(self):
        main_block = self.__parse()
        self.__process_main_block(main_block)
        if self.outfile == '':
            print self.__outputBuffer

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
            for s in stmt.content:
                self.__process_stmt(s)


    # Possible item types: Line, SyntaxErrorLine, Comment, MultiLine,
    # SyntaxErrorMultiLine
    def __process_item(self, stmt):
        if hasattr(stmt, 'item'):
            if isinstance(stmt.item, readfortran.Comment):
                self.__process_comment(stmt.item)
            elif isinstance(stmt.item, readfortran.Line):
                self.__process_line(stmt.item)

    def __process_comment(self, comment):
        if not isinstance(comment, readfortran.Comment):
            return
        if self.__is_pragma(comment):
            if self.__is_claw_pragma(comment):
                # process claw pragma
                if self.__is_valid_claw_pragma(comment):
                    claw_dir = self.__get_claw_directive(comment)
                    if(claw_dir == self.directives.LOOP_FUSION):
                        print '! LOOP_FUSION'
                    elif(claw_dir == self.directives.LOOP_INTERCHANGE):
                        print '! LOOP_INTERCHANGE'

                    # just output pragma if option is to keep them
                    if self.keep_pragma:
                        self.__add_to_buffer(comment.comment)
                else:
                    # Error
                    self.__exit_error(directive = comment.comment, linenum = 10)
            else: # other pragma are kept in the output
                self.__add_to_buffer(comment.comment)
        else:
            self.__add_to_buffer(comment.comment)

    def __process_line(self, line):
        if not isinstance(line, readfortran.Line):
            return
        self.__add_to_buffer(line.line)

    def __add_to_buffer(self, line):
        self.__outputBuffer += line
        self.__outputBuffer += '\n'

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
