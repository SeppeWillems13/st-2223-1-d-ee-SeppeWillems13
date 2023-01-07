import cv2
import numpy as np
from PIL import Image, ImageOps
from keras.models import load_model
import os


class HandClassifier:
    def __init__(self):
        model_path = 'keras/keras_model.h5'
        labels_path = "keras/labels.txt"
        abs_model_path = os.path.abspath(model_path)
        abs_label_path = os.path.abspath(labels_path)

        self.model = load_model(abs_model_path, compile=False)
        with open(abs_label_path, 'r') as f:
            self.labels = f.read().splitlines()

    def classify(self, image):
        # Resize the image to a 224x224 with the same strategy as in TM2:
        # resizing the image to be at least 224x224 and then cropping from the center
        image = Image.fromarray(image)
        image.convert('RGB')
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
        # Turn the image into a NumPy array
        image_array = np.asarray(image)
        # Normalize the image
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
        # Add the image to the data array
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        data[0] = normalized_image_array
        # Use the model to make a prediction
        prediction = self.model.predict(data)
        # Get the index of the most likely class
        index = np.argmax(prediction[0])

        # run the inference
        prediction = self.model.predict(data)
        index = np.argmax(prediction)
        class_name = self.labels[index]
        confidence_score = prediction[0][index]

        return class_name, confidence_score
