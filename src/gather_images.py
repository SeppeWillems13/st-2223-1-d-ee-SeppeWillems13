import cv2
import os
import sys
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import math
import time


def collect_images(label_name, num_samples):
    # Set up the save path and create the directory if it doesn't exist
    save_path = os.path.join('image_data', label_name)
    os.makedirs(save_path, exist_ok=True)

    offset = 20
    imgSize = 300

    # Initialize the camera and set up the video capture
    cap = cv2.VideoCapture(0)
    detector = HandDetector(maxHands=1)

    if not cap.isOpened():
        print("Error opening video stream or file")
        return

    start = False
    count = 0

    while True:
        if count == num_samples:
            break

        success, img = cap.read()
        hands, img = detector.findHands(img)
        if hands:
            hand = hands[0]
            x, y, w, h = hand['bbox']

            imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
            imgCrop = img[y - offset:y + h + offset, x - offset:x + w + offset]

            imgCropShape = imgCrop.shape

            aspectRatio = h / w

            if aspectRatio > 1:
                k = imgSize / h
                wCal = math.ceil(k * w)
                imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                imgResizeShape = imgResize.shape
                wGap = math.ceil((imgSize - wCal) / 2)
                imgWhite[:, wGap:wCal + wGap] = imgResize

            else:
                k = imgSize / w
                hCal = math.ceil(k * h)
                imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                imgResizeShape = imgResize.shape
                hGap = math.ceil((imgSize - hCal) / 2)
                imgWhite[hGap:hCal + hGap, :] = imgResize

            cv2.imshow("ImageCrop", imgCrop)
            cv2.imshow("ImageWhite", imgWhite)

        if start:
            count += 1
            cv2.imwrite(f'{save_path}/Image_{time.time()}.jpg', imgWhite)
            print(count)

        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        if key == ord("s"):
            start = not start

    # Release the camera and destroy the window
    cap.release()
    cv2.destroyAllWindows()
    print(f"\n{count} image(s) saved to {save_path}")


def main():
    # Parse the command-line arguments
    try:
        label_name = sys.argv[1]
        num_samples = int(sys.argv[2])
    except:
        print("Error: missing or invalid arguments")
        print("Usage: python collect_images.py LABEL_NAME NUM_SAMPLES")
        return

    # Check that the label name is valid
    if label_name not in ['rock', 'paper', 'scissors']:
        print("Error: label name must be 'rock', 'paper', or 'scissors'")
        return

    # Check that the number of samples is within a valid range
    if num_samples < 1 or num_samples > 1000:
        print("Error: number of samples must be between 1 and 1000")
        return

    # Collect the images
    collect_images(label_name, num_samples)


if __name__ == '__main__':
    main()
