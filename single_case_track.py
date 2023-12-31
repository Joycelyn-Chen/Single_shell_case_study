import os
import csv
from collections import defaultdict

class track:
    def __init__(self, initial_time, initial_id):
        self.initial_time = initial_time
        self.initial_id = initial_id
        self.tracker = []


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


def traverse_track(initial_id, target_track, initial_time_stamp = 200):
    single_track = [] 
    prev_id = initial_id
    track_died = False

    for time_stamp, segments in target_track.items():
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

def has_similar_size(prev_area, current_area):
    if current_area > prev_area:
        if float(prev_area)/float(current_area) > 0.8:
            return True
    else:
        if float(current_area)/float(prev_area) > 0.8:
            return True
    return False

def two_iou_overlapped(bbox_1, bbox_2, segment_bbox):
    if ((calculate_iou(bbox_1, segment_bbox) > 0.7) and (calculate_iou(bbox_2, segment_bbox) > 0.5)):
        return True
    return False
    



root_directory = "/home/joy0921/Desktop/2023S/Dataset/outputs"

# Create a dictionary to store the target track
#target_track = defaultdict(list)
target_track = []



# Get all the CSV files in the root directory and its subdirectories
csv_files = [os.path.join(root, file) for root, _, files in os.walk(root_directory) for file in files if file.endswith(".csv")]


#+--------------------------------------------------------------------------------------------------+
#| BEWARE!!!!!!!                                                                                    |
#| csv_file has to be in format: <root_dir/sn34_smd132_bx5_pe300_hdf5_plt_cnt_1490_z0/metadata.csv> |
#+--------------------------------------------------------------------------------------------------+

time_path = {}
for file in csv_files:
    time = int(file.split("/")[-2].split("_")[-2])
    time_path[time] = file

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
    for segment in segments:
        segment["time_stamp"] = time

    # Find the segment with the largest intersection of union with the previous time stamp
    if len(target_track) == 0:
        # If it's the first CSV file, record all segments
        for i, segment in enumerate(segments):
            target_track.append(track(segment["time_stamp"], segment["id"]))
            target_track[i].tracker.append(segment_obj(int(segment["time_stamp"]), int(segment["id"]), int(segment["area"]), [float(segment["bbox_x0"]), float(segment["bbox_y0"]),
                                                                                                     float(segment["bbox_w"]), float(segment["bbox_h"])]))
            # target_track[segment["time_stamp"]].append(segment)
    else:
        # previous_segments = target_track[list(target_track.keys())[-1]]

        # for segment in segments:
        #     max_iou = 0.0
        #     best_match = None

        #     for prev_segment in previous_segments:
        #         iou = calculate_iou(
        #             [float(prev_segment["bbox_x0"]), float(prev_segment["bbox_y0"]),
        #              float(prev_segment["bbox_w"]), float(prev_segment["bbox_h"])],
        #             [float(segment["bbox_x0"]), float(segment["bbox_y0"]),
        #              float(segment["bbox_w"]), float(segment["bbox_h"])]
        #         )

        #         if iou > max_iou:
        #             max_iou = iou
        #             best_match = segment   #originally: best_match = prev_segment
        #             best_match["prev_time"] = prev_segment["time_stamp"]
        #             best_match["prev_id"] = prev_segment["id"]

        #     if best_match is not None:
        #         target_track[segment["time_stamp"]].append(best_match)

        for target in target_track:
            prev_segment = target.tracker[-1]       # output a segment (time, id, area, bbox) prev_segment.bbox
            max_iou = 0.0
            best_match = None
            for segment in segments:
                segment_bbox = [float(segment["bbox_x0"]), float(segment["bbox_y0"]), float(segment["bbox_w"]), float(segment["bbox_h"])]
                iou = calculate_iou(prev_segment.bbox, segment_bbox)
                if iou > max_iou:
                    if len(target.tracker) > 2:
                        # compare the two time stamp before, area and iou
                        if not (has_similar_size(prev_segment.area, int(segment["area"])) and two_iou_overlapped(target.tracker[-1].bbox, target.tracker[-2].bbox, segment_bbox)):
                            continue

                    best_match = segment_obj(int(segment["time_stamp"]), int(segment["id"]), int(segment["area"]), [float(segment["bbox_x0"]), float(segment["bbox_y0"]),
                                                                                                     float(segment["bbox_w"]), float(segment["bbox_h"])])
            if best_match is not None:
                target.tracker.append(best_match)


# # Print the target track
# for time_stamp, segments in target_track.items():
#     print("Time Stamp:", time_stamp)
#     for segment in segments:
#         print("Segment:", segment)

# single_track = traverse_track(initial_id = 7, initial_time_stamp = 210, target_track = target_track)

# for track in single_track:
#     print(track)

# DEBUG: check if the definitions are correct
for target in target_track:
    if target.initial_id == 7 and target.initial_time_stamp == 210:
        print("\nYa did it!!!!\n\n")
        print(target.tracker)