#! /usr/bin/env python

import fparser
from fparser import api

source_str = '''
        subroutine foo
          integer i, r
          do i=1,100
            r = r + i
          end do
        end
        '''
tree = api.parse(source_str)
for stmt, depth in api.walk(tree):
	print depth, stmt.item

