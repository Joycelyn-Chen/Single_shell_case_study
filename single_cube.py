import os
import csv
from collections import defaultdict

class track:
    def __init__(self, initial_time, initial_id):
        self.initial_time = initial_time
        self.initial_id = initial_id
        self.prev_timestamp_segID = None
        self.next_timestamp_segID = None

        self.tracker = []       # list of segments: [segment1, segment2]


class segment_obj:      
    def __init__(self, slice_z, id, area, bbox):     
        self.slice_z = slice_z     
        self.id = id
        self.area = area
        self.bbox = bbox        #(bbox_x, bbox_y, bbox_w, bbox_h)
        

def calculate_iou(bbox1, bbox2):
    x1, y1, w1, h1 = bbox1
    x2, y2, w2, h2 = bbox2

    intersect_x = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
    intersect_y = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
    intersection = intersect_x * intersect_y

    union = (w1 * h1) + (w2 * h2) - intersection
    iou = intersection / union if union > 0 else 0.0

    return iou


def traverse_track(initial_id, target_tracks, initial_time_stamp = 200):
    single_track = [] 
    prev_id = initial_id
    track_died = False

    for time_stamp, segments in target_tracks.items():
        # start tracking when the segment appears
        if(int(time_stamp) < initial_time_stamp):
            continue

        for segment in segments:
            print(segment)
            if(int(segment["prev_id"]) == prev_id):
                print(time_stamp, ": ", end = "")
                print(segment["id"])
                single_track.append((int(time_stamp), int(segment["id"])))
                prev_id = int(segment["id"])
                break

    return single_track

def has_similar_size(area1, area2):
    # Place the one with bigger area as the denominator
    if area1 > area2:
        area2, area1 = area1, area2
    if float(area2) / float(area1) > 0.8:                       # magic
        return True
    return False

def compare_area(area1, area2):
    # Place the one with bigger area as the denominator
    if area1 > area2:
        area2, area1 = area1, area2
    return float(area1) / float(area2)
    

def two_iou_overlapped(bbox_1, bbox_2, segment_bbox):
    if ((calculate_iou(bbox_1, segment_bbox) > 0.7) and (calculate_iou(bbox_2, segment_bbox) > 0.5)):       # magic
        return True
    return False
    
def in_the_target_area(bbox1, bbox2):
    extension = 100

    x1, y1, w1, h1 = bbox1  # the base, previous segment
    x2, y2, w2, h2 = bbox2  # the target segment

    if (x2 > x1 - extension) and (y2 > y1 - extension) and (w2 < w1 + extension) and (h2 < h1 + extension):
        return True
    return False

def record_all_segments(segments, target_tracks, timestamp, begin_time):
    if timestamp == begin_time:
        for i, segment in enumerate(segments):
            target_tracks[timestamp].append(track(timestamp, segment["id"]))       
            target_tracks[timestamp][i].tracker.append(segment_obj(int(segment["slice_z"]), int(segment["id"]), int(segment["area"]), [float(segment["bbox_x0"]), float(segment["bbox_y0"]),
                                                                                                    float(segment["bbox_w"]), float(segment["bbox_h"])]))
    else:
        prev_segments = []
        for target in target_tracks[timestamp - 1]:
            prev_segments.append(target.tracker[0])         # organizing all of the first segments in the previous data cube into one list
        
        for i, segment in enumerate(segments):    
            target_tracks[timestamp].append(track(timestamp, segment["id"])) 
            target_tracks[timestamp][i].tracker.append(segment_obj(int(segment["slice_z"]), int(segment["id"]), int(segment["area"]), [float(segment["bbox_x0"]), float(segment["bbox_y0"]),
                                                                                                    float(segment["bbox_w"]), float(segment["bbox_h"])]))
           
            max_area_similarity = 0.0
            best_match = None
            target_segment = target_tracks[timestamp][i].tracker[-1]
            prev_trackID = None

            for j, prev_seg in enumerate(prev_segments):
                if in_the_target_area(target_segment.bbox, prev_seg.bbox):
                    area_ratio = compare_area(target_segment.area, prev_seg.area)
                    if area_ratio > max_area_similarity:
                        max_area_similarity = area_ratio
                        best_match = prev_seg
                        prev_trackID = j

            if best_match is not None:
                target_tracks[timestamp][i].prev_timestamp_segID = best_match.id
                target_tracks[timestamp - 1][prev_trackID].next_timestamp_segID = target_segment.id

    return target_tracks


def search4corresponding_z(tracker, z):
    for segment in tracker:
        if segment.slice_z == z:
            return segment
    return None

def search4best_match_in_segments(target_segment, segments):
    max_area_similarity = 0.0
    best_match = None

    for segment in segments:
        segment_bbox = [float(segment["bbox_x0"]), float(segment["bbox_y0"]), float(segment["bbox_w"]), float(segment["bbox_h"])]
        if in_the_target_area(target_segment.bbox, segment_bbox):
            area_ratio = compare_area(target_segment.area, int(segment["area"]))
            if area_ratio > max_area_similarity:
                max_area_similarity = area_ratio           
                best_match = segment_obj(int(segment["slice_z"]), int(segment["id"]), int(segment["area"]), [float(segment["bbox_x0"]), float(segment["bbox_y0"]),
                                                                                                                float(segment["bbox_w"]), float(segment["bbox_h"])])
        
    return best_match, max_area_similarity

def extract_current_batch(csv_files, timestamp):
    current_batch = []
    for file in csv_files:
        if int(file.split("/")[-2].split("_")[-2]) == timestamp:
            current_batch.append(file)
    return current_batch


def organize_paths_to_be_sorted(current_batch):
    time_path = {}                                          # {200+z : file_path, 201 (z = 1):file_path}
    for file in current_batch:
        time = int(file.split("/")[-2].split("_")[-2])      # to retrieve the 0200
        z = int(file.split("/")[-2].split("_")[-1][1:])     # to retrieve the z199
        time_path[time+z] = file
    return time_path

def sort_csv_files(time_path):
    sorted_csv_files = []
    for key in sorted(time_path):
        sorted_csv_files.append(time_path[key])
    return sorted_csv_files

def record_z_4_segments(csv_file, segments):
    z = int(csv_file.split("/")[-2].split("_")[-1][1:])
    for segment in segments:
        segment["slice_z"] = z 
    return segments

def adding_astro_prefix(time):
    if time < 1000:
        return f'sn34_smd132_bx5_pe300_hdf5_plt_cnt_0{time}'
    else:
        return f'sn34_smd132_bx5_pe300_hdf5_plt_cnt_{time}'


def trace_back_2_1st_timestamp(timestamp, begin_time, first_seg_id):
    current_time = begin_time
    next_timestamp_segID = target_tracks[begin_time][first_seg_id].next_timestamp_segID
    current_time += 1

    while current_time != timestamp:
        next_timestamp_segID = target_tracks[current_time][next_timestamp_segID].next_timestamp_segID
        current_time += 1

    return next_timestamp_segID


# root directory to the SAM output masks 
# CV lab computer
mask_root = "/home/joy0921/Desktop/2023S/Dataset/200_210/mask_outputs"    # magic
# compute2.idsl
# mask_root = "/home/joy0921/Desktop/Dataset/200_210/outputs/200"    # magic


# Get all the CSV files in the root directory and its subdirectories
#+--------------------------------------------------------------------------------------------------+
#| BEWARE!!!!!!!                                                                                    |
#| csv_file has to be in format: <root_dir/sn34_smd132_bx5_pe300_hdf5_plt_cnt_1490_z0/metadata.csv> |
#+--------------------------------------------------------------------------------------------------+
csv_files = [os.path.join(root, file) for root, _, files in os.walk(mask_root) for file in files if file.endswith(".csv")]

begin_time = 200                                                        # magic
end_time = 202                                                          # magic

# Create a dictionary to store the target track
target_tracks = {i: [] for i in range(begin_time, end_time)}           # dict of tracks: {200: [track1], 201: [track2]...}


# Preprocess the first batch, which is the first timestamp
# have the first cube ready so that all the subsequent timestamp can be tracked accordingly
current_batch = extract_current_batch(csv_files, begin_time)
time_path = organize_paths_to_be_sorted(current_batch)
sorted_csv_files = sort_csv_files(time_path)


for csv_file in sorted_csv_files:
    with open(csv_file, "r") as file:
        segments = list(csv.DictReader(file))
    if len(segments) == 0:      # if no generated masks from SAM, then continue reading the next file
            continue

    segments = record_z_4_segments(csv_file, segments)  

    # Find the segment with the largest intersection of union with the previous time stamp
    if len(target_tracks[begin_time]) == 0:              # If it's the first CSV file, record all segments
        target_tracks = record_all_segments(segments, target_tracks, begin_time, begin_time)
        
    else:
        for target in target_tracks[begin_time]:
            prev_segment = target.tracker[-1]       # output a segment (time, id, area, bbox) prev_segment.bbox
            
            best_match, _ = search4best_match_in_segments(prev_segment, segments)
            
            if best_match is not None:
                target.tracker.append(best_match)


folder_root = adding_astro_prefix(begin_time)    
first_seg_id = 17                                                       # magic

with open("tmp.sh", "w") as f:
    f.write("rm -rf case_masks\n")
    f.write("mkdir case_masks\n")
    for i, target in enumerate(target_tracks[begin_time]):
        if i == 17:
            print(target.initial_time)
        # print(f"{i}:\ninit_time: {target.initial_time}\tinit_id: {target.initial_id}\t tracker len: {len(target.tracker)}")
        if int(target.initial_id) == first_seg_id and int(target.initial_time) == begin_time:
            print("+---------Case study Result------------+")
            for j, seg in enumerate(target.tracker):
                print(f"[{j}]  Time stamp: {begin_time} - {seg.slice_z}\tId: {seg.id}\tArea: {seg.area}")       
                f.write(f"cp {os.path.join(mask_root, str(begin_time), f'{folder_root}_z{seg.slice_z}', f'{seg.id}.png')} {os.path.join('case_masks', f'{folder_root}_z{seg.slice_z}.png')}\n")      
print(f"+---------Done with t = {begin_time}------------+\n\n")





# Now process the subsequent data cubes
for timestamp in range(begin_time + 1, end_time):
    current_batch = extract_current_batch(csv_files, timestamp)
    time_path = organize_paths_to_be_sorted(current_batch)          # {200+z : file_path, 201 (z = 1):file_path}

    # Sort the CSV files by their dir name
    sorted_csv_files = sort_csv_files(time_path)
    
    # Process each CSV file
    for csv_file in sorted_csv_files:
        with open(csv_file, "r") as file:
            # reader = csv.DictReader(file)
            # segments = list(reader)
            segments = list(csv.DictReader(file))

        if len(segments) == 0:      # if no generated masks from SAM, then continue reading the next file
            continue

        # Record the z slices for all segments
        z = int(csv_file.split("/")[-2].split("_")[-1][1:])
        segments = record_z_4_segments(csv_file, segments)  

        # Find the segment with the largest intersection of union with the previous time stamp
        if len(target_tracks[timestamp]) == 0:              # If it's the first CSV file of the timestamp, record all segments
            target_tracks = record_all_segments(segments, target_tracks, timestamp, begin_time)
            
        else:
            # for the subsequent timestamps
            for target in target_tracks[timestamp]:
                prev_z_segment = target.tracker[-1]
                prev_t_segment = search4corresponding_z(target.tracker, z)  
                best_match, _ = search4best_match_in_segments(prev_z_segment, segments)

                if prev_t_segment is not None:
                    # find best match for both prev_z and prev_t, if they match, good, if doesn't, move on for now          # debug
                    best_match_t, _ = search4best_match_in_segments(prev_t_segment, segments)
                    if not best_match.id == best_match_t.id:
                        best_match = None

                if best_match is not None:
                    target.tracker.append(best_match)
        


    # DEBUG: check if the route definitions are correct

    folder_root = adding_astro_prefix(timestamp)
    first_seg_id = trace_back_2_1st_timestamp(timestamp, begin_time, first_seg_id)                                   

    with open("tmp.sh", "a+") as f:
        for i, target in enumerate(target_tracks[timestamp]):
            if int(target.initial_id) == first_seg_id and int(target.initial_time) == timestamp:
                print("+---------Case study Result------------+")
                for j, seg in enumerate(target.tracker):
                    print(f"[{j}]  Time stamp: {timestamp} - {seg.slice_z}\tId: {seg.id}\tArea: {seg.area}")       
                    f.write(f"cp {os.path.join(mask_root, str(timestamp),f'{folder_root}_z{seg.slice_z}', f'{seg.id}.png')} {os.path.join('case_masks', f'{folder_root}_z{seg.slice_z}.png')}\n")      
    print(f"+---------Done with t = {timestamp}------------+\n\n")

# 201:1, 


