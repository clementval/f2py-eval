#!/usr/bin/env python

import sys, getopt
import fparser
from fparser import readfortran
import re

def main(argv):
   inputfile = ''
   try:
      opts, args = getopt.getopt(argv,"i:")
   except getopt.GetoptError:
      print_help()
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print_help()
         sys.exit()
      elif opt == "-i":
         inputfile = arg
   if inputfile == '':
      print_help()
      sys.exit()
   else:
      f2py_parse(inputfile)

def print_help():
   print 'detect_directives.py -i <inputfile>'

def find_pragma(comment_stmt):
    if(comment_stmt.comment != ''):
        p_pragma = re.compile('^!\$')
        p_claw = re.compile('^!\$claw\s*[loop\-fusion|loop\-interchange]')
        if p_claw.match(comment_stmt.comment):
            print 'CLAW pragma detected: ' + comment_stmt.comment
        elif p_pragma.match(comment_stmt.comment):
            print 'Std pragma: ' + comment_stmt.comment


def f2py_parse(inputfile):
   reader = readfortran.FortranFileReader(inputfile)

   iterate = True
   while iterate:
       try:
           line = reader.next()
           if isinstance(line, readfortran.Comment):
               find_pragma(line)
       except StopIteration:
           iterate = False


if __name__ == "__main__":
   main(sys.argv[1:])
