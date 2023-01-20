import datetime
import math
import sys

import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
image_width = 300
image_height = 300


def resize_and_show(image):
    h, w = image.shape[:2]
    if h < w:
        img = cv2.resize(image, (image_width, math.floor(h / (w / image_width))))
    else:
        img = cv2.resize(image, (math.floor(w / (h / image_height)), image_height))

    cv2.imshow("Hand In Resize", img)


def crop_and_save(image: np.ndarray, hand_landmarks: mp_hands.HandLandmark, folder: str, picture_name: str) -> None:
    min_x, min_y, max_x, max_y = 1.0, 1.0, 0.0, 0.0
    for landmark in hand_landmarks.landmark:
        min_x, min_y = min(landmark.x, min_x), min(landmark.y, min_y)
        max_x, max_y = max(landmark.x, max_x), max(landmark.y, max_y)
    offset_x, offset_y = 0.05, 0.05
    frame_height, frame_width = image.shape[:2]
    min_x, min_y = int(min_x * frame_width - offset_x * frame_width), int(
        min_y * frame_height - offset_y * frame_height)
    max_x, max_y = int(max_x * frame_width + offset_x * frame_width), int(
        max_y * frame_height + offset_y * frame_height)
    hand_image = image[min_y:max_y, min_x:max_x]

    resize_and_show(cv2.flip(hand_image, 1))
    cv2.imshow("Hand After Resize", hand_image)
    cv2.imwrite(f"{folder}/{user_input}/{picture_name}.jpg", hand_image)


folder = r"C:\Users\seppe\PycharmProjects\st-2223-1-d-ee-SeppeWillems13\src\project\base\hand_recognition" \
         r"\new_image_data"
if len(sys.argv) != 2:
    print("Please provide a valid input for rock, paper or scissors")
    sys.exit()
user_input = sys.argv[1]

cap = cv2.VideoCapture(0)
with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
    count = 0
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                current_hand_landmarks = hand_landmarks
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
        cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
        key = cv2.waitKey(5) & 0xFF
        if key == ord('s'):
            count += 1
            picture_name = f"{user_input}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{count}"
            print(f"Saving image {count} of type {user_input}")
            crop_and_save(image, current_hand_landmarks, folder, picture_name)
        elif key == 27:
            break
    cap.release()
    cv2.destroyAllWindows()
