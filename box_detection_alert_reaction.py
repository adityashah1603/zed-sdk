"""
Box Detection with Reaction Time Logging for ZED Camera

Features:
1. Opens the ZED camera.
2. Runs a YOLO model to detect specified classes in the scene.
3. Triggers left/right alerts (external .exe) when detections are within 1 meter.
4. Records user reaction times whenever the reaction button is pressed after an alert.

To change which classes are detected:
    - Update the TARGET_CLASS_NAMES set below with the class names you want.
    - Class names must match the labels exposed by the loaded YOLO model.
    - Set TARGET_CLASS_NAMES = None to accept every class.
"""

import csv
import math
import os
import subprocess
import sys
import time
from collections import deque
from datetime import datetime
from typing import Deque, Dict, Optional

import cv2
import numpy as np
import pyzed.sl as sl

try:
    from ultralytics import YOLO
except ImportError as import_error:
    raise ImportError(
        "Ultralytics YOLO is required for this script. Install with `pip install ultralytics`."
    ) from import_error

# ----------------------------
# Configuration
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Default to custom weights if available, otherwise fall back to a small COCO model.
DEFAULT_MODEL_CANDIDATES = [
    #os.path.join(BASE_DIR, "best (1).pt"),
    
    os.path.join(BASE_DIR, "weights", "best.pt"),
    "yolov8n.pt",
]

YOLO_MODEL_PATH = next((path for path in DEFAULT_MODEL_CANDIDATES if os.path.exists(path)), DEFAULT_MODEL_CANDIDATES[-1])

# Set to a collection of class names you want the model to detect (case-sensitive).
# Example for COCO model: {"box", "person", "suitcase"}
# Set to None to detect every class the model predicts (default behaviour for stock YOLO weights).
TARGET_CLASS_NAMES = {"person"}  # Change to a set like {"box"} if you only want specific classes.

CONFIDENCE_THRESHOLD = 0.5
ALERT_DISTANCE_METERS = 1.0
ALERT_COOLDOWN_SECONDS = 1.0  # prevent repetitive alerts on the same side
 
# Path to tactile alert executable packaged under `TactorMatching3_Package`.
TACTOR_ALERT_EXE = os.path.join(
    BASE_DIR,
    "TactorMatching3_Package",
    "TactorMatching3_Package",
    "TactorMatching3.exe",
)
TACTOR_ALERT_LEVEL = "near"

# Reaction logging
REACTION_LOG_DIR = os.path.join(BASE_DIR, "reaction_times")
REACTION_KEY = ord(" ")  # spacebar key to acknowledge alerts
REACTION_LOG_PATH = os.path.join(
    REACTION_LOG_DIR, f"reaction_times_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
)


# ----------------------------
# Utility Functions
# ----------------------------
def load_yolo_model(model_path: str) -> YOLO:
    print(f"[INFO] Loading YOLO model from: {model_path}")
    model = YOLO(model_path)
    print(f"[INFO] Model loaded. Available classes ({len(model.names)}): {model.names}")
    return model


def filter_detection(cls_id: int, class_map: Dict[int, str]) -> bool:
    if TARGET_CLASS_NAMES is None:
        return True
    class_name = class_map.get(cls_id)
    return class_name in TARGET_CLASS_NAMES


def run_alert_executable(
    direction: str, level: str = TACTOR_ALERT_LEVEL
) -> Optional[subprocess.CompletedProcess]:
    exe_path = TACTOR_ALERT_EXE
    if not exe_path or not os.path.isfile(exe_path):
        print(f"[WARN] Alert executable not found: {exe_path}")
        return None
    try:
        print(f"[TACTOR] Triggering {direction.lower()} at {level.lower()} level via {exe_path}")
        result = subprocess.run(
            [
                exe_path,
                "--direction",
                direction.lower(),
                "--level",
                level.lower(),
            ],
            check=False,
        )
        if result.returncode != 0:
            print(f"[WARN] Tactor executable exited with code {result.returncode}")
        return result
    except Exception as exc:
        print(f"[ERROR] Failed to launch alert executable ({exe_path}): {exc}")
        return None


def save_reaction_times(records: Deque[Dict], csv_path: str) -> None:
    if not records:
        print("[INFO] No reaction times to save.")
        return
    fieldnames = ["alert_id", "timestamp", "class_name", "side", "distance_m", "reaction_time_s"]
    try:
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        with open(csv_path, "w", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                writer.writerow(record)
        print(f"[INFO] Reaction times written to {csv_path}")
    except Exception as exc:
        print(f"[ERROR] Failed to save reaction times: {exc}")


def depth_at_point(depth_map: sl.Mat, x: int, y: int) -> Optional[float]:
    width = depth_map.get_width()
    height = depth_map.get_height()
    if x < 0 or y < 0 or x >= width or y >= height:
        return None
    err, depth_value = depth_map.get_value(x, y)
    if err != sl.ERROR_CODE.SUCCESS:
        return None
    if depth_value <= 0 or math.isinf(depth_value) or math.isnan(depth_value):
        return None
    return float(depth_value)


# ----------------------------
# Main Routine
# ----------------------------
def main() -> int:
    reaction_log: Deque[Dict] = deque()
    pending_alerts: Deque[Dict] = deque()
    alert_triggered = False
    last_alert_time = {"LEFT": 0.0, "RIGHT": 0.0}
    alert_counter = 0

    model = load_yolo_model(YOLO_MODEL_PATH)
    class_map = model.names

    zed = sl.Camera()

    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD720
    init_params.camera_fps = 15
    init_params.depth_mode = sl.DEPTH_MODE.NEURAL
    init_params.coordinate_units = sl.UNIT.METER
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
    init_params.sdk_verbose = True

    if zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
        print("[ERROR] Unable to open ZED camera.")
        return 1

    runtime_params = sl.RuntimeParameters()
    depth_map = sl.Mat()
    image_left = sl.Mat()

    camera_info = zed.get_camera_information()
    image_size = camera_info.camera_configuration.resolution
    frame_center_x = image_size.width / 2

    window_name = "ZED Box Detection Alerts"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)

    try:
        while True:
            if zed.grab(runtime_params) != sl.ERROR_CODE.SUCCESS:
                continue

            zed.retrieve_image(image_left, sl.VIEW.LEFT)
            zed.retrieve_measure(depth_map, sl.MEASURE.DEPTH)

            frame_rgba = image_left.get_data()
            frame_bgr = cv2.cvtColor(frame_rgba, cv2.COLOR_BGRA2BGR)

            detections = model.predict(frame_bgr, verbose=False)[0]

            for det in detections.boxes:
                conf_tensor = det.conf
                conf = float(conf_tensor.item()) if hasattr(conf_tensor, "item") else float(conf_tensor)
                if conf < CONFIDENCE_THRESHOLD:
                    continue

                cls_tensor = det.cls
                cls_id = int(cls_tensor.item()) if hasattr(cls_tensor, "item") else int(cls_tensor)
                if not filter_detection(cls_id, class_map):
                    continue

                xyxy = det.xyxy[0] if len(det.xyxy.shape) > 1 else det.xyxy
                x1, y1, x2, y2 = [int(round(v)) for v in xyxy.tolist()]
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)

                distance = depth_at_point(depth_map, center_x, center_y)
                if distance is None:
                    continue

                side = "LEFT" if center_x < frame_center_x else "RIGHT"
                class_name = class_map.get(cls_id, f"class_{cls_id}")

                # Draw visuals
                color = (0, 255, 0)
                cv2.rectangle(frame_bgr, (x1, y1), (x2, y2), color, 2)
                label_text = f"{class_name} [{side}] {distance:.2f}m"
                cv2.putText(frame_bgr, label_text, (x1, max(15, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                now = time.time()
                if (
                    not alert_triggered
                    and distance < ALERT_DISTANCE_METERS
                    and now - last_alert_time[side] >= ALERT_COOLDOWN_SECONDS
                ):
                    alert_counter += 1
                    last_alert_time[side] = now
                    direction = "left" if side == "LEFT" else "right"
                    run_alert_executable(direction)

                    pending_alerts.append(
                        {
                            "alert_id": alert_counter,
                            "timestamp": datetime.now().isoformat(),
                            "class_name": class_name,
                            "side": side,
                            "distance_m": distance,
                            "trigger_time": now,
                        }
                    )
                    print(
                        f"[ALERT #{alert_counter}] {class_name} on {side} at {distance:.2f}m. Awaiting reaction..."
                    )
                    alert_triggered = True

            if pending_alerts:
                cv2.putText(
                    frame_bgr,
                    f"Alerts pending: {len(pending_alerts)} | Press SPACE when you respond",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2,
                )

            cv2.imshow(window_name, frame_bgr)
            key = cv2.waitKey(1) & 0xFF

            if key == 27:  # ESC
                print("[INFO] ESC pressed, exiting.")
                break
            if key == REACTION_KEY:
                if pending_alerts:
                    alert_event = pending_alerts.popleft()
                    reaction_time = time.time() - alert_event["trigger_time"]
                    alert_event["reaction_time_s"] = reaction_time
                    reaction_log.append(alert_event)
                    print(
                        f"[REACTION] Alert #{alert_event['alert_id']} ({alert_event['class_name']} {alert_event['side']}) "
                        f"reaction time: {reaction_time:.3f}s"
                    )
                else:
                    print("[INFO] Reaction key pressed with no pending alerts.")

    except KeyboardInterrupt:
        print("[INFO] Interrupted by user.")
    finally:
        cv2.destroyAllWindows()
        zed.close()
        save_reaction_times(reaction_log, REACTION_LOG_PATH)

    return 0


if __name__ == "__main__":
    sys.exit(main())

