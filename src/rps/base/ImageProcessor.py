import cv2
import numpy as np


class ImageProcessor:
    def __init__(self, detector, img_size, offset):
        self.detector = detector
        self.img_size = img_size
        self.offset = offset

    def process_image(self, img, hand):
        # Crop the image based on the bounding box of the detected hand
        x, y, w, h = hand['bbox']
        img_crop = img[y - self.offset:y + h + self.offset, x - self.offset:x + w + self.offset]

        # Convert the image to grayscale
        img_crop = cv2.cvtColor(img_crop, cv2.COLOR_BGR2GRAY)

        # Apply histogram equalization to enhance the contrast
        img_crop = cv2.equalizeHist(img_crop)

        # Apply Gaussian blur to the image to remove noise
        img_crop = cv2.GaussianBlur(img_crop, (5, 5), 0)

        # Calculate the edge map of the image
        img_crop = cv2.Canny(img_crop, 100, 200, L2gradient=True)

        # Calculate the HOG descriptor of the image
        win_size = (32, 32)
        block_size = (16, 16)
        block_stride = (8, 8)
        cell_size = (8, 8)
        num_bins = 9
        hog = cv2.HOGDescriptor(win_size, block_size, block_stride, cell_size, num_bins)
        img_hog = hog.compute(img_crop)

        # Normalize the pixel values to the range [0, 1]
        img_hog = np.interp(img_hog, (img_hog.min(), img_hog.max()), (0, 1))

        # Convert the image data to depth 8 bits per pixel
        img_hog = cv2.normalize(img_hog, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

        # Apply median filtering to the image to remove noise
        img_hog = cv2.medianBlur(img_hog, ksize=5)

        # Resize the image to 300x300
        img_crop = cv2.resize(img_hog, (self.img_size, self.img_size))

        # Add a third dimension to the resized image to match the shape of the white image
        img_resize = np.expand_dims(img_crop, axis=2)

        # Create an empty white image of size 300x300
        img_white = np.ones((self.img_size, self.img_size, 3), np.uint8) * 255

        return img_white, img_resize

