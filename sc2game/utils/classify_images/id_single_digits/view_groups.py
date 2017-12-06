'''
Created on Apr 9, 2017

@author: akaiser
'''

import argparse
import pickle
from sklearn.externals import joblib
import cv2
from collections import defaultdict
import numpy as np

def view_groups(kmeans_file, names_file, images_path):
    names = pickle.load(open(names_file, "rb"))
    kmeans = joblib.load(kmeans_file)
    labels = kmeans.labels_
    max_label = max(labels)
    for label in xrange(0, max_label+1):
        index = 0
        imgs = []
        while index < len(labels):
            if labels[index] == label:
                img = cv2.imread(images_path + "/" + names[index], 0)
                imgs.append(img)
            index += 1
        display_multiple_images(label, imgs)


def display_multiple_images(label, images):
    """
    Display multiple iamges in one window, assumes all the images have the same
    height and weight
    """
    max_height = 1000
    padding = 3
    img_height, img_width = images[0].shape
    
    rows = max_height / (img_height + padding)
    if rows > len(images):
        rows = len(images)
    columns = ((len(images)-1) / rows) + 1
    
    height = (rows * img_height) + ((rows-1)*padding)
    width = (columns * img_width) + ((columns-1)*padding)
    
    canvas = np.zeros((height, width), dtype=np.uint8)
    img = images[0]
    x = 0
    y = 0
    for img in images:
        canvas[y:y+img.shape[0], x:x+img.shape[1]] = img
        y += img.shape[0] + 3
        if y > height:
            y = 0
            x += img.shape[1] + 3
    cv2.imshow(str(label), canvas)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def how_many(kmeans_file, names_file, images_path):
    kmeans = joblib.load(kmeans_file)
    labels = kmeans.labels_
    groups = defaultdict(int)
    for i in xrange(len(labels)):
        groups[labels[i]] += 1
    for l in groups:
        print(str(l) + ": " + str(groups[l]))
    

            
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Look at the different groups created")
    parser.add_argument("-k", "--kmeans_file", default="/Users/akaiser/Documents/workspace/data/kmeans.pkl")
    parser.add_argument("-o", "--names_file", default="/Users/akaiser/Documents/workspace/data/names.pkl")
    parser.add_argument("-i", "--images_path", default="/Users/akaiser/Documents/workspace/data/proleague_minerals_digits")
    args = parser.parse_args()
    view_groups(args.kmeans_file, args.names_file, args.images_path)
#     how_many(args.kmeans_file, args.names_file, args.images_path)