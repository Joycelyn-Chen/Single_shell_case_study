import cv2 as cv
import os
import numpy as np

def extract_files(root_dir):
    image_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                image_files.append(os.path.join(root, file))
    return image_files

def convert_binary_mask_to_red(mask_path):
    # Load the binary mask image
    mask = cv.imread(mask_path, cv.IMREAD_GRAYSCALE)

    # Create a red mask by duplicating the grayscale mask into all 3 channels
    red_mask = np.zeros((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)
    red_mask[:, :, 2] = mask

    return red_mask

masks_folder = "/Users/joycelynchen/Desktop/UBC/Research/Program/Single_shell_case_study/case_masks"
img_folder = "/Users/joycelynchen/Desktop/UBC/Research/Program/Single_shell_case_study/time_z0"
track_folder = "/Users/joycelynchen/Desktop/UBC/Research/Program/Single_shell_case_study/track_output"


# read the masks
mask_files = extract_files(masks_folder)
# read the images
image_files = extract_files(img_folder)


# read all the masks
for file in mask_files:
    
    red_mask = convert_binary_mask_to_red(file)
    for img in image_files:
        img_name = img.split("/")[-1].split(".")[-2]
        mask_name = file.split("/")[-1].split(".")[-2]
        # find the corresponding pair, cast the mask on the image
        if img_name == mask_name:
            origin_img = cv.imread(img)
            combined_img = cv.addWeighted(origin_img, 1, red_mask, 0.4, 0)
            
            # output the combined result to the folder
            filename = os.path.join(track_folder, f"{img_name}.png")
            cv.imwrite(filename, combined_img)
            print(f"Done with {img_name}")
    # cv.imshow("Red Mask", red_mask)
    # cv.waitKey(0)
    # cv.destroyAllWindows()
    



