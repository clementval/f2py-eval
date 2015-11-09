#!/usr/bin/env python

import sys, getopt
import fparser
from fparser import parsefortran
from fparser import api
from fparser import readfortran
from fparser import block_statements


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

def print_help():
   print 'parse_file.py -i <inputfile> -o <outputfile> [-a (analyze while parsing)]'

def print_block_info(block):
   print '####### BLOCK INFORMATION #######'
   print 'Root blocktype: ' + block.blocktype
   print '  name:   ' + block.blocktype
   print '  content:'
   print block.content
   for stmt in block.content:
       print_stmt_info(stmt)

def print_stmt_info(stmt):
   print '####### STMT INFORMATION #######'
   print stmt.item



def f2py_parse(inputfile, outputfile, analyze=False):


   reader = api.get_reader(inputfile, True, False, None, None)
   parser = parsefortran.FortranParser(reader, False)
   parser.parse()

   print_block_info(parser.block)



   if outputfile == '':
      #print parser.block
      outputfile = outputfile
   else:
      output = open(outputfile, 'w+')
      output_str = str(parser.block)
      output.write(output_str)
   if analyze == True:
      analyse_result = parser.analyze()

if __name__ == "__main__":
   main(sys.argv[1:])




#for stmt, depth in api.walk(tree):
#	print depth, stmt.item
