"""
Parallel ZED detection with tactile feedback and reaction logging.

This script launches two independent threads:
1. Detection thread – handles ZED camera streaming, YOLO inference, and pushes
   alert events when an object is detected within 1 meter on either side.
2. Haptics thread – receives alert events, triggers `TactorMatching3.exe`, and
   records the user's reaction time (press Enter when the vibration is felt).

Outputs:
    - Reaction logs stored in `reaction_times/` alongside this script.
"""

import csv
import math
import os
import subprocess
import sys
import time
from queue import Empty, Queue
from threading import Event, Thread
from typing import Any, Dict, Optional, Set, Tuple, List

import cv2
import numpy as np
import pyzed.sl as sl

try:
    from ultralytics import YOLO
except ImportError as import_error:
    raise ImportError(
        "Ultralytics YOLO is required. Install with `pip install ultralytics`."
    ) from import_error


# ----------------------------
# Configuration
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TACTOR_EXE_PATH = os.path.join(BASE_DIR, "TactorMatching3.exe")
TACTOR_LEVEL = "near"
REACTION_LOG_DIR = os.path.join(BASE_DIR, "reaction_times")

CONFIDENCE_THRESHOLD = 0.3
ALERT_DISTANCE_METERS = 1.0
# Maximum distance (pixels) to match detections to tracked objects
TRACKING_MAX_DISTANCE = 100

MODEL_CANDIDATES = [
    #os.path.join(BASE_DIR, "best (1).pt"),
    os.path.join(BASE_DIR, "weights", "best.pt"),
    "yolov8n.pt",
]
YOLO_MODEL_PATH = next(
    (path for path in MODEL_CANDIDATES if os.path.exists(path)), MODEL_CANDIDATES[-1]
)


# ----------------------------
# Utility helpers
# ----------------------------
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


def trigger_tactor(direction: str, level: str = TACTOR_LEVEL) -> int:
    if not os.path.isfile(TACTOR_EXE_PATH):
        print(f"[TACTOR][WARN] Executable not found: {TACTOR_EXE_PATH}")
        return -1
    print(f"[TACTOR] Triggering {direction.lower()} at {level.lower()} level")
    result = subprocess.run(
        [
            TACTOR_EXE_PATH,
            "--direction",
            direction.lower(),
            "--level",
            level.lower(),
        ],
        check=False,
    )
    if result.returncode != 0:
        print(f"[TACTOR][WARN] Exit code {result.returncode}")
    return result.returncode


def ensure_reaction_log_dir() -> None:
    os.makedirs(REACTION_LOG_DIR, exist_ok=True)


def reaction_log_path() -> str:
    ensure_reaction_log_dir()
    timestamp = datetime_now()
    return os.path.join(REACTION_LOG_DIR, f"reaction_times_{timestamp}.csv")


def datetime_now() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


def write_reaction_header(csv_path: str) -> None:
    ensure_reaction_log_dir()
    with open(csv_path, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            ["alert_id", "timestamp", "class_name", "direction", "distance_m", "reaction_time_s"]
        )


def append_reaction_row(
    csv_path: str,
    alert_id: int,
    class_name: str,
    direction: str,
    distance_m: float,
    reaction_time_s: float,
) -> None:
    with open(csv_path, "a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                alert_id,
                time.strftime("%Y-%m-%dT%H:%M:%S"),
                class_name,
                direction.upper(), 
                f"{distance_m:.3f}",
                f"{reaction_time_s:.3f}",
            ]
        )


# ----------------------------
# Threads
# ----------------------------
def detection_worker(event_queue: Queue, stop_event: Event) -> None:
    from datetime import datetime

    reaction_counter = 0
    # Track objects with unique IDs and their state
    # Each tracked object has: (track_id, center_x, center_y, class_name, side, distance, below_threshold)
    tracked_objects: Dict[int, Dict[str, Any]] = {}  # track_id -> object info
    next_track_id = 1
    # Set of track IDs that have already triggered an alert (below threshold)
    alerted_track_ids: Set[int] = set()

    print(f"[DETECTION] Loading YOLO model from: {YOLO_MODEL_PATH}")
    model = YOLO(YOLO_MODEL_PATH)
    class_map = model.names

    zed = sl.Camera()
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD720
    init_params.camera_fps = 15
    init_params.depth_mode = sl.DEPTH_MODE.NEURAL
    init_params.coordinate_units = sl.UNIT.METER
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP

    if zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
        print("[DETECTION][ERROR] Unable to open ZED camera.")
        stop_event.set()
        event_queue.put(None)
        return

    runtime_params = sl.RuntimeParameters()
    depth_map = sl.Mat()
    image_left = sl.Mat()

    camera_info = zed.get_camera_information()
    image_size = camera_info.camera_configuration.resolution
    frame_center_x = image_size.width / 2

    window_name = "ZED Tactor Detection"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)

    print("[DETECTION] Started. Press ESC to exit.")
    try:
        while not stop_event.is_set():
            if zed.grab(runtime_params) != sl.ERROR_CODE.SUCCESS:
                continue

            zed.retrieve_image(image_left, sl.VIEW.LEFT)
            zed.retrieve_measure(depth_map, sl.MEASURE.DEPTH)

            frame_rgba = image_left.get_data()
            frame_bgr = cv2.cvtColor(frame_rgba, cv2.COLOR_BGRA2BGR)

            detections = model.predict(frame_bgr, verbose=False)[0]

            cv2.line(
                frame_bgr,
                (int(frame_center_x), 0),
                (int(frame_center_x), frame_bgr.shape[0]),
                (0, 255, 255),
                2,
            )

            # Current frame detections with their info
            current_detections: List[Dict[str, Any]] = []

            for det in detections.boxes:
                conf = float(det.conf.item()) if hasattr(det.conf, "item") else float(det.conf)
                if conf < CONFIDENCE_THRESHOLD:
                    continue

                cls_id = int(det.cls.item()) if hasattr(det.cls, "item") else int(det.cls)
                # Only detect class 1 (person)
                if cls_id != 0:
                    continue
                class_name = class_map.get(cls_id, f"class_{cls_id}")

                xyxy = det.xyxy[0] if len(det.xyxy.shape) > 1 else det.xyxy
                x1, y1, x2, y2 = [int(round(v)) for v in xyxy.tolist()]
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)

                distance = depth_at_point(depth_map, center_x, center_y)
                if distance is None:
                    continue

                side = "LEFT" if center_x < frame_center_x else "RIGHT"

                current_detections.append({
                    "center_x": center_x,
                    "center_y": center_y,
                    "class_name": class_name,
                    "side": side,
                    "distance": distance,
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                    "conf": conf,
                })

            # Match current detections to tracked objects
            matched_track_ids = set()
            for det_info in current_detections:
                center_x = det_info["center_x"]
                center_y = det_info["center_y"]
                class_name = det_info["class_name"]
                side = det_info["side"]
                distance = det_info["distance"]

                # Try to match to existing tracked object
                best_match_id = None
                best_distance = float('inf')

                for track_id, tracked_obj in tracked_objects.items():
                    # Must match class and side
                    if tracked_obj["class_name"] != class_name or tracked_obj["side"] != side:
                        continue

                    # Calculate distance between centers
                    dx = center_x - tracked_obj["center_x"]
                    dy = center_y - tracked_obj["center_y"]
                    dist = math.sqrt(dx * dx + dy * dy)

                    if dist < TRACKING_MAX_DISTANCE and dist < best_distance:
                        best_distance = dist
                        best_match_id = track_id

                if best_match_id is not None:
                    # Match found - update tracked object
                    track_id = best_match_id
                    tracked_objects[track_id].update({
                        "center_x": center_x,
                        "center_y": center_y,
                        "distance": distance,
                    })
                else:
                    # New object - assign new track ID
                    track_id = next_track_id
                    next_track_id += 1
                    tracked_objects[track_id] = {
                        "center_x": center_x,
                        "center_y": center_y,
                        "class_name": class_name,
                        "side": side,
                        "distance": distance,
                        "below_threshold": False,
                    }

                matched_track_ids.add(track_id)
                is_below_threshold = distance < ALERT_DISTANCE_METERS
                prev_below_threshold = tracked_objects[track_id].get("below_threshold", False)
                tracked_objects[track_id]["below_threshold"] = is_below_threshold

                # Determine color based on threshold state
                if is_below_threshold:
                    if track_id in alerted_track_ids:
                        color = (0, 0, 255)  # Red - already alerted
                    else:
                        color = (0, 255, 0)  # Green - just crossed threshold
                else:
                    color = (0, 255, 0)  # Green - above threshold

                # Draw bounding box
                cv2.rectangle(frame_bgr, (det_info["x1"], det_info["y1"]), 
                             (det_info["x2"], det_info["y2"]), color, 2)
                label_text = f"{class_name} [{side}] {distance:.2f}m ID:{track_id}"
                cv2.putText(
                    frame_bgr,
                    label_text,
                    (det_info["x1"], max(15, det_info["y1"] - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2,
                )

                # Check if object just crossed threshold (from above to below)
                if is_below_threshold and not prev_below_threshold and track_id not in alerted_track_ids:
                    # Object just crossed threshold - trigger alert
                    reaction_counter += 1
                    alerted_track_ids.add(track_id)
                    event_queue.put(
                        {
                            "alert_id": reaction_counter,
                            "timestamp": datetime.now().isoformat(),
                            "class_name": class_name,
                            "direction": side,
                            "distance_m": distance,
                        }
                    )
                    print(
                        f"[DETECTION][ALERT #{reaction_counter}] {class_name} on {side}"
                        f" (ID:{track_id}) crossed threshold at {distance:.2f}m (conf {det_info['conf']:.2f})"
                    )
                elif not is_below_threshold and prev_below_threshold and track_id in alerted_track_ids:
                    # Object went back above threshold - remove from alerted set so it can alert again
                    alerted_track_ids.discard(track_id)

            # Remove tracked objects that are no longer detected (went out of frame)
            tracked_objects = {tid: obj for tid, obj in tracked_objects.items() if tid in matched_track_ids}
            alerted_track_ids = {tid for tid in alerted_track_ids if tid in tracked_objects}

            cv2.imshow(window_name, frame_bgr)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                print("[DETECTION] ESC pressed. Exiting detection loop.")
                break

    except KeyboardInterrupt:
        print("[DETECTION] Interrupted by user.")
    finally:
        stop_event.set()
        event_queue.put(None)
        cv2.destroyAllWindows()
        zed.close()
        print("[DETECTION] Camera closed.")


def haptics_worker(event_queue: Queue, stop_event: Event) -> None:
    csv_path = reaction_log_path()
    write_reaction_header(csv_path)
    print(f"[HAPTICS] Logging reaction times to {csv_path}")

    while not stop_event.is_set():
        try:
            alert = event_queue.get(timeout=0.5)
        except Empty:
            continue

        if alert is None:
            break

        direction = alert["direction"]
        class_name = alert["class_name"]
        alert_id = alert["alert_id"]
        distance_m = alert["distance_m"]

        return_code = trigger_tactor(direction)
        start_time = time.time()

        if return_code != 0:
            print(f"[HAPTICS][WARN] Skipping reaction logging for alert {alert_id}")
            continue

        try:
            input_msg = (
                f"[HAPTICS] Alert #{alert_id} ({class_name} {direction}) fired."
                " Press Enter once you respond..."
            )
            input(input_msg)
        except KeyboardInterrupt:
            print("[HAPTICS] Interrupted during reaction capture.")
            stop_event.set()
            break

        reaction_time = time.time() - start_time
        append_reaction_row(csv_path, alert_id, class_name, direction, distance_m, reaction_time)
        print(
            f"[HAPTICS][REACTION] Alert #{alert_id} {direction} reaction time: {reaction_time:.3f}s"
        )

    print("[HAPTICS] Exiting.")


# ----------------------------
# Entrypoint
# ----------------------------
def main() -> int:
    event_queue: Queue = Queue()
    stop_event: Event = Event()

    detector = Thread(target=detection_worker, args=(event_queue, stop_event), daemon=True)
    haptics = Thread(target=haptics_worker, args=(event_queue, stop_event), daemon=True)

    detector.start()
    haptics.start()

    try:
        while detector.is_alive():
            detector.join(timeout=0.5)
    except KeyboardInterrupt:
        print("[MAIN] Keyboard interrupt received. Signaling shutdown.")
        stop_event.set()

    stop_event.set()
    event_queue.put(None)

    haptics.join()

    print("[MAIN] All threads terminated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())


