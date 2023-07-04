import numpy as np
import cv2 as cv
import os

def calculate_mean_with_mask(image, mask):
    # Convert the image and mask to numpy arrays
    image = np.array(image)
    mask = np.array(mask)
    
    # Check if the image and mask have the same size
    if image.shape != mask.shape:
        raise ValueError("Image and mask must have the same size.")
    
    print(mask)
    for i in mask:
        for j in i:
            if(mask[i][j] == 1):
                print(f"({i}, {j})")
    # Calculate the mean of pixels labeled as 1 in the mask
    labeled_pixels = image[mask == 1]
    
    # mean = np.mean(labeled_pixels)
    mean = 0
    return mean


image_root = "/home/joy0921/Desktop/2023S/Single_shell_case_study/time_z0"
mask_root = "/home/joy0921/Desktop/2023S/Single_shell_case_study/case_masks"
filename = "sn34_smd132_bx5_pe300_hdf5_plt_cnt_0200_z0"
image = cv.imread(f"{os.path.join(image_root, filename)}.jpg")
mask = cv.imread(f"{os.path.join(mask_root, filename)}.png")


mean = calculate_mean_with_mask(image, mask)
print("Mean:", mean)
