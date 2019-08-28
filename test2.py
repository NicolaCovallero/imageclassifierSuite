
#usage python trainStandardDatasetLeNet.py --dataset MNIST
#usage python trainStandardDatasetLeNet.py  --dataset CIFAR10

#usage python trainStandardDatasetLeNet.py  --dataset CIFAR100

#usage python trainStandardDatasetLeNet.py  --dataset fashion_mnist

from sklearn.model_selection import train_test_split
import tensorflow as tf

from tensorflow.keras.datasets import mnist


from modelsRepo import modelsFactory
from modelEvaluator import ModelEvaluator
from keras.utils import np_utils
from keras.preprocessing.image import ImageDataGenerator
from  util import  plotUtil

from sklearn.preprocessing import LabelBinarizer
from sklearn.metrics import classification_report
import cv2
from keras.preprocessing.image import img_to_array

from keras.datasets import cifar10
from keras.datasets import fashion_mnist
from keras.datasets import cifar100
from keras.datasets import mnist

import argparse



import numpy as np

import pickle
import os
from imutils import build_montages


if __name__ == '__main__':


	# construct the argument parse and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("--dataset", required=True, help="name of the dataset")
	args = vars(ap.parse_args())
	dataset=args["dataset"]

	EPOCHS=30
	BS=32
	INIT_LR = 1e-3

	labels=[]
	print("[INFO] downloading {0}...".format(dataset))

	if(dataset=="MNIST"):
		(trainData, trainLabels), (testData, testLabels) = mnist.load_data()
		labels =  ['0','1','2','3','4','5','6','7','8','9']


	if(dataset=="CIFAR10"):
		(trainData, trainLabels), (testData, testLabels) = cifar10.load_data()
		labels =  ['airplane','automobile','bird','cat','deer','dog','frog','horse','ship','truck']


	if(dataset=="CIFAR100"):
		(trainData, trainLabels), (testData, testLabels) = cifar100.load_data()

	if(dataset=="fashion_mnist"):
		(trainData, trainLabels), (testData, testLabels) = fashion_mnist.load_data()

	#get original img width , hight and number of channels
	try:

		numPfSamples,imgWidth,imgHeight,numOfchannels=trainData.shape

	except:
		numPfSamples,imgWidth,imgHeight=trainData.shape
		numOfchannels=1


	print("[INFO] Original {} dataset of trainData shape {}".format(dataset,trainData.shape))
	print("[INFO] Original {} dataset of trainLabels shape {}".format(dataset,trainLabels.shape))
	print("[INFO] Original {} dataset of testData shape {}".format(dataset,testData.shape))
	print("[INFO] Original {} dataset of testLabels shape {}".format(dataset,testLabels.shape))


	trainX = trainData.reshape((trainData.shape[0], imgWidth,imgHeight,  numOfchannels))
	testX = testData.reshape((testData.shape[0], imgWidth,imgHeight, numOfchannels))
	images=[]
	for  i in range(9):
		image=trainData[i]
		if(numOfchannels==1):
			image = cv2.merge([image] * 3)
		images.append(image)
	
	montage = build_montages(images, (96, 96), (3, 3))
	cv2.imshow("Sample imaged from training datasert", montage[0])
	cv2.waitKey(0)

	trainX = trainX.astype("float32") / 255.0
	testX = testX.astype("float32") / 255.0


	# transform the training and testing labels into vectors in the
	# range [0, classes] -- this generates a vector for each label,
	# where the index of the label is set to `1` and all other entries
	# to `0`; in the case of MNIST, there are 10 class labels
	
	#trainY = np_utils.to_categorical(trainLabels, 10)
	#testY = np_utils.to_categorical(testLabels, 10)

	trainLabels=trainLabels.astype(str)
	testLabels=testLabels.astype(str)



	#lb.classes_  will be  the labels with the same order in one hot vector--->. label = lb.classes_[i]
	lb = LabelBinarizer()
	trainY = lb.fit_transform(trainLabels)
	testY = lb.fit_transform(testLabels)
	numOfOutputs=len(lb.classes_)





	model=modelsFactory.ModelCreator(numOfOutputs,imgWidth,imgHeight,numOfchannels,"LenetModel").model

	model.summary()
	opt = tf.keras.optimizers.Adam(lr=INIT_LR, decay=INIT_LR / EPOCHS)
	model.compile(loss="categorical_crossentropy", optimizer=opt, metrics=["accuracy"])


	# train the network
	print("[INFO] training network...")
	#model.fit(trainX, trainY, batch_size=128, epochs=20,verbose=1)

	aug = ImageDataGenerator()


	history = model.fit_generator(aug.flow(trainX, trainY, batch_size=BS),
	validation_data=(testX, testY), steps_per_epoch=len(trainX) // BS,
	epochs=EPOCHS, verbose=1)


	

	# serialize the label binarizer to disk
	fileNameToSaveLabels=dataset+"_labels.pkl"
	fileNameToSaveLabels=os.path.join("Results",fileNameToSaveLabels)
	f = open(fileNameToSaveLabels, "wb")
	f.write(pickle.dumps(lb.classes_))
	f.close()


	info1=plotUtil.plotAccuracyAndLossesonSameCurve(history,dataset+"_")
	info2=plotUtil.plotAccuracyAndLossesonSDifferentCurves(history,dataset+"_")


	#sklearn.metrics.classification_report(y_true, y_pred, labels=None, target_names=None, sample_weight=None, digits=2, output_dict=False)
	# evaluate the network
	print("[INFO] evaluating network...")
	predictions = model.predict(testX, batch_size=32)
	y_true=testY.argmax(axis=1)
	y_pred=predictions.argmax(axis=1)

	print(lb.classes_)
	print(type(lb.classes_))
	print(classification_report(y_true,y_pred, target_names=lb.classes_))

	


	fileToSaveModel=os.path.join("Results",dataset+"Lenet.keras2")
	model.save(fileToSaveModel)

	print("[INFO] Model saved to {}".format(fileToSaveModel))
	print("[INFO] Labels  saved to {}".format(fileNameToSaveLabels))
	print(info1)
	print(info2)





	imageIndex=0
	image = (testData[imageIndex] * 255).astype("uint8")
	imgDisplay=image.copy()

	# pre-process the image for classification
	image = image.astype("float") / 255.0
	image = img_to_array(image)
	image = np.expand_dims(image, axis=0)
	#print(image.shape) (1,28,28,1)

	predictions = model.predict(image, batch_size=32)
	print("predictions={}".format(predictions))

 
	# show the image and prediction

	 # merge the channels into one image
	if(numOfchannels==1):
		imgDisplay = cv2.merge([imgDisplay] * 3)
	#print(imgDisplay.shape)
 
	# resize the image from a 28 x 28 image to a 96 x 96 image so we
	# can better see it
	imgDisplay = cv2.resize(imgDisplay, (96, 96), interpolation=cv2.INTER_LINEAR)
	y_pred=predictions.argmax(axis=1)
	predictedLabel=labels[y_pred[0]]
	actualLabel=labels[np.argmax(testY[imageIndex])]

	cv2.putText(imgDisplay, str(predictedLabel), (5, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

	print("[INFO] Predicted: {}, Actual: {}".format(predictedLabel,actualLabel))
	cv2.imshow("Digit", imgDisplay)
	cv2.waitKey(0)

