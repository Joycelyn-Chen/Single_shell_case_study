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
    red_mask[:, :, 1] = mask
    red_mask[:, :, 2] = mask

    return red_mask

# masks_folder = "./case_masks"
masks_folder = "/home/joy0921/Desktop/2023S/Segmentation/XMem/workspace/output/masks"
# CV lab server
# img_folder = "/home/joy0921/Desktop/2023S/Dataset/200_210/raw_imgs"
# img_folder = "/home/joy0921/Desktop/Dataset/200_210/finer_time_200_210"
img_folder = "/home/joy0921/Desktop/2023S/Segmentation/XMem/workspace/output/images"
track_folder = "/home/joy0921/Desktop/2023S/Segmentation/XMem/workspace/output/track_output"


# read the masks
mask_files = extract_files(masks_folder)
# read the images
image_files = extract_files(img_folder)


# read all the maskstrash:///rename.py
for file in mask_files:
    red_mask = convert_binary_mask_to_red(file)
    for img in image_files:
        img_name = img.split("/")[-1].split(".")[-2]
        mask_name = file.split("/")[-1].split(".")[-2]
        # find the corresponding pair, cast the mask on the image
        if img_name == mask_name:
            origin_img = cv.imread(img)
            red_mask = red_mask * 2
            combined_img = cv.addWeighted(origin_img, 1, red_mask, 0.9, 0)
            
            # output the combined result to the folder
            filename = os.path.join(track_folder, f"{img_name}.png")
            cv.imwrite(filename, combined_img)
            print(f"Done with {img_name}")
    # cv.imshow("Red Mask", red_mask)
    # cv.waitKey(0)
    # cv.destroyAllWindows()
    



