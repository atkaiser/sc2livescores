'''
Created on Jul 16, 2014

@author: akaiser
'''

import sys

sys.path.append('/Users/akaiser/Documents/workspace/sc2livescores')

from sc2livescores import sets
from PIL import Image

def convert(val):
    if val > 125:
        return 256
    return 0

im = Image.open('/Users/akaiser/Documents/workspace/sc2livescores/sc2game/temps/basetradetv/l_gas.jpeg')
img = im.convert('L')
cim = img.point(convert)
cim.show()
cim.save('/Users/akaiser/Desktop/temps/test.jpeg')
