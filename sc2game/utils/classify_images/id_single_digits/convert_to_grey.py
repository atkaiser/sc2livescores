'''
Created on Apr 8, 2017

@author: akaiser
'''

import argparse
import os
from PIL import Image

def convert_to_grey(path):
    for image_path in os.listdir(path):
        im = Image.open(path + "/" + image_path)
        im.convert('L').save(path + "/" + image_path)
        
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Split proleague mineral images into just single digits")
    parser.add_argument("-p", "--path", default="/Users/akaiser/Documents/workspace/data/proleague_minerals_digits",
                        help="Folder with images to convert")
    args = parser.parse_args()
    convert_to_grey(args.path)