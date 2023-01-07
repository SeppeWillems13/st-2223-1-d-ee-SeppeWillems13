import cv2
import numpy as np


class ImageProcessor:
    def __init__(self, detector, img_size, offset):
        self.detector = detector
        self.img_size = img_size
        self.offset = offset

    def process(self, img, hand):
        # Crop the image based on the bounding box of the detected hand
        x, y, w, h = hand['bbox']
        img_crop = img[y - self.offset:y + h + self.offset, x - self.offset:x + w + self.offset]

        # Convert the image to grayscale
        img_crop = cv2.cvtColor(img_crop, cv2.COLOR_BGR2GRAY)

        # Convert the image data to depth 8 bits per pixel
        img_hog = cv2.normalize(img_crop, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

        # Apply median filtering to the image to remove noise
        img_hog = cv2.medianBlur(img_hog, ksize=5)

        # Resize the image to 300x300
        img_crop = cv2.resize(img_hog, (self.img_size, self.img_size))

        # Add a third dimension to the resized image to match the shape of the white image
        img_resize = np.expand_dims(img_crop, axis=2)

        # Create an empty white image of size 300x300
        img_white = np.ones((self.img_size, self.img_size, 3), np.uint8) * 255

        return img_white, img_resize
