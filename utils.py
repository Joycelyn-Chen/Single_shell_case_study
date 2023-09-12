import numpy as np
import cv2 as cv
import os
import matplotlib.pyplot as plt

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
    
    coordinates = np.argwhere(expanded_mask == 255)

    # Calculate the mean of pixels labeled as 1 in the mask
    labeled_pixels = image[expanded_mask == 255]
    
    # Uncomment this one
    mean = np.mean(labeled_pixels)
    # mean = 0
    return round(mean, 2)


def draw_area_graph(time, area, mean_dens, timestamp):
    area = [val * ((1000/256) ** 2) for val in area]
    fig, ax1 = plt.subplots()

    # Plot the first line
    ax1.plot(time, area, 'o-', label='Area', color='blue')
    ax1.set_xlabel('Time stamp')
    ax1.set_ylabel('Area (parsec squared)', color='black')

    # Create the second subplot sharing the same x-axis
    ax2 = ax1.twinx()

    # Plot the second line
    ax2.plot(time, mean_dens, 'o-', label='Mean Density', color='red')
    ax2.set_ylabel('Mean Density', color='black')

    # Add legend
    lines = ax1.get_lines() + ax2.get_lines()
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc='center left')
    plt.show()
    # plt.savefig(os.path.join("graph", f"{timestamp}.png"))
    


