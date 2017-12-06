'''
Created on Apr 8, 2017

@author: akaiser

This script will do Kmeans learning on the hog features for an image.

It requires that the path given has black and white single digit images.
These can be obtained by running the split_images.py and convert_to_grey.py scripts
in this folder.

As output it will joblib.dump the classifier to the output file.
'''

import argparse
import os
from scipy import misc
from skimage.feature import hog
from sklearn.cluster import KMeans
import numpy as np
from sklearn.externals import joblib
import pickle

def learn(images_path, output_path):
    print("Generating features")
    names = []
    features = []
    for image_path in os.listdir(images_path):
        im_ar = misc.imread(images_path + "/" + image_path)
        feature = hog(im_ar, pixels_per_cell=(2,2), cells_per_block=(2,2))
        names.append(image_path)
        features.append(feature)
    X = np.zeros((len(features), len(features[0])))
    for i in range(len(features)):
        X[i] = features[i]
    kmean = KMeans(n_clusters=11)
    print("running kmeans")
    kmean.fit(X)
    joblib.dump(kmean, output_path + "/kmeans.pkl")
    pickle.dump(names, open(output_path + "/names.pkl", "wb"))
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Split proleague mineral images into just single digits")
    parser.add_argument("-p", "--path", default="/Users/akaiser/Documents/workspace/data/proleague_minerals_digits",
                        help="Folder with images to learn on")
    parser.add_argument("-o", "--output_path", default="/Users/akaiser/Documents/workspace/data")
    args = parser.parse_args()
    learn(args.path, args.output_path)