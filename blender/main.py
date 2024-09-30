import bpy
import json
import datetime
import requests
from math import radians


fps = 40
# key frame json uri
api_url = "http://127.0.0.1:8000/keyframe/smooth_logs/?time_range=100&split_parts=1,0.5,0&split_range=0.5"

def get_json():
    response = requests.get(api_url)
    return json.loads(response.content)

def datetime_iso8601(value):
    return value.replace("T", " ").replace("Z", "+00:00")

def get_min_timestamp(data):
    timestamps = []

    for keyframe_type in data:
        for part_index_json_str in data[keyframe_type]:
            for part_log in data[keyframe_type][part_index_json_str]:
                timestamps.append(datetime.datetime.fromisoformat(datetime_iso8601(part_log['s'])).timestamp())

    return min(timestamps)

data = get_json()
timebase = get_min_timestamp(data)
bpy.ops.object.mode_set(mode='POSE')

for keyframe_type in data:
    if keyframe_type != "finger_keyframe_logs":
        continue

    for part_index_json_str in data[keyframe_type]:
        part = json.loads(part_index_json_str)
        bone_name = part['hand'] + "_" + part['finger_index'] + "_" + part['segment_type']
        bone = bpy.context.object.pose.bones.get(bone_name)

        if bone == None:
            print(bone_name + " is not found")
            continue

        for part_log in data[keyframe_type][part_index_json_str]:
            start_timestamp = datetime.datetime.fromisoformat(datetime_iso8601(part_log['s'])).timestamp()
            frame = int((start_timestamp - timebase) * fps)

            bone.rotation_mode = 'XYZ'
            bone.rotation_euler = (radians(part_log['x']), radians(part_log['y']), radians(part_log['z']))
            bone.keyframe_insert(data_path="rotation_euler", frame=frame)
            bpy.context.view_layer.update()
