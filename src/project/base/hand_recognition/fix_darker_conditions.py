import os

import cv2
import numpy as np

# Get the path to the image from the user
image_path = r"C:\Users\seppe\Pictures\Camera Roll\WIN_20230122_15_42_55_Pro.jpg"

# Get the path to the save folder from the user
save_folder = r"C:\Users\seppe\OneDrive\Bureaublad\dark_images_fix"

# Read the image
image = cv2.imread(image_path)

# Create a blank image with the same shape as the original image
blank_image = np.zeros(image.shape, dtype = image.dtype)

#create 2 for loops to itearte through alpha 1,2,3 and beta 0,10,20,30,40,50,60,70,80,90,100
for alpha in range(1,4):
    for beta in range(0,101,10):
        new_image = cv2.convertScaleAbs(image, alpha=2, beta=10)
        # Save the new image
        cv2.imwrite(os.path.join(save_folder, f"alpha_{alpha}_beta_{beta}.jpg"), new_image)
