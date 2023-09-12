import numpy as np
import cv2 as cv
import os

def calculate_mean_with_mask(image_filename, mask_filename):
    image = cv.imread(image_filename)
    mask = cv.imread(mask_filename)  

    # Convert the image and mask to numpy arrays
    image = np.array(image)

    gray = cv.cvtColor(mask, cv.COLOR_BGR2GRAY)
  
    # Apply thresholding to create a binary mask
    _, binary_mask = cv.threshold(gray, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)
    mask = np.array(binary_mask)
    expanded_mask = np.repeat(mask[:, :, np.newaxis], 3, axis=2)
    
    # Check if the image and mask have the same size
    if image.shape != expanded_mask.shape:
        raise ValueError("Image and mask must have the same size.")
    
    # coordinates = np.argwhere(expanded_mask == 255)

    # Calculate the mean of pixels labeled as 1 in the mask
    labeled_pixels = image[expanded_mask == 255]
    
    # Uncomment this one
    mean = np.mean(labeled_pixels)
    # mean = 0
    return round(mean, 2)

# # CV lab computer
# image_root = "/home/joy0921/Desktop/2023S/Dataset/200_210/raw_imgs"
# mask_root = "./case_masks"
# graph_root = "./graphs"


image_root = "./time_z0"
mask_root = "./case_masks"

mean_list = []

begin_time = 200
end_time = 209 + 1


# read all the masks images within the masks/

# sort the with the timestamp (ascending)

# for each timestamp, calculate the accumulated size and mean density


for i in range(begin_time, end_time):
    filename = f"sn34_smd132_bx5_pe300_hdf5_plt_cnt_0{i}_z0"
    image = cv.imread(f"{os.path.join(image_root, filename)}.jpg")
    mask = cv.imread(f"{os.path.join(mask_root, filename)}.png")
    mean_list.append(calculate_mean_with_mask(image, mask))

print("Mean:", mean_list)

