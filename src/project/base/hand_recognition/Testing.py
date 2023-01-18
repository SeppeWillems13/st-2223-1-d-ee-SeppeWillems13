import math

import cv2
import mediapipe as mp
import numpy as np
from keras.models import load_model

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

model_path = r'C:\Users\seppe\PycharmProjects\st-2223-1-d-ee-SeppeWillems13\src\project\keras\keras_model_second.h5'
labels_path = r'C:\Users\seppe\PycharmProjects\st-2223-1-d-ee-SeppeWillems13\src\project\keras\labels.txt'
# Load the model and labels
model = load_model(model_path, compile=False)
with open(labels_path, 'r') as f:
    labels = f.read().splitlines()

image_width = 300
image_height = 300


def resize_and_show(image):
    h, w = image.shape[:2]
    if h < w:
        img = cv2.resize(image, (image_width, math.floor(h / (w / image_width))))
    else:
        img = cv2.resize(image, (math.floor(w / (h / image_height)), image_height))


def crop_and_predict(image: np.ndarray, hand_landmarks: mp_hands.HandLandmark) -> None:
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

    return hand_image


cap = cv2.VideoCapture(0)
with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
    count = 0
    current_hand_landmarks = None
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
        if current_hand_landmarks is not None:
            # crop_and_predict(image, current_hand_landmarks)
            hand_image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
            # Show the image in a window
            cv2.imshow('Webcam Image', hand_image)
            # Make the image a numpy array and reshape it to the models input shape.
            hand_image = np.asarray(hand_image, dtype=np.float32).reshape(1, 224, 224, 3)
            # Normalize the image array
            hand_image = (hand_image / 127.5) - 1
            # Have the model predict what the current image is. Model.predict
            # returns an array of percentages. Example:[0.2,0.8] meaning its 20% sure
            # it is the first label and 80% sure its the second label.
            probabilities = model.predict(hand_image)
            # Print what the highest value probabilitie label
            print(labels[np.argmax(probabilities)])
            # Listen to the keyboard for presses.
            keyboard_input = cv2.waitKey(1)
            # 27 is the ASCII for the esc key on your keyboard.
            if keyboard_input == 27:
                break

        cv2.waitKey(1)
    cap.release()
    cv2.destroyAllWindows()
