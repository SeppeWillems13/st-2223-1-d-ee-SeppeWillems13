import cv2
from cvzone.HandTrackingModule import HandDetector
import math

from hand_recognition.HandClassifier import HandClassifier
from hand_recognition.ImageProcessor import ImageProcessor

cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1)
classifier = HandClassifier()

offset = 20
img_size = 300

labels = ["paper", "rock", "scissors"]

while True:
    processor = ImageProcessor(detector, img_size, offset)
    success, img = cap.read()
    hands = detector.findHands(img, draw=False)

    if hands:
        hand = hands[0]
        x, y, w, h = hand['bbox']
        img_white, img_resize = processor.process(img, hand)
        # Calculate the aspect ratio of the cropped image
        aspect_ratio = h / w
        # If the aspect ratio is greater than 1, add the resized image to the white image
        # with a gap at the top and bottom to center the image
        if aspect_ratio > 1:
            h_gap = math.ceil((img_size - img_resize.shape[0]) / 2)
            img_white[h_gap:h_gap + img_resize.shape[0], :] = img_resize

        # If the aspect ratio is less than or equal to 1, add the resized image to the white image
        # with a gap at the left and right to center the image
        else:
            w_gap = math.ceil((img_size - img_resize.shape[1]) / 2)
            img_white[:, w_gap:w_gap + img_resize.shape[1]] = img_resize

        # improve with probability!!!!
        prediction, confidence_score = classifier.classify(img_white)

        cv2.rectangle(img, (x - offset, y - offset - 50),
                      (x - offset + 90, y - offset - 50 + 50), (255, 0, 255), cv2.FILLED)
        cv2.putText(img, prediction, (x, y - 26), cv2.FONT_HERSHEY_COMPLEX, 1.7, (255, 255, 255), 2)
        cv2.rectangle(img, (x - offset, y - offset),
                      (x + w + offset, y + h + offset), (255, 0, 255), 4)

        cv2.imshow("ImageWhite", img_white)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
