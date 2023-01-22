import datetime
import math
import os
import sys
import cv2
import numpy as np

image_width = 300
image_height = 300


def resize_and_show(image,picture_name):
    h, w = image.shape[:2]
    if h < w:
        img = cv2.resize(image, (image_width, math.floor(h / (w / image_width))))
    else:
        img = cv2.resize(image, (math.floor(w / (h / image_height)), image_height))

    cv2.imshow("Hand After Resize", img)
    #check if folder exists
    if not os.path.exists(f"{folder}/{user_input}"):
        os.makedirs(f"{folder}/{user_input}")

    cv2.imwrite(f"{folder}/{user_input}/{picture_name}.jpg", img)
    print(f"Saved image {picture_name} of type {user_input} in {folder}/{user_input}")


folder = r"C:\Users\seppe\PycharmProjects\st-2223-1-d-ee-SeppeWillems13\src\project\base\hand_recognition" \
         r"\dark_image_data"
if len(sys.argv) != 2:
    print("Please provide a valid input for rock, paper or scissors")
    sys.exit()
user_input = sys.argv[1]

cap = cv2.VideoCapture(0)
count = 0
while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
    key = cv2.waitKey(5) & 0xFF
    if key == ord('s'):
        count += 1
        picture_name = f"{user_input}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{count}"
        print(f"Saving image {count} of type {user_input}")
        resize_and_show(image,picture_name)
    elif key == 27:
        break
cap.release()
cv2.destroyAllWindows()
