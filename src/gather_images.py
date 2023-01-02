"""Import all dependencies."""
import cv2
import os
import sys
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import math
import time


def collect_images(label_name, num_samples):
    """Get num_samples of type label_name with hand recognition and save them in their respected folder"""
    # Set up the save path and create the directory if it doesn't exist
    save_path = os.path.join('image_data', label_name)
    os.makedirs(save_path, exist_ok=True)

    offset = 20
    img_size = 300

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
        hands = detector.findHands(img, draw=False)
        if hands:
            hand = hands[0]
            x, y, w, h = hand['bbox']

            img_white = np.ones((img_size, img_size, 3), np.uint8) * 255
            img_crop = img[y - offset:y + h + offset, x - offset:x + w + offset]

            aspect_ratio = h / w

            if aspect_ratio > 1:
                k = img_size / h
                w_cal = math.ceil(k * w)
                img_resize = cv2.resize(img_crop, (w_cal, img_size))
                w_gap = math.ceil((img_size - w_cal) / 2)
                img_white[:, w_gap:w_cal + w_gap] = img_resize

            else:
                k = img_size / w
                h_cal = math.ceil(k * h)
                img_resize = cv2.resize(img_crop, (img_size, h_cal))
                h_gap = math.ceil((img_size - h_cal) / 2)
                img_white[h_gap:h_cal + h_gap, :] = img_resize

            cv2.imshow("ImageCrop", img_crop)
            cv2.imshow("ImageWhite", img_white)

            if start:
                count += 1
                cv2.imwrite(f'{save_path}/Image_{time.time()}.jpg', img_white)
                print(count)

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, "Collecting {}/{} of type {}".format(count, num_samples, label_name),
                    (5, 50), font, 0.7, (0, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        if key == ord("s"):
            start = not start
        if key == ord('q'):
            break
    # Release the camera and destroy the window
    cap.release()
    cv2.destroyAllWindows()
    print(f"\n{count} image(s) saved to {save_path}")


def main():
    """Main method checks if the args are between 1 and 1000 and of type rock,paper,scissor"""
    # noinspection PyBroadException
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
