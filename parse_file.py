#!/usr/bin/env python

import sys, getopt
import fparser
from fparser import parsefortran
from fparser import api
from fparser import readfortran
from fparser import block_statements


class claw_parser:
    def __init__(self, infile, outfile, keep_pragma=True):
        self.infile = infile
        self.outfile = outfile
        self.keep_pragma = keep_pragma

    def __parse(self):
        reader = api.get_reader(self.infile, True, False, None, None)
        parser = parsefortran.FortranParser(reader, False)
        parser.parse()
        return parser.block

    def translate(self):
        main_block = self.__parse()
        self.__process_main_block(main_block)


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
        print comment.comment

    def __process_line(self, line):
        if not isinstance(line, readfortran.Line):
            return
        print line.line

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
