'''
Created on May 26, 2016

@author: akaiser
'''

import os
from PIL import Image
from scipy import misc
from skimage.feature import hog
from sklearn.cluster import KMeans
import numpy as np
from sklearn.externals import joblib

digits_dir = "/Users/akaiser/Desktop/pics/digits"

def split_images(path):
    for image_path in os.listdir(path):
        im = Image.open(path + "/" + image_path)
        image_path = image_path.split(".")[0]
        im.crop((3, 1, 13, 13)).save(digits_dir + "/" + image_path + "-0.jpeg")
        im.crop((12, 1, 22, 13)).save(digits_dir + "/" + image_path + "-1.jpeg")
        im.crop((21, 1, 31, 13)).save(digits_dir + "/" + image_path + "-2.jpeg")
        im.crop((30, 1, 40, 13)).save(digits_dir + "/" + image_path + "-3.jpeg")


def convert_to_grey(path):
    for image_path in os.listdir(path):
        im = Image.open(path + "/" + image_path)
        im.convert('L').save(path + "/" + image_path)
        
def learn():
    names = []
    features = []
    for image_path in os.listdir(digits_dir):
        im_ar = misc.imread(digits_dir + "/" + image_path)
        feature = hog(im_ar, pixels_per_cell=(2,2), cells_per_block=(2,2))
        names.append(image_path)
        features.append(feature)
    X = np.zeros((len(features), len(features[0])))
    for i in range(len(features)):
        X[i] = features[i]
    kmean = KMeans(n_clusters=11)
    print("running kmeans")
    kmean.fit(X)
    joblib.dump(kmean, "/tmp/k.pkl")
    return names
        
        
def results():
    names = []
    for image_path in os.listdir(digits_dir):
        names.append(image_path)
    kmean = joblib.load("/tmp/k.pkl")
    labels = kmean.labels_
    for i in range(100):
        print(names[i] + ":\t" + str(labels[i]))
    

if __name__ == '__main__':
#     convert_to_grey(digits_dir)
#     split_images("/Users/akaiser/Desktop/pics/proleague/minerals")
#     learn()
    results()