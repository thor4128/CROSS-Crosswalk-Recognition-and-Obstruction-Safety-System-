import argparse
import time
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

import cv2
import numpy as np


VEHICLE_CLASSES = {"car", "truck", "bus", "motorbike", "motorcycle"}


@dataclass
class Detection:
    class_name: str
    confidence: float
    box: Tuple[int, int, int, int]


class YoloOnnxDetector:
    def __init__(
        self,
        model_path: str,
        class_names: Sequence[str],
        input_size: int = 640,
        confidence_threshold: float = 0.4,
        nms_threshold: float = 0.45,
        prefer_cuda: bool = True,
    ) -> None:
        self.input_size = input_size
        self.class_names = list(class_names)
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.net = cv2.dnn.readNetFromONNX(model_path)

        if prefer_cuda:
            try:
                self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
                self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
            except cv2.error:
                self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
                self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        else:
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    def detect(self, frame: np.ndarray) -> List[Detection]:
        height, width = frame.shape[:2]
        scale = min(self.input_size / width, self.input_size / height)
        new_w, new_h = int(width * scale), int(height * scale)

        # Letterbox the frame into a square input so we match the ONNX model size
        # without distorting the scene geometry too much.
        resized = cv2.resize(frame, (new_w, new_h))
        canvas = np.full((self.input_size, self.input_size, 3), 114, dtype=np.uint8)
        canvas[:new_h, :new_w] = resized

        blob = cv2.dnn.blobFromImage(canvas, scalefactor=1.0 / 255.0, size=(self.input_size, self.input_size), swapRB=True)
        self.net.setInput(blob)
        outputs = self.net.forward()
        return self._parse_outputs(outputs, width, height, scale)

    def _parse_outputs(
        self,
        outputs: np.ndarray,
        original_width: int,
        original_height: int,
        scale: float,
    ) -> List[Detection]:
        predictions = np.squeeze(outputs)
        if predictions.ndim != 2:
            raise ValueError("Unexpected YOLO output shape; expected a 2D tensor after squeezing.")

        # Many YOLO ONNX exports come out as either [num_preds, attrs] or
        # [attrs, num_preds], so normalize into one row per candidate.
        if predictions.shape[0] < predictions.shape[1]:
            predictions = predictions.T

        boxes = []
        scores = []
        class_ids = []

        for row in predictions:
            if row.shape[0] < 6:
                continue

            # YOLO rows are center-x, center-y, width, height, then class scores.
            cx, cy, w, h = row[:4]
            class_scores = row[4:]
            class_id = int(np.argmax(class_scores))
            score = float(class_scores[class_id])

            if score < self.confidence_threshold:
                continue

            x = int((cx - w / 2) / scale)
            y = int((cy - h / 2) / scale)
            bw = int(w / scale)
            bh = int(h / scale)

            x = max(0, min(x, original_width - 1))
            y = max(0, min(y, original_height - 1))
            bw = max(1, min(bw, original_width - x))
            bh = max(1, min(bh, original_height - y))

            boxes.append([x, y, bw, bh])
            scores.append(score)
            class_ids.append(class_id)

        indices = cv2.dnn.NMSBoxes(boxes, scores, self.confidence_threshold, self.nms_threshold)
        detections: List[Detection] = []
        if len(indices) == 0:
            return detections

        for idx in np.array(indices).flatten():
            class_name = self.class_names[class_ids[idx]] if class_ids[idx] < len(self.class_names) else str(class_ids[idx])
            detections.append(Detection(class_name=class_name, confidence=scores[idx], box=tuple(boxes[idx])))

        return detections


def load_class_names(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def order_quad(points: np.ndarray) -> np.ndarray:
    pts = points.astype(np.float32)
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    ordered = np.zeros((4, 2), dtype=np.float32)
    ordered[0] = pts[np.argmin(s)]
    ordered[2] = pts[np.argmax(s)]
    ordered[1] = pts[np.argmin(diff)]
    ordered[3] = pts[np.argmax(diff)]
    return ordered


def detect_crosswalk_polygon(frame: np.ndarray, roi_top_ratio: float = 0.45) -> Optional[np.ndarray]:
    height, width = frame.shape[:2]
    roi_top = int(height * roi_top_ratio)
    roi = frame[roi_top:, :]

    # We search only in the lower part of the image because that is where a
    # forward-facing road camera usually sees the crosswalk.
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 190, 255, cv2.THRESH_BINARY)

    # Morphology helps connect fragmented white paint into stripe-like blobs.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 3))
    opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    dilated = cv2.dilate(opened, kernel, iterations=2)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    stripe_boxes = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 300:
            continue

        # Zebra crosswalk stripes are usually wide, fairly flat bright regions.
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / float(h)
        if aspect_ratio < 2.0 or h > 90 or w < 25:
            continue

        stripe_boxes.append((x, y, w, h))

    if len(stripe_boxes) < 3:
        return None

    stripe_boxes.sort(key=lambda box: (box[1], box[0]))

    centers_y = np.array([y + h / 2 for (_, y, _, h) in stripe_boxes], dtype=np.float32)
    if centers_y.max() - centers_y.min() < 20:
        return None

    # Merge the candidate stripes into one enclosing quadrilateral that acts as
    # the crosswalk region for overlap checks.
    grouped = np.array(
        [
            [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]
            for (x, y, w, h) in stripe_boxes
        ],
        dtype=np.int32,
    )
    all_points = grouped.reshape(-1, 2)
    hull = cv2.convexHull(all_points.astype(np.int32))
    perimeter = cv2.arcLength(hull, True)
    approx = cv2.approxPolyDP(hull, 0.03 * perimeter, True)

    if len(approx) == 4:
        polygon = order_quad(approx.reshape(4, 2))
    else:
        rect = cv2.minAreaRect(hull)
        polygon = order_quad(cv2.boxPoints(rect))

    polygon[:, 1] += roi_top
    return polygon.astype(np.int32)


def box_overlap_ratio(box: Tuple[int, int, int, int], polygon: np.ndarray, frame_shape: Tuple[int, int, int]) -> float:
    x, y, w, h = box
    mask_poly = np.zeros(frame_shape[:2], dtype=np.uint8)
    mask_box = np.zeros(frame_shape[:2], dtype=np.uint8)

    # Rasterize both shapes into masks so we can measure how much of the vehicle
    # box lies inside the detected crosswalk area.
    cv2.fillPoly(mask_poly, [polygon], 255)
    cv2.rectangle(mask_box, (x, y), (x + w, y + h), 255, thickness=-1)

    overlap = cv2.bitwise_and(mask_poly, mask_box)
    overlap_area = cv2.countNonZero(overlap)
    box_area = max(1, w * h)
    return overlap_area / float(box_area)


def draw_polygon(frame: np.ndarray, polygon: np.ndarray, color: Tuple[int, int, int], label: str) -> None:
    cv2.polylines(frame, [polygon], isClosed=True, color=color, thickness=3)
    anchor = tuple(polygon[0])
    cv2.putText(frame, label, (anchor[0], max(20, anchor[1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2, cv2.LINE_AA)


def annotate_frame(
    frame: np.ndarray,
    polygon: Optional[np.ndarray],
    detections: Sequence[Detection],
    intrusion_ratio: float,
) -> Tuple[np.ndarray, bool]:
    output = frame.copy()
    intrusion_found = False

    if polygon is not None:
        draw_polygon(output, polygon, (0, 255, 255), "Crosswalk")

    for detection in detections:
        x, y, w, h = detection.box
        is_vehicle = detection.class_name.lower() in VEHICLE_CLASSES
        intruding = False

        if polygon is not None and is_vehicle:
            # Trigger only when enough of the vehicle box overlaps the crosswalk,
            # which reduces false alarms from boxes that barely touch the edge.
            overlap_ratio = box_overlap_ratio(detection.box, polygon, frame.shape)
            intruding = overlap_ratio >= intrusion_ratio
            intrusion_found = intrusion_found or intruding

        color = (0, 255, 0)
        if intruding:
            color = (0, 0, 255)
        elif is_vehicle:
            color = (255, 200, 0)

        cv2.rectangle(output, (x, y), (x + w, y + h), color, 2)
        label = f"{detection.class_name} {detection.confidence:.2f}"
        if intruding:
            label += " IN CROSSWALK"
        cv2.putText(output, label, (x, max(20, y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2, cv2.LINE_AA)

    status_text = "Vehicle in crosswalk" if intrusion_found else "Crosswalk clear"
    status_color = (0, 0, 255) if intrusion_found else (0, 200, 0)
    cv2.putText(output, status_text, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 1.0, status_color, 3, cv2.LINE_AA)
    return output, intrusion_found


def open_capture(source: str) -> cv2.VideoCapture:
    if source.isdigit():
        return cv2.VideoCapture(int(source))
    return cv2.VideoCapture(source)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detect a zebra crosswalk and flag vehicles entering it on NVIDIA Jetson.")
    parser.add_argument("--source", default="0", help="Camera index or video file path.")
    parser.add_argument("--model", required=True, help="Path to a YOLO ONNX model file.")
    parser.add_argument("--classes", required=True, help="Path to class names text file.")
    parser.add_argument("--input-size", type=int, default=640, help="YOLO input size.")
    parser.add_argument("--confidence", type=float, default=0.4, help="Detection confidence threshold.")
    parser.add_argument("--nms", type=float, default=0.45, help="Non-maximum suppression threshold.")
    parser.add_argument("--intrusion-ratio", type=float, default=0.15, help="Minimum box overlap ratio to trigger an alert.")
    parser.add_argument("--roi-top-ratio", type=float, default=0.45, help="Upper bound for the region searched for a crosswalk.")
    parser.add_argument("--save-video", default="", help="Optional output video path.")
    parser.add_argument("--no-display", action="store_true", help="Disable the preview window.")
    parser.add_argument("--cpu", action="store_true", help="Force CPU inference instead of CUDA.")
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    class_names = load_class_names(args.classes)
    detector = YoloOnnxDetector(
        model_path=args.model,
        class_names=class_names,
        input_size=args.input_size,
        confidence_threshold=args.confidence,
        nms_threshold=args.nms,
        prefer_cuda=not args.cpu,
    )

    cap = open_capture(args.source)
    if not cap.isOpened():
        raise RuntimeError(f"Unable to open video source: {args.source}")

    writer = None
    fps_counter_time = time.time()
    frame_counter = 0
    fps = 0.0

    # Main processing loop: read a frame, estimate the crosswalk, detect vehicles,
    # then draw the alert state for display or recording.
    while True:
        ok, frame = cap.read()
        if not ok:
            break

        polygon = detect_crosswalk_polygon(frame, roi_top_ratio=args.roi_top_ratio)
        detections = detector.detect(frame)
        annotated, intrusion = annotate_frame(frame, polygon, detections, args.intrusion_ratio)

        frame_counter += 1
        elapsed = time.time() - fps_counter_time
        if elapsed >= 1.0:
            fps = frame_counter / elapsed
            fps_counter_time = time.time()
            frame_counter = 0

        cv2.putText(annotated, f"FPS {fps:.1f}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        if intrusion:
            cv2.putText(annotated, "ALERT", (20, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 3, cv2.LINE_AA)

        if args.save_video:
            if writer is None:
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                height, width = annotated.shape[:2]
                source_fps = cap.get(cv2.CAP_PROP_FPS) or 20.0
                writer = cv2.VideoWriter(args.save_video, fourcc, source_fps, (width, height))
            writer.write(annotated)

        if not args.no_display:
            cv2.imshow("Jetson Crosswalk Monitor", annotated)
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord("q"):
                break

    cap.release()
    if writer is not None:
        writer.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
