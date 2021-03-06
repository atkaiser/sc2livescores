from glob import glob
import mahotas
import mahotas.features
import milk
from jug import TaskGenerator

"""
Notes: April 7th, 2017
I've never actually used this script and I don't know if it even works
I also haven't installed the libraries before.  From what I remember it is 
supposed to do something about classifying images
"""

@TaskGenerator
def features_for(imname):
    img = mahotas.imread(imname)
    return mahotas.features.haralick(img).mean(0)

@TaskGenerator
def learn_model(features, labels):
    learner = milk.defaultclassifier()
    return learner.train(features, labels)

@TaskGenerator
def classify(model, features):
     return model.apply(features)

positives = glob('positives/*.jpg')
negatives = glob('negatives/*.jpg')
unlabeled = glob('unlabeled/*.jpg')

features = map(features_for, negatives + positives)
labels = [0] * len(negatives) + [1] * len(positives)

model = learn_model(features, labels)

labeled = [classify(model, features_for(u)) for u in unlabeled]