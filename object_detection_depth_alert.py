"""
ZED Object Detection with Depth and Position Alerts

This script:
1. Detects objects using ZED's AI object detection
2. Measures depth/distance to each object
3. Classifies objects as LEFT or RIGHT based on position in frame
4. Alerts when objects are within 1 meter proximity
5. Displays live camera feed with bounding boxes and labels
"""

import pyzed.sl as sl
import cv2
import numpy as np
import sys
import math

def main():
    # Create ZED camera object
    zed = sl.Camera()
    
    # Set initialization parameters
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD720  # 720p resolution
    init_params.camera_fps = 30  # 30 FPS
    init_params.depth_mode = sl.DEPTH_MODE.NEURAL  # High quality depth mode
    init_params.coordinate_units = sl.UNIT.METER  # Use meters for measurements
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
    init_params.sdk_verbose = True
    
    # Open the camera
    print("Opening ZED Camera...")
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print(f"Error opening camera: {repr(err)}")
        exit(1)
    
    print("Camera opened successfully!")
    
    # Get camera information
    camera_info = zed.get_camera_information()
    print(f"Camera Model: {camera_info.camera_model}")
    print(f"Serial Number: {camera_info.serial_number}")
    print(f"Firmware: {camera_info.camera_configuration.firmware_version}")
    
    # Enable positional tracking (required for object detection)
    print("\nEnabling Positional Tracking...")
    tracking_params = sl.PositionalTrackingParameters()
    tracking_params.enable_imu_fusion = True
    err = zed.enable_positional_tracking(tracking_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print(f"Error enabling tracking: {repr(err)}")
        zed.close()
        exit(1)
    
    print("Positional tracking enabled!")
    
    # Enable object detection
    print("\nEnabling Object Detection...")
    obj_detection_params = sl.ObjectDetectionParameters()
    obj_detection_params.enable_tracking = True
    obj_detection_params.enable_segmentation = False  # Set to True for person masks
    obj_detection_params.detection_model = sl.OBJECT_DETECTION_MODEL.MULTI_CLASS_BOX_FAST
    
    err = zed.enable_object_detection(obj_detection_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print(f"Error enabling object detection: {repr(err)}")
        zed.close()
        exit(1)
    
    print("Object detection enabled!")
    print("\n" + "="*70)
    print("Starting object detection and depth analysis...")
    print("Press Ctrl+C to stop")
    print("="*70 + "\n")
    
    # Runtime parameters for object detection
    obj_runtime_params = sl.ObjectDetectionRuntimeParameters()
    obj_runtime_params.detection_confidence_threshold = 40  # 40% confidence threshold
    
    # Runtime parameters for grab
    runtime_params = sl.RuntimeParameters()
    
    # Objects container
    objects = sl.Objects()
    
    # Get image dimensions for left/right classification
    image_size = zed.get_camera_information().camera_configuration.resolution
    frame_center_x = image_size.width / 2
    
    # Alert threshold in meters
    ALERT_DISTANCE = 1.0
    
    # Create Mat objects for image retrieval
    image_left = sl.Mat()
    
    # Create OpenCV window
    window_name = "ZED Object Detection - Depth & Position Alerts"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)
    
    frame_count = 0
    
    try:
        while True:
            # Grab a new frame
            if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
                frame_count += 1
                
                # Retrieve the left image
                zed.retrieve_image(image_left, sl.VIEW.LEFT)
                
                # Convert to OpenCV format (BGRA to BGR)
                image_ocv = image_left.get_data()
                image_bgr = cv2.cvtColor(image_ocv, cv2.COLOR_BGRA2BGR)
                
                # Retrieve detected objects
                err = zed.retrieve_objects(objects, obj_runtime_params)
                
                if err == sl.ERROR_CODE.SUCCESS:
                    # Check if we have new detections
                    if objects.is_new:
                        num_objects = len(objects.object_list)
                        
                        if num_objects > 0:
                            print(f"\n--- Frame {frame_count} | Detected {num_objects} object(s) ---")
                            
                            for idx, obj in enumerate(objects.object_list):
                                # Get object properties
                                label = obj.label.name
                                object_id = obj.id
                                confidence = obj.confidence
                                tracking_state = obj.tracking_state.name
                                
                                # Get 3D position
                                position = obj.position
                                distance = math.sqrt(
                                    position[0]**2 + 
                                    position[1]**2 + 
                                    position[2]**2
                                )
                                
                                # Get 2D bounding box center to determine left/right
                                bbox_2d = obj.bounding_box_2d
                                if len(bbox_2d) >= 2:
                                    # Calculate center of bounding box
                                    center_x = (bbox_2d[0][0] + bbox_2d[2][0]) / 2 if len(bbox_2d) >= 3 else bbox_2d[0][0]
                                    
                                    # Determine if object is on left or right side
                                    side = "LEFT" if center_x < frame_center_x else "RIGHT"
                                else:
                                    side = "UNKNOWN"
                                
                                # Check if object is within alert distance
                                is_alert = distance < ALERT_DISTANCE
                                alert_status = "⚠️  ALERT!" if is_alert else "OK"
                                
                                # Print object information
                                print(f"\n  Object #{idx + 1} [ID: {object_id}]")
                                print(f"    Type: {label}")
                                print(f"    Confidence: {confidence:.1f}%")
                                print(f"    Position: ({position[0]:.2f}, {position[1]:.2f}, {position[2]:.2f}) meters")
                                print(f"    Distance: {distance:.2f} meters")
                                print(f"    Side: {side}")
                                print(f"    Tracking: {tracking_state}")
                                print(f"    Status: {alert_status}")
                                
                                # Additional alert for close objects
                                if is_alert:
                                    print(f"    >>> WARNING: {label} is VERY CLOSE on the {side} ({distance:.2f}m) <<<")
                                
                                # Draw bounding box on image
                                if len(bbox_2d) >= 4:
                                    # Color: Red for alerts, Green for safe
                                    color = (0, 0, 255) if is_alert else (0, 255, 0)
                                    thickness = 2 if is_alert else 1
                                    
                                    # Draw rectangle
                                    top_left = (int(bbox_2d[0][0]), int(bbox_2d[0][1]))
                                    bottom_right = (int(bbox_2d[2][0]), int(bbox_2d[2][1]))
                                    cv2.rectangle(image_bgr, top_left, bottom_right, color, thickness)
                                    
                                    # Prepare label text
                                    label_text = f"{label} [{side}]"
                                    distance_text = f"{distance:.2f}m"
                                    if is_alert:
                                        distance_text += " ALERT!"
                                    
                                    # Draw label background (smaller)
                                    label_size, _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
                                    distance_size, _ = cv2.getTextSize(distance_text, cv2.FONT_HERSHEY_SIMPLEX, 0.35, 1)
                                    max_width = max(label_size[0], distance_size[0])
                                    
                                    cv2.rectangle(image_bgr, 
                                                (top_left[0], top_left[1] - 30), 
                                                (top_left[0] + max_width + 8, top_left[1]), 
                                                color, -1)
                                    
                                    # Draw text (smaller fonts)
                                    cv2.putText(image_bgr, label_text, 
                                              (top_left[0] + 4, top_left[1] - 17), 
                                              cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                                    cv2.putText(image_bgr, distance_text, 
                                              (top_left[0] + 4, top_left[1] - 5), 
                                              cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
                
                # Draw info panel on top
                info_bg = image_bgr.copy()
                cv2.rectangle(info_bg, (0, 0), (image_bgr.shape[1], 50), (0, 0, 0), -1)
                image_bgr = cv2.addWeighted(image_bgr, 0.6, info_bg, 0.4, 0)
                
                fps = zed.get_current_fps()
                info_text = f"Frame: {frame_count} | FPS: {fps:.1f} | Objects: {len(objects.object_list)}"
                cv2.putText(image_bgr, info_text, (10, 20), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(image_bgr, "Press 'Q' or ESC to quit", (10, 40), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
                
                # Display the image
                cv2.imshow(window_name, image_bgr)
                
                # Check for key press (1ms wait)
                key = cv2.waitKey(1)
                if key == 27 or key == ord('q') or key == ord('Q'):  # ESC or Q to quit
                    break
                
    except KeyboardInterrupt:
        print("\n\nStopping detection...")
    
    # Cleanup
    print("\nClosing window...")
    cv2.destroyAllWindows()
    
    print("Disabling object detection...")
    zed.disable_object_detection()
    
    print("Disabling positional tracking...")
    zed.disable_positional_tracking()
    
    print("Closing camera...")
    zed.close()
    
    print(f"\nProcessed {frame_count} frames. Goodbye!")

if __name__ == "__main__":
    main()

