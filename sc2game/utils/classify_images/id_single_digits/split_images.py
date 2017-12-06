'''
Created on Apr 7, 2017

@author: akaiser
'''

import argparse
import os
from PIL import Image

def split_images(in_dir, out_dir):
    for image_path in os.listdir(in_dir):
        im = Image.open(in_dir + "/" + image_path)
        image_path = image_path.split(".")[0]
        im.crop((3, 1, 13, 13)).save(out_dir + "/" + image_path + "-0.jpeg")
        im.crop((12, 1, 22, 13)).save(out_dir + "/" + image_path + "-1.jpeg")
        im.crop((21, 1, 31, 13)).save(out_dir + "/" + image_path + "-2.jpeg")
        im.crop((30, 1, 40, 13)).save(out_dir + "/" + image_path + "-3.jpeg")
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Split proleague mineral images into just single digits")
    parser.add_argument("-in", "--in_dir", default="/Users/akaiser/Documents/workspace/data/sc2_pics/proleague/minerals",
                        help="Where the current images are")
    parser.add_argument("-out", "--out_dir", default="/Users/akaiser/Documents/workspace/data/proleague_minerals_digits")
    args = parser.parse_args()
    split_images(args.in_dir, args.out_dir)