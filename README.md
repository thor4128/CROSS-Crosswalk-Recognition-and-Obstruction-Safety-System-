# Jetson Crosswalk Monitor

This is a Jetson-friendly Python prototype that:

- detects a zebra-style crosswalk region from the camera image
- detects road vehicles with a YOLO ONNX model
- raises an alert when a vehicle box overlaps the crosswalk

## Files

- `jetson_crosswalk_monitor.py`: main application
- `requirements.txt`: Python dependencies

## What you need on the Jetson

1. Python 3.9+ with OpenCV and NumPy installed
2. A YOLO `.onnx` object detection model trained on vehicle classes
3. A text file with one class name per line, matching the model output order

## Install

```bash
python3 -m pip install -r requirements.txt
```

For best Jetson performance, use an OpenCV build with CUDA enabled instead of the default pip wheel if you already have one on your device.

## Run

Camera input:

```bash
python3 jetson_crosswalk_monitor.py --source 0 --model yolov8n.onnx --classes coco.names
```

Video file input:

```bash
python3 jetson_crosswalk_monitor.py --source sample.mp4 --model yolov8n.onnx --classes coco.names --save-video output.mp4
```

## Notes

- The crosswalk detector is designed for zebra-style white stripe crosswalks.
- It searches the lower portion of the image by default. Adjust `--roi-top-ratio` if your camera angle is different.
- A vehicle is flagged when at least `15%` of its box overlaps the detected crosswalk polygon. Tune this with `--intrusion-ratio`.
- If your model uses `motorcycle` instead of `motorbike`, the code already handles both.
- For production use, you will likely want to calibrate the camera view and replace the heuristic crosswalk detector with a trained segmentation model.
