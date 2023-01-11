"""Import all dependencies."""
import os
import argparse
import numpy as np
import math
import time
import cv2
from cvzone.HandTrackingModule import HandDetector


def collect_images(label_name, num_samples):
    """Get num_samples of type label_name with hand recognition and save them in their respected folder"""
    # Set up the save path and create the directory if it doesn't exist
    save_path = os.path.join('../image_data', label_name)
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
    #delay = 1000  # delay in milliseconds
    start_key = ord('s')
    stop_key = ord('q')

    while True:
        if count == num_samples:
            break

        success, img = cap.read()
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

            # If the aspect ratio is less than or equal to 1, add the resized image to the white image
            # with a gap at the left and right to center the image
            else:
                w_gap = math.ceil((img_size - img_resize.shape[1]) / 2)
                img_white[:, w_gap:w_gap + img_resize.shape[1]] = img_resize

            # Display the original and preprocessed images
            cv2.imshow("ImageCrop", img_crop)
            cv2.imshow("ImageWhite", img_white)

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, "Collecting {}/{} of type {}".format(count, num_samples, label_name),
                    (5, 50), font, 0.7, (0, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow("Image", img)

        # Check if the user has pressed the start key
        #key = cv2.waitKey(delay)
        #if key == start_key:
        start = True

        # Check if the user has pressed the stop key
        #elif key == stop_key:
            #break

        # Save the preprocessed image to a file if collection has started
        if start:
            count += 1
            file_path = os.path.join(save_path, f'image_{time.time()}.jpg')
            success = cv2.imwrite(file_path, img_white)
            if success:
                print(f'Saved image {count} to {file_path}')
            else:
                print(f'Failed to save image {count}')

        # Release the video capture and destroy the windows
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('label_name', type=str, help='Name of the label to collect')
    parser.add_argument('num_samples', type=int, help='Number of samples to collect')
    args = parser.parse_args()

    collect_images(args.label_name, args.num_samples)
