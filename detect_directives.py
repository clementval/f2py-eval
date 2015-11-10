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


class ClawInfo:
    """Small class to hold claw parsing information"""
    nbLoopFusion = 0
    nbLoopInterchange = 0

    def incrLoopFusion(self):
        self.nbLoopFusion += 1

    def incrLoopInterchange(self):
        self.nbLoopInterchange += 1


def validate_claw_pragma(pragma_stmt, info):
    p_claw = re.compile('^!\$claw\s*(loop\-fusion|loop\-interchange)')
    if p_claw.match(pragma_stmt.comment):
        p_fusion = re.compile('^!\$claw\s*loop\-fusion')
        p_interchange = re.compile('^!\$claw\s*loop\-fusion')
        if p_fusion.match(pragma_stmt.comment):
            info.incrLoopFusion()
        elif p_interchange.match(pragma_stmt.comment):
            info.incrLoopInterchange()
        return True
    else:
        return False

def find_pragma(comment_stmt, info):
    if(comment_stmt.comment != ''):
        p_pragma = re.compile('^!\$')
        p_claw = re.compile('^!\$claw')
        if p_claw.match(comment_stmt.comment):
            if validate_claw_pragma(comment_stmt, info):
                print 'CLAW pragma detected: ' + comment_stmt.comment
            else:
                print 'Invalid CLAW pragma: ' + comment_stmt.comment
        elif p_pragma.match(comment_stmt.comment):
            print 'Std pragma: ' + comment_stmt.comment

def print_info(info):
    print ''
    print '### Parsing info'
    print ' loop-fusion: ' + str(info.nbLoopFusion)
    print ' loop-interchange: ' + str(info.nbLoopInterchange)

def f2py_parse(inputfile):
    info = ClawInfo()
    reader = readfortran.FortranFileReader(inputfile)
    iterate = True
    while iterate:
        try:
            line = reader.next()
            if isinstance(line, readfortran.Comment):
                find_pragma(line, info)
        except StopIteration:
            iterate = False
    print_info(info)



if __name__ == "__main__":
   main(sys.argv[1:])
