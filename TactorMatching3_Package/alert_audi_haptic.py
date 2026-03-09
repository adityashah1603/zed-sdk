"""
Parallel ZED detection with tactile feedback, audio alerts, and reaction logging.

This script launches two independent threads:
1. Detection thread – handles ZED camera streaming, YOLO inference, and pushes
   alert events when an object is detected within 1 meter on either side.
2. Haptics thread – receives alert events, triggers `TactorMatching3.exe`, plays
   audio alerts (left/right), and records the user's reaction time (press Enter
   the left/right arrow key when the vibration is felt).

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
    import msvcrt  # Windows-only; used for arrow-key reaction capture
except ImportError as import_error:
    raise ImportError(
        "This script requires Windows (msvcrt) for arrow-key reaction capture."
    ) from import_error

try:
    from ultralytics import YOLO
except ImportError as import_error:
    raise ImportError(
        "Ultralytics YOLO is required. Install with `pip install ultralytics`."
    ) from import_error

try:
    import pygame
    pygame.mixer.init()
except ImportError as import_error:
    raise ImportError(
        "Pygame is required for audio playback. Install with `pip install pygame`."
    ) from import_error


# ----------------------------
# Configuration
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TACTOR_EXE_PATH = os.path.join(BASE_DIR, "TactorMatching3.exe")
REACTION_LOG_DIR = os.path.join(BASE_DIR, "reaction_times")

# Tactor placement: "seatback" or "wrist" -> produces e.g. seatback-left, wrist-right
TACTOR_POSITION = "seatback"
# If True, flip LEFT/RIGHT for haptic output:
#   - obstacle on LEFT  -> vibrate RIGHT
#   - obstacle on RIGHT -> vibrate LEFT
REVERSE_HAPTIC_SIDES = False
 
# Audio mode: which set of sounds to use for alerts.
AUDIO_MODE = "pedestrian"

# Delay (in seconds) between when an alert event is generated and when
# the audio prompt is played. The tactor (haptic) is triggered immediately.
ALERT_AUDIO_DELAY_S = 1.65

CONFIDENCE_THRESHOLD = 0.3
ALERT_DISTANCE_METERS = 1.6
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


def trigger_tactor(direction: str) -> int:
    """Call TactorMatching3.exe --direction {position}-{left|right}"""
    if not os.path.isfile(TACTOR_EXE_PATH):
        print(f"[TACTOR][WARN] Executable not found: {TACTOR_EXE_PATH}")
        return -1
    position = TACTOR_POSITION.lower()

    # Optionally flip the logical LEFT/RIGHT coming from detection
    dir_up = direction.upper()
    if REVERSE_HAPTIC_SIDES:
        dir_up = "LEFT" if dir_up == "RIGHT" else "RIGHT"

    side = "left" if dir_up == "LEFT" else "right"
    full_direction = f"{position}-{side}"
    print(f"[TACTOR] Triggering {full_direction}")
    result = subprocess.run(
        [TACTOR_EXE_PATH, "--direction", full_direction],
        check=False,
    )
    if result.returncode != 0:
        print(f"[TACTOR][WARN] Exit code {result.returncode}")
    return result.returncode


def audio_file_for_alert(direction: str) -> Optional[str]:
    """
    Return the audio filename that corresponds to an alert direction + AUDIO_MODE.
    Returns None if AUDIO_MODE is unknown.
    """
    mode = AUDIO_MODE.lower()

    if mode == "steer":
        base_name = "Steer"
        side = "left" if direction.upper() == "RIGHT" else "right"
        return f"{base_name}_{side}.mp3"
    if mode == "pedestrian":
        base_name = "Pedestrian"
        side = "left" if direction.upper() == "LEFT" else "right"
        return f"{base_name}_{side}.mp3"
    if mode == "beep":
        base_name = "Beep"
        side = "right"  # pick whichever channel you want to use
        return f"{base_name}_{side}.mp3"

    return None


def play_audio(direction: str) -> bool:
    """
    Play audio file based on direction (LEFT or RIGHT) and AUDIO_MODE.
    AUDIO_MODE can be:
      - "steer":      steer/Steer_left.mp3 or steer/Steer_right.mp3
      - "pedestrian": pedestrian/Pedestrian_left.mp3 or pedestrian/Pedestrian_right.mp3
      - "beep":       beep/beep.mp3 for both directions
    Returns True if audio was played successfully, False otherwise.
    """
    mode = AUDIO_MODE.lower()

    if mode == "steer":
        folder = "steer"
        filename = audio_file_for_alert(direction) or ""
    elif mode == "pedestrian":
        folder = "pedestrian"
        filename = audio_file_for_alert(direction) or ""
    elif mode == "beep":
        folder = "beep"
        filename = audio_file_for_alert(direction) or ""
    else:
        print(f"[AUDIO][WARN] Unknown AUDIO_MODE '{AUDIO_MODE}'. Use: steer, pedestrian, or beep.")
        return False

    audio_dir = os.path.join(BASE_DIR, "Audio_Files", folder)
    audio_path = os.path.join(audio_dir, filename)

    if not os.path.isfile(audio_path):
        print(f"[AUDIO][WARN] Audio file not found: {audio_path}")
        return False

    try:
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        print(f"[AUDIO] Playing mode={AUDIO_MODE}, direction={direction}: {filename}")
        return True
    except Exception as e:
        print(f"[AUDIO][ERROR] Failed to play audio: {e}")
        return False


def ensure_reaction_log_dir() -> None:
    os.makedirs(REACTION_LOG_DIR, exist_ok=True)


def reaction_log_path() -> str:
    ensure_reaction_log_dir()
    timestamp = datetime_now()

    def _safe_part(value: object) -> str:
        s = str(value).strip()
        # keep filenames simple and cross-platform safe
        s = s.replace(" ", "-").replace(os.sep, "-")
        if os.altsep:
            s = s.replace(os.altsep, "-")
        return s

    filename = (
        f"{timestamp}_"
        f"{_safe_part(TACTOR_POSITION)}_"
        f"{_safe_part(REVERSE_HAPTIC_SIDES)}_"
        f"{_safe_part(AUDIO_MODE)}.csv"
    )
    return os.path.join(REACTION_LOG_DIR, filename)


def datetime_now() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


def write_reaction_header(csv_path: str) -> None:
    ensure_reaction_log_dir()
    with open(csv_path, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "alert_id",
                "timestamp",
                "class_name",
                "direction",
                "distance_m",
                "reaction_time_s",
                "key_pressed",
                "audio_file",
            ]
        )


def append_reaction_row(
    csv_path: str,
    alert_id: int,
    class_name: str,
    direction: str,
    distance_m: float,
    reaction_time_s: float,
    key_pressed: str,
    audio_file: str,
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
                key_pressed.upper(),
                audio_file,
            ]
        )


def play_audio_with_delay(direction: str, delay_s: float) -> None:
    """
    Play audio after an optional non-blocking delay, so we can trigger
    haptics and schedule audio "together" but start playback slightly later.
    """
    if delay_s > 0:
        time.sleep(delay_s)
    play_audio(direction)


def wait_for_any_arrow() -> str:
    """
    Block until the user presses either the Left or Right Arrow.
    Returns "LEFT" or "RIGHT" based on the key actually pressed.
    """
    # Arrow keys on Windows arrive as a two-character sequence:
    # prefix: '\x00' or '\xe0', then code: 'K' (left), 'M' (right)
    while True:
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):
            key = msvcrt.getwch()
            if key == "K":
                return "LEFT"
            if key == "M":
                return "RIGHT"


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

        # Record time from when we initiate haptics/audio to user reaction
        start_time = time.time()
        audio_file = audio_file_for_alert(direction) or ""

        # Start tactor and audio in their own threads so they run "together"
        def _tactor_thread() -> None:
            rc = trigger_tactor(direction)
            if rc != 0:
                print(f"[HAPTICS][WARN] Tactor command for alert {alert_id} exited with code {rc}")

        Thread(target=_tactor_thread, daemon=True).start()
        Thread(
            target=play_audio_with_delay,
            args=(direction, ALERT_AUDIO_DELAY_S),
            daemon=True,
        ).start()


        try:
            print(
                f"[HAPTICS] Alert #{alert_id} ({class_name} {direction}) fired. "
                "Press LEFT or RIGHT ARROW once you respond..."
            )
            key_pressed = wait_for_any_arrow()
        except KeyboardInterrupt:
            print("[HAPTICS] Interrupted during reaction capture.")
            stop_event.set()
            break

        reaction_time = time.time() - start_time
        append_reaction_row(
            csv_path,
            alert_id,
            class_name,
            direction,
            distance_m,
            reaction_time,
            key_pressed,
            audio_file,
        )
        print(
            f"[HAPTICS][REACTION] Alert #{alert_id} {direction} "
            f"reaction time: {reaction_time:.3f}s (key: {key_pressed})"
        )

        # After the first full alert + reaction is logged,
        # stop further alerts for this run.
        stop_event.set()
        break

    print("[HAPTICS] Exiting.")


# ----------------------------
# Entrypoint
# ----------------------------
def main() -> int:
    # Verify audio files exist (warn if not, but don't fail)
    mode = AUDIO_MODE.lower()
    base_audio_dir = os.path.join(BASE_DIR, "Audio_Files")

    if mode == "steer":
        audio_left = os.path.join(base_audio_dir, "steer", "Steer_left.mp3")
        audio_right = os.path.join(base_audio_dir, "steer", "Steer_right.mp3")
    elif mode == "pedestrian":
        audio_left = os.path.join(base_audio_dir, "pedestrian", "Pedestrian_left.mp3")
        audio_right = os.path.join(base_audio_dir, "pedestrian", "Pedestrian_right.mp3")
    elif mode == "beep":
        audio_left = audio_right = os.path.join(base_audio_dir, "beep", "beep.mp3")
    else:
        print(f"[WARN] Unknown AUDIO_MODE '{AUDIO_MODE}'. Use: steer, pedestrian, or beep.")
        audio_left = audio_right = None

    if audio_left and not os.path.isfile(audio_left):
        print(f"[WARN] Left audio file not found: {audio_left}")
        print("[WARN] Audio alerts will be disabled for LEFT direction.")
    if audio_right and not os.path.isfile(audio_right):
        print(f"[WARN] Right audio file not found: {audio_right}")
        print("[WARN] Audio alerts will be disabled for RIGHT direction.")
    
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

