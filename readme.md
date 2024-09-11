# What is this?

This project body motion track software server side.

## Final target

1. [ ] T-body correction gyroscope.
2. [ ] Receive hardware signo and calculate motion frame.
3. [ ] Sending frame motion to blender client script.
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
