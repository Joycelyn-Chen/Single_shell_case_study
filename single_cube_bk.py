import os
import csv
from collections import defaultdict

class track:
    def __init__(self, initial_time, initial_id):
        self.initial_time = initial_time
        self.initial_id = initial_id
        self.tracker = []       # list of segments: [segment1, segment2]


class segment_obj:
    def __init__(self, time_stamp, id, area, bbox):
        self.time_stamp = time_stamp
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
    if float(area2) / float(area1) > 0.8:
        return True
    return False

def compare_area(area1, area2):
    # Place the one with bigger area as the denominator
    if area1 > area2:
        area2, area1 = area1, area2
    return float(area1) / float(area2)
    

def two_iou_overlapped(bbox_1, bbox_2, segment_bbox):
    if ((calculate_iou(bbox_1, segment_bbox) > 0.7) and (calculate_iou(bbox_2, segment_bbox) > 0.5)):
        return True
    return False
    
def in_the_target_area(bbox1, bbox2):
    extension = 100

    x1, y1, w1, h1 = bbox1  # the base, previous segment
    x2, y2, w2, h2 = bbox2  # the target segment

    if (x2 > x1 - extension) and (y2 > y1 - extension) and (w2 < w1 + extension) and (h2 < h1 + extension):
        return True
    return False

def record_all_segments(segments, target_tracks):
    for i, segment in enumerate(segments):
        target_tracks.append(track(segment["time_stamp"], segment["id"]))
        target_tracks[i].tracker.append(segment_obj(int(segment["time_stamp"]), int(segment["id"]), int(segment["area"]), [float(segment["bbox_x0"]), float(segment["bbox_y0"]),
                                                                                                float(segment["bbox_w"]), float(segment["bbox_h"])]))
    return target_tracks


# root directory to the SAM output masks 
# CV lab computer
#root_directory = "/home/joy0921/Desktop/2023S/SAM_outputs/outputs_200"
# compute2.idsl
root_directory = "/home/joy0921/Desktop/Dataset/200_210/outputs/201"

# Create a dictionary to store the target track
target_tracks = []           # list of tracks: [track1, track2]


# Get all the CSV files in the root directory and its subdirectories
#+--------------------------------------------------------------------------------------------------+
#| BEWARE!!!!!!!                                                                                    |
#| csv_file has to be in format: <root_dir/sn34_smd132_bx5_pe300_hdf5_plt_cnt_1490_z0/metadata.csv> |
#+--------------------------------------------------------------------------------------------------+
csv_files = [os.path.join(root, file) for root, _, files in os.walk(root_directory) for file in files if file.endswith(".csv")]

begin_time = 201
end_time = 202

for timestamp in range(begin_time, end_time):
    current_batch = []
    for file in csv_files:
        if int(file.split("/")[-2].split("_")[-2]) == timestamp:
            current_batch.append(file)

    time_path = {}          # {200+z : file_path, 201 (z = 1):file_path}
    for file in current_batch:
        time = int(file.split("/")[-2].split("_")[-2])      # to retrieve the 0200
        z = int(file.split("/")[-2].split("_")[-1][1:])     # to retrieve the z199
        time_path[time+z] = file

    # # Sort the CSV files by their dir name
    # sorted_time_path = sorted(time_path.items(), key=lambda x:x[0])
    sorted_csv_files = []
    for key in sorted(time_path):
        # print(key, ": ", time_path[key])
        sorted_csv_files.append(time_path[key])


    # Process each CSV file
    for csv_file in sorted_csv_files:
        with open(csv_file, "r") as file:
            reader = csv.DictReader(file)
            segments = list(reader)

        if len(segments) == 0:
            continue

        # Record the time stamp for all segments
        time = int(csv_file.split("/")[-2].split("_")[-2])
        z = int(csv_file.split("/")[-2].split("_")[-1][1:])
        for segment in segments:
            segment["time_stamp"] = time + z

        # Find the segment with the largest intersection of union with the previous time stamp
        if len(target_tracks) == 0:              # If it's the first CSV file, record all segments
            target_tracks = record_all_segments(segments, target_tracks)
            # for i, segment in enumerate(segments):
            #     target_tracks.append(track(segment["time_stamp"], segment["id"]))
            #     target_tracks[i].tracker.append(segment_obj(int(segment["time_stamp"]), int(segment["id"]), int(segment["area"]), [float(segment["bbox_x0"]), float(segment["bbox_y0"]),
            #                                                                                             float(segment["bbox_w"]), float(segment["bbox_h"])]))
                
        else:
            for target in target_tracks:
                prev_segment = target.tracker[-1]       # output a segment (time, id, area, bbox) prev_segment.bbox
                max_iou = 0.0
                best_match = None

                max_area_similarity = 0.0

                for segment in segments:
                    segment_bbox = [float(segment["bbox_x0"]), float(segment["bbox_y0"]), float(segment["bbox_w"]), float(segment["bbox_h"])]
                    if in_the_target_area(prev_segment.bbox, segment_bbox):
                        area_ratio = compare_area(prev_segment.area, int(segment["area"]))
                        if area_ratio > max_area_similarity:
                            max_area_similarity = area_ratio
                            best_match = segment_obj(int(segment["time_stamp"]), int(segment["id"]), int(segment["area"]), [float(segment["bbox_x0"]), float(segment["bbox_y0"]),
                                                                                                                            float(segment["bbox_w"]), float(segment["bbox_h"])])
                    
                if best_match is not None:
                    target.tracker.append(best_match)
        


    # # Print the target track
    # for time_stamp, segments in target_tracks.items():
    #     print("Time Stamp:", time_stamp)
    #     for segment in segments:
    #         print("Segment:", segment)

    # single_track = traverse_track(initial_id = 7, initial_time_stamp = 210, target_tracks = target_tracks)

    # for track in single_track:
    #     print(track)



    # DEBUG: check if the route definitions are correct

    mask_root = root_directory #'/home/joy0921/Desktop/2023S/SAM_outputs/outputs_200'
    folder_root = f'sn34_smd132_bx5_pe300_hdf5_plt_cnt_0{timestamp}'
    first_seg_id = 1

    with open("tmp.sh", "w") as f:
        for i, target in enumerate(target_tracks):
            # print(f"{i}:\ninit_time: {target.initial_time}\tinit_id: {target.initial_id}\t tracker len: {len(target.tracker)}")
            if int(target.initial_id) == first_seg_id and int(target.initial_time) == timestamp:
                print("+---------Case study Result------------+")
                for j, seg in enumerate(target.tracker):
                    print(f"[{j}]  Time stamp: {seg.time_stamp}\tId: {seg.id}\tArea: {seg.area}")
                    f.write(f"cp {os.path.join(mask_root, f'{folder_root}_z{seg.time_stamp - timestamp}', f'{seg.id}.png')} {os.path.join('case_masks', f'{folder_root}_z{seg.time_stamp - timestamp}.png')}\n")      
    print(f"+---------Done with t = {timestamp}------------+\n\n")

# 201:1, 
