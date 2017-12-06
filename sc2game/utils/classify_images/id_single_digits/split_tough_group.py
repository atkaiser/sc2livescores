'''
Created on Apr 17, 2017

@author: akaiser
'''

import argparse
import pickle
from sklearn.externals import joblib

from scipy import misc
from skimage.feature import hog
from sklearn.cluster import KMeans
import numpy as np

def get_images(kmeans_file, names_file):
    names = pickle.load(open(names_file, "rb"))
    kmeans = joblib.load(kmeans_file)
    labels = kmeans.labels_
    label = 8
    index = 0
    imgs = []
    while index < len(labels):
        if labels[index] == label:
            imgs.append(names[index])
        index += 1
    return imgs

def learn(names, images_path, output_path):
    print("Generating features")
    features = []
    for image_path in names:
        im_ar = misc.imread(images_path + "/" + image_path)
        feature = hog(im_ar, pixels_per_cell=(2,2), cells_per_block=(2,2))
        features.append(feature)
    X = np.zeros((len(features), len(features[0])))
    for i in range(len(features)):
        X[i] = features[i]
    kmean = KMeans(n_clusters=3)
    print("running kmeans")
    kmean.fit(X)
    joblib.dump(kmean, output_path + "/kmeans.pkl")
    pickle.dump(names, open(output_path + "/names.pkl", "wb"))
    return



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Look at the different groups created")
    parser.add_argument("-k", "--kmeans_file", default="/Users/akaiser/Documents/workspace/data/kmeans.pkl")
    parser.add_argument("-o", "--names_file", default="/Users/akaiser/Documents/workspace/data/names.pkl")
    parser.add_argument("-i", "--images_path", default="/Users/akaiser/Documents/workspace/data/proleague_minerals_digits")
    args = parser.parse_args()
    images = get_images(args.kmeans_file, args.names_file)
    learn(images, args.images_path, "/tmp")