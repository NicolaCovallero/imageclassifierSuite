# USAGE


#python test_network_multiClassifier.py  --model Results/SportsClassification_Classifier.keras2 --image TestImages/test_images_sports/tennis.jpeg --labelPKL Results/SportsClassification_labels.pkl --width 224 --height 224

# import the necessary packages

import tensorflow  as tf

from tensorflow.keras.preprocessing.image import img_to_array
import numpy as np
import argparse
import imutils
import cv2
import pickle






# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-m", "--model", required=True,
	help="path to trained model model")
ap.add_argument("-i", "--image", required=True,
	help="path to input image")
ap.add_argument("-lbpkl", "--labelPKL", required=True,
	help="path to label list as pickle file")
ap.add_argument("--width",  required=True,help="image width")
ap.add_argument("--height",  required=True,help="image height")

args = vars(ap.parse_args())

width=int(args["width"])
height=int(args["height"])

labels = pickle.loads(open(args["labelPKL"], "rb").read())

# load the image
image = cv2.imread(args["image"])
orig = image.copy()

# pre-process the image for classification
image = cv2.resize(image, (width,height))
image = image.astype("float") / 255.0
image = img_to_array(image)
image = np.expand_dims(image, axis=0)

# load the trained convolutional neural network
print("[INFO] loading network. from {}".format(args["model"]))
#model = tf.keras.models.load_model(args["model"])
model = tf.keras.models.load_model(args["model"])


print("[INFO] Model loaded succesfully from {}".format(args["model"]))

# classify the input image


prediction= (model.predict(image)[0])[0] #probabilty
y_pred=prediction.argmax(axis=1)

# build the label
label = labels[y_pred]
proba = prediction if (prediction > 0.5) else (1-prediction)


label = "{}: {:.2f}%".format(label, proba * 100)

# draw the label on the image
output = imutils.resize(orig, width=400)
cv2.putText(output, label, (10, 25),  cv2.FONT_HERSHEY_SIMPLEX,
	0.7, (0, 255, 0), 2)

# show the output image
cv2.imshow("Output", output)
cv2.waitKey(0)