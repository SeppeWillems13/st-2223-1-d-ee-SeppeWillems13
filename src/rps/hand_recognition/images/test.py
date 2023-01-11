"""Import all dependencies."""
import os
import argparse
import numpy as np
import math
import time
import cv2
from cvzone.HandTrackingModule import HandDetector


def collect_images(label_name=None, num_samples=None, image_dir=None):
    """Get num_samples of type label_name with hand recognition and save them in their respected folder"""

    # Set up the save path and create the directory if it doesn't exist
    if label_name is None:
        label_name = input("Enter the label name: ")
    save_path = os.path.join('../image_data', label_name)
    os.makedirs(save_path, exist_ok=True)

    offset = 20
    img_size = 300
    delay = 1000  # delay in milliseconds
    start_key = ord('s')
    stop_key = ord('q')
    detector = HandDetector(maxHands=1)

    if image_dir is None:
        # If image_dir is not provided, use the camera for input
        # Initialize the camera and set up the video capture
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error opening video stream or file")
            return
        if num_samples is None:
            num_samples = int(input("Enter the number of samples to collect: "))
        count = 0
        while True:
            if count == num_samples:
                break

            success, img = cap.read()
            if success:
                hands = detector.findHands(img, draw=False)
                if hands:
                    hand = hands[0]
                    # Preprocess the image for hand recognition
                    img_crop = preprocess_image(img, hand, offset, img_size)

                # Display the original and preprocessed images
                cv2.imshow("Original", img)
                cv2.imshow("Preprocessed", img_crop)

                key = cv2.waitKey(delay)
                if key == start_key:
                    # Save the preprocessed image to the save directory
                    cv2.imwrite(os.path.join(save_path, f'{count}.jpg'), img_crop)
                    count += 1
                elif key == stop_key:
                    break
        cap.release()
    else:
        # If image_dir is provided, read the images from the specified directory
        # Get a list of all the files in the directory
        image_files = os.listdir(image_dir)
        # Sort the files by name
        image_files.sort()
        # Iterate through the files and process_image the images
        for file in image_files:

            # Load the image file
            img = cv2.imread(os.path.join(image_dir, file))
            hands = detector.findHands(img, draw=False)
            if hands:
                hand = hands[0]
                # Preprocess the image for hand recognition
                img_crop = preprocess_image(img, hand, offset, img_size)
                if img_crop is None or img.size == 0:
                    continue
                # Display the original and processed images
                cv2.imshow("Original", img)
                cv2.imshow("Preprocessed", img_crop)
                cv2.waitKey(delay)

                # Save the preprocessed image to the save directory
                cv2.imwrite(os.path.join(save_path, f'{file}'), img_crop)


def preprocess_image(img, hand, offset, img_size):
    """Preprocess the image for hand recognition"""
    # Check if the image is empty or invalid
    if img is None or img.size == 0:
        return None

    # Crop the image based on the bounding box of the detected hand
    x, y, w, h = hand['bbox']
    img_crop = img[y - offset:y + h + offset, x - offset:x + w + offset]
    # Normalize the pixel values to the range [0, 1]
    if img_crop.size <= 0:
        return
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

    return img_white


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--label_name', type=str, required=True, help='Label name for the collected images')
    parser.add_argument('--num_samples', type=int, required=False, help='Number of samples to collect')
    parser.add_argument('--image_dir', type=str, required=False, help='Directory containing images to be processed')
    args = parser.parse_args()

    label_name = args.label_name
    num_samples = args.num_samples
    image_dir = args.image_dir
    collect_images(label_name, num_samples, image_dir)
