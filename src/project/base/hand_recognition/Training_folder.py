import math
import os
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
    if not os.path.exists(f"{folder}/{user_input}"):
        os.makedirs(f"{folder}/{user_input}")

    cv2.imshow("Hand After Resize", hand_image)
    cv2.imwrite(f"{folder}/{user_input}/{picture_name}.jpg", hand_image)


# write me a program that takes folder as input and a user_input as input
folder = r"C:\Users\seppe\OneDrive\Bureaublad\rps_images\rps-cv-images\paper"
user_input = "paper"
folder_to_save = r"C:\Users\seppe\OneDrive\Bureaublad\rps_images\folder_to_save"

# loop to all images in folder
for filename in os.listdir(folder):
    # get the image
    image = cv2.imread(os.path.join(folder, filename))
    # convert image to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    cv2.flip(image, 1)
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    # Run MediaPipe Hands.
    with mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=1,
            min_detection_confidence=0.7) as hands:

        # Convert the BGR image to RGB, flip the image around y-axis for correct
        # handedness output and process it with MediaPipe Hands.
        results = hands.process(cv2.flip(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), 1))
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=hand_landmarks,
                    connections=mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles
                    .get_default_hand_landmarks_style())
                crop_and_save(image, hand_landmarks, folder, filename)
                cv2.imshow("Hand", image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
