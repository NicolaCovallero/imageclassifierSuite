# USAGE
# python test_network_binary.py --model Results/Santa_binaryClassifier.keras2  --image TestImages/test_images_Santa_and_noSanta/santa_01.png --labelPKL Results/Santa_labels.pkl --width  28 --height 28

#python test_network_binary.py --model Results/cats_dogs_binaryClassifier.keras2 --image TestImages/test_images_cats_and_dogs/cats/cat_44.jpeg  --width  150 --height  150 --labelPKL Results/cats_and_dogs_labels.pkl 

#python test_network_binary.py --model Results/cats_dogs_binaryClassifier.keras2 --image TestImages/test_images_cats_and_dogs/dogs/dog_23.jpeg --labelPKL Results/cats_and_dogs_labels.pkl --width  150 --height  150

# import the necessary packages
from keras.preprocessing.image import img_to_array
from keras.models import load_model
import numpy as np
import argparse
import imutils
import cv2
import tensorflow as tf 
import pickle
import os






# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-m", "--model", required=True,
	help="path to trained model model")
ap.add_argument("-i", "--image", required=True,
	help="path to input image")
ap.add_argument("-lbpkl", "--labelPKL", required=True,
	help="path to label list as picklw file")

ap.add_argument("--width", required=True,
	help="path to label list as picklw file")
ap.add_argument("--height", required=True,
	help="path to label list as picklw file")
args = vars(ap.parse_args())

width=int(args["width"])
height=int(args["height"])


labels = pickle.loads(open(args["labelPKL"], "rb").read())
print(labels) #for example {'cats': 0, 'dogs': 1}


# load the image
image = cv2.imread(args["image"])
orig = image.copy()

# pre-process the image for classification
image = cv2.resize(image, (width,height))
image = image.astype("float") / 255.0
image = img_to_array(image)
image = np.expand_dims(image, axis=0)

# load the trained convolutional neural network
print("[INFO] loading network...")
model = tf.keras.models.load_model(args["model"])
print("[INFO] Model loaded succesfully from {}".format(args["model"]))

# classify the input image


prediction= (model.predict(image)[0])[0] #probabilty


tmpLabels=[None,None]

# build the label
for key,value in labels.items():   #{'cats': 0, 'dogs': 1}
	tmpLabels[value]= key

labels=tmpLabels

label = labels[1] if prediction > 0.5 else labels[0] 
proba = prediction if (prediction > 0.5) else (1-prediction)


label = "{}: {:.2f}%".format(label, proba * 100)

# draw the label on the image
output = imutils.resize(orig, width=400)
cv2.putText(output, label, (10, 25),  cv2.FONT_HERSHEY_SIMPLEX,0.7, (0, 255, 0), 2)

# show the output image
cv2.imshow("Output", output)
fileNameToSaveImageWithPrediction="prediction_"+os.path.basename(args["image"])
fileNameToSaveImageWithPrediction=os.path.join("Results",fileNameToSaveImageWithPrediction)
cv2.imwrite(fileNameToSaveImageWithPrediction,output)
print("[INFO] Image with prediction saved to  {}".format(fileNameToSaveImageWithPrediction))
cv2.waitKey(0)