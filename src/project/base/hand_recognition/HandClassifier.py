import os

import numpy as np
from PIL import Image, ImageOps
from keras.models import load_model


class HandClassifier:
    def __init__(self, dark_mode=False):
        # Get the absolute paths to the model and labels files
        if dark_mode:
            # TODO scissors hand palm facing webcam 99% hand THIS IS WRONG
            model_path = os.path.abspath('keras/keras_dark_model.h5')
        else:
            model_path = os.path.abspath('keras/keras_model_second.h5')

        labels_path = os.path.abspath('keras/labels.txt')

        # Load the model and labels
        self.model = load_model(model_path, compile=False)
        with open(labels_path, 'r') as f:
            self.labels = f.read().splitlines()

    def classify(self, image):
        # Create the array of the right shape to feed into the keras model
        # The 'length' or number of images you can put into the array is
        # determined by the first position in the shape tuple, in this case 1.
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

        image = Image.fromarray(image)

        # resize the image to a 224x224 with the same strategy as in TM2:
        # resizing the image to be at least 224x224 and then cropping from the center
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

        # turn the image into a numpy array
        image_array = np.asarray(image)

        # Normalize the image
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

        # Load the image into the array
        data[0] = normalized_image_array

        # run the inference
        prediction = self.model.predict(data)
        index = np.argmax(prediction)
        class_name = self.labels[index]
        confidence_score = prediction[0][index]

        return class_name, confidence_score
