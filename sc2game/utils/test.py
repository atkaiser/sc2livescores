'''
Created on Jul 16, 2014

@author: akaiser
'''

import sys

with open(sys.argv[1]) as f:
    for line in f:
        l = line.rstrip()
        if "=" in l:
            num = l.index("=")
            print l[0:num] + "_1080" + l[num:]
        else:
            print l

