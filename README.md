# Single_shell_case_study

## Running SAM


## If missing 
- 

## Pre-process
- Check all the folders are clean and empty
    - case_masks/
    - track_outputs
- Check all the paths in the `single_cube.py` is pointing to the right place


## Generating tracking results
1. `single_cube.py`
- On compute2.idsl: Execute `python single_cube.py`

2. Execute `tmp.sh`: to copy the correspning masks to the one folder

3. Execute `track.py`: to combine the masks and the raw images to visualize the segmentation results.


---
# File explanations
## `single_cube_bk.py`
- iterating through SAM output and associating tracks together and output the correnspnding masks copying command to `tmp.sh`
- can only run for one single timestamp (entire 200, from z0 - z799)


