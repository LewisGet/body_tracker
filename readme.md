# What is this?

This project is body motion track software.


## Final target

1. [ ] T-body correction gyroscope.
2. [x] ~~Receive hardware signo and calculate motion frame.~~
3. [x] ~~Sending frame motion to blender client script.~~
4. [x] ~~Select key log frame and smooth between keyframes logs.~~


## api

1. smooth keyframes api `/keyframe/smooth_logs`. passing value by `GET` method.
    it will find all keyframes timestamp, each timestamp will add, sub a microsecond
    then search all `action_log` in this range and avg the logs vector.
    range config by `time_range`.
2. smooth keyframes api `/keyframe/smooth_logs`. will also calculate between keyframes,
    and split to multiple parts config by `split_parts` and range by `split_range`.
    eg: `split_parts=[0.25,0.5,0.75]&split_range=0.1`
    it will match 24% to 26% range logs vector in keyframes gap and avg it.
3. clean up logger `/record/reset_log`. you need to passing `confirm=true` to execute it.
4. batch create logger `/record/api/batch/create/action_log/` passing value like
    `target_id=1,2,3&target_type=1,1,1&x=1,2,3&y=1,2,3&z=1,2,3&timestamp=1,1,1` or
    same `target_type` `target_id=1,2,3&target_type=1&x=1,2,3&y=1,2,3&z=1,2,3&timestamp=1,1,1` or
    same id and type `target_id=1&target_type=1&x=1,2,3&y=1,2,3&z=1,2,3&timestamp=1,1,1`
5. setup baseline by record action logs `/record/setup/baseline` it will average all five seconds vectors. this data not include before three seconds ending data.


## blender

init script

```py
filename = "path_project/blender/main.py"
exec(compile(open(filename).read(), filename, 'exec'))
```


## web panel

1. to auto enable, disable hardware signal recording panel `/record/panel`
2. hardware connect panel `/record/hardware/connect/status`


## now testing status preview

[![Watch the video](https://img.youtube.com/vi/9I-nfS2DxPA/maxresdefault.jpg)](https://youtu.be/9I-nfS2DxPA)
