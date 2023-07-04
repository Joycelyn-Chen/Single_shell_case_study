import cv2 as cv
import os


img1_filename = "/Users/joycelynchen/Desktop/UBC/Research/Program/Single_shell_case_study/outputs/sn34_smd132_bx5_pe300_hdf5_plt_cnt_0300_z0/23.png"
img2_filename = "/Users/joycelynchen/Desktop/UBC/Research/Program/Single_shell_case_study/outputs/sn34_smd132_bx5_pe300_hdf5_plt_cnt_0300_z0/116.png"
img1 = cv.imread(img1_filename)
img2 = cv.imread(img2_filename)
img_name = img2_filename.split("/")[-2]

assert img1 is not None, "file could not be read, check with os.path.exists()"
# assert img2 is not None, "file could not be read, check with os.path.exists()"




out_img = cv.addWeighted(img1, 1, img2, 1, 0)

out_path = os.path.join("/Users/joycelynchen/Desktop/UBC/Research/Program/Single_shell_case_study/case_masks", img_name)
cv.imwrite(f"{out_path}.png", out_img)

