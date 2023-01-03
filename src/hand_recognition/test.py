import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import numpy as np
import math

cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1)
classifier = Classifier("jupityer/model/keras_model.h5", "jupityer/model/labels.txt")

offset = 20
img_size = 300

labels = ["paper", "rock", "scissors"]

while True:
    success, img = cap.read()
    imgOutput = img.copy()
    hands = detector.findHands(img, draw=False)
    if hands:
        hand = hands[0]

        # Crop the image based on the bounding box of the detected hand
        x, y, w, h = hand['bbox']
        img_crop = img[y - offset:y + h + offset, x - offset:x + w + offset]

        # Normalize the pixel values to the range [0, 1]
        img_crop = np.interp(img_crop, (img_crop.min(), img_crop.max()), (0, 1))

        # Convert the image data to depth 8 bits per pixel
        img_crop = cv2.normalize(img_crop, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

        # Apply median filtering to the image to remove noise
        img_crop = cv2.medianBlur(img_crop, ksize=5)

        # Convert the image to grayscale
        img_crop = cv2.cvtColor(img_crop, cv2.COLOR_BGR2GRAY)

        # Resize the image to 300x300
        img_crop = cv2.resize(img_crop, (img_size, img_size))

        # Add a third dimension to the resized image to match the shape of the white image
        img_resize = np.expand_dims(img_crop, axis=2)

        # Create an empty white image of size 300x300
        img_white = np.ones((img_size, img_size, 3), np.uint8) * 255

        # Calculate the aspect ratio of the cropped image
        aspect_ratio = h / w

        # If the aspect ratio is greater than 1, add the resized image to the white image
        # with a gap at the top and bottom to center the image
        if aspect_ratio > 1:
            h_gap = math.ceil((img_size - img_resize.shape[0]) / 2)
            img_white[h_gap:h_gap + img_resize.shape[0], :] = img_resize
            prediction, index = classifier.getPrediction(img_white, draw=False)
            print(prediction, index)

        # If the aspect ratio is less than or equal to 1, add the resized image to the white image
        # with a gap at the left and right to center the image
        else:
            w_gap = math.ceil((img_size - img_resize.shape[1]) / 2)
            img_white[:, w_gap:w_gap + img_resize.shape[1]] = img_resize
            prediction, index = classifier.getPrediction(img_white, draw=False)
            print(prediction, index)

        cv2.rectangle(imgOutput, (x - offset, y - offset - 50),
                      (x - offset + 90, y - offset - 50 + 50), (255, 0, 255), cv2.FILLED)
        cv2.putText(imgOutput, labels[index], (x, y - 26), cv2.FONT_HERSHEY_COMPLEX, 1.7, (255, 255, 255), 2)
        cv2.rectangle(imgOutput, (x - offset, y - offset),
                      (x + w + offset, y + h + offset), (255, 0, 255), 4)

        cv2.imshow("ImageCrop", img_crop)
        cv2.imshow("ImageWhite", img_white)

    cv2.imshow("Image", imgOutput)
    cv2.waitKey(1)
