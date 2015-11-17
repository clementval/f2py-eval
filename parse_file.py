#!/usr/bin/env python

import sys, getopt
import fparser
from fparser import parsefortran
from fparser import api
from fparser import readfortran
from fparser import block_statements


def print_block_info(block):
   print '####### BLOCK INFORMATION #######'
   print 'Root blocktype: ' + block.blocktype
   print '  name:   ' + block.blocktype
   print '  content:'
   print block.content

def process_main_block(block):
    for stmt in block.content:
        process_stmt(stmt)

def process_stmt(stmt):
   process_item(stmt)
   if hasattr(stmt, 'content'):
       for s in stmt.content:
           process_stmt(s)


# Possible item types: Line, SyntaxErrorLine, Comment, MultiLine,
# SyntaxErrorMultiLine
def process_item(stmt):
    if hasattr(stmt, 'item'):
        if isinstance(stmt.item, readfortran.Comment):
            process_comment(stmt.item)
        elif isinstance(stmt.item, readfortran.Line):
            process_line(stmt.item)

def process_comment(comment):
    if not isinstance(comment, readfortran.Comment):
        return
    print comment.comment

def process_line(line):
    if not isinstance(line, readfortran.Line):
        return
    print line.line


def f2py_parse(inputfile, outputfile, analyze=False):
   reader = api.get_reader(inputfile, True, False, None, None)
   parser = parsefortran.FortranParser(reader, False)
   parser.parse()

   #print_block_info(parser.block)
   process_main_block(parser.block)

   if outputfile == '':
      #print parser.block
      outputfile = outputfile
   else:
      output = open(outputfile, 'w+')
      output_str = str(parser.block)
      output.write(output_str)
   if analyze == True:
      analyse_result = parser.analyze()

def print_help():
   print 'parse_file.py -i <inputfile> -o <outputfile> [-a (analyze while parsing)]'

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
      elif opt in ("-a"):
         analyze = True
   if inputfile == '':
      print_help()
      sys.exit()
   else:
      f2py_parse(inputfile, outputfile, analyze)

if __name__ == "__main__":
   main(sys.argv[1:])
