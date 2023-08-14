import os

# Function to find missing correspondences
def find_missing_correspondences(image_folder, subfolder_folder):
    # Get the list of image filenames
    image_filenames = os.listdir(image_folder)
   
    # Get the list of subfolder names
    subfolder_names = os.listdir(subfolder_folder)
   
    # Create a list to store missing correspondences
    missing_correspondences = image_filenames.copy()
   
    # Compare subfolder names with image filenames
    for subfolder_name in subfolder_names:
        if subfolder_name in missing_correspondences:
            missing_correspondences.remove(subfolder_name)
   
    return missing_correspondences

# Input folders
# It's on compute2.idsl
image_folder = "/home/joy0921/Desktop/Dataset/finer_time_200_210"
subfolder_folder = "/home/joy0921/Desktop/Segmentation/segment-anything/outputs_0811_200_210"

# Find missing correspondences
missing_correspondences = find_missing_correspondences(image_folder, subfolder_folder)

# Print the list of missing correspondences
print("Missing Correspondences:")
for missing in missing_correspondences:
    print(missing)