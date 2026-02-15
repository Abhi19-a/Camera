#!/usr/bin/env python3
"""
Arducam Camera Properties Tester
Tests and displays available camera properties for Arducam 16MP USB camera
"""

import cv2
import sys
import time

def test_camera_properties(camera_id=0):
    """Test and display all available camera properties"""
    
    print("=== Arducam Camera Properties Test ===")
    print(f"Testing camera ID: {camera_id}")
    print()
    
    # Initialize camera
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        print(f"Error: Cannot open camera {camera_id}")
        return False
    
    # Get camera backend info
    backend_name = cap.getBackendName()
    print(f"Camera Backend: {backend_name}")
    
    # Get basic camera info
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"Default Resolution: {width}x{height}")
    print(f"Default FPS: {fps}")
    print()
    
    # Test focus-related properties
    print("=== FOCUS PROPERTIES ===")
    
    # Auto focus
    autofocus = cap.get(cv2.CAP_PROP_AUTOFOCUS)
    print(f"CAP_PROP_AUTOFOCUS: {autofocus}")
    
    # Focus
    focus = cap.get(cv2.CAP_PROP_FOCUS)
    print(f"CAP_PROP_FOCUS: {focus}")
    
    # Absolute focus
    absolute_focus = cap.get(cv2.CAP_PROP_FOCUS)
    print(f"CAP_PROP_FOCUS (absolute): {absolute_focus}")
    
    print()
    
    # Test other important properties
    print("=== OTHER CAMERA PROPERTIES ===")
    
    properties_to_test = [
        ("Brightness", cv2.CAP_PROP_BRIGHTNESS),
        ("Contrast", cv2.CAP_PROP_CONTRAST),
        ("Saturation", cv2.CAP_PROP_SATURATION),
        ("Hue", cv2.CAP_PROP_HUE),
        ("Gain", cv2.CAP_PROP_GAIN),
        ("Exposure", cv2.CAP_PROP_EXPOSURE),
        ("Auto Exposure", cv2.CAP_PROP_AUTO_EXPOSURE),
        ("Sharpness", cv2.CAP_PROP_SHARPNESS),
        ("Gamma", cv2.CAP_PROP_GAMMA),
        ("Backlight", cv2.CAP_PROP_BACKLIGHT),
        ("Zoom", cv2.CAP_PROP_ZOOM),
        ("Auto Focus", cv2.CAP_PROP_AUTOFOCUS),
        ("Focus", cv2.CAP_PROP_FOCUS),
        ("ISO Speed", cv2.CAP_PROP_ISO_SPEED),
        ("Temperature", cv2.CAP_PROP_TEMPERATURE),
    ]
    
    for prop_name, prop_id in properties_to_test:
        value = cap.get(prop_id)
        if value != -1.0:  # -1.0 usually means property not supported
            print(f"{prop_name}: {value}")
    
    print()
    
    # Test setting autofocus to manual
    print("=== TESTING AUTOFOCUS CONTROL ===")
    
    # Try to disable autofocus
    print("Attempting to disable autofocus...")
    result = cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    print(f"Set autofocus to manual (0): {'Success' if result else 'Failed'}")
    
    # Check if it worked
    time.sleep(0.5)
    current_autofocus = cap.get(cv2.CAP_PROP_AUTOFOCUS)
    print(f"Current autofocus value: {current_autofocus}")
    
    # Test manual focus control
    print("\nTesting manual focus control...")
    
    # Try different focus values
    test_focus_values = [0, 50, 100, 150, 200, 255]
    
    for focus_value in test_focus_values:
        result = cap.set(cv2.CAP_PROP_FOCUS, focus_value)
        current_focus = cap.get(cv2.CAP_PROP_FOCUS)
        print(f"Set focus to {focus_value}: {'Success' if result else 'Failed'}, Current: {current_focus}")
        time.sleep(0.1)
    
    print()
    
    # Test resolution settings
    print("=== TESTING RESOLUTION SETTINGS ===")
    
    resolutions_to_test = [
        (640, 480),
        (1280, 720),
        (1920, 1080),
        (2560, 1440),
        (3840, 2160),
        (4656, 3496),  # 16MP approximate
    ]
    
    for width, height in resolutions_to_test:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        if actual_width == width and actual_height == height:
            print(f"Resolution {width}x{height}: Supported ✓")
        else:
            print(f"Resolution {width}x{height}: Not supported (got {actual_width}x{actual_height})")
    
    print()
    
    # Test frame capture
    print("=== TESTING FRAME CAPTURE ===")
    
    ret, frame = cap.read()
    if ret:
        print(f"Frame capture: Success ✓")
        print(f"Actual frame size: {frame.shape}")
    else:
        print("Frame capture: Failed ✗")
    
    # Cleanup
    cap.release()
    
    return True

def list_available_cameras():
    """List all available cameras"""
    print("=== SCANNING FOR CAMERAS ===")
    
    available_cameras = []
    
    for i in range(10):  # Test first 10 camera indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                available_cameras.append(i)
                print(f"Camera {i}: Available ✓")
            else:
                print(f"Camera {i}: Available but no frame")
            cap.release()
        else:
            print(f"Camera {i}: Not available")
    
    print(f"\nFound {len(available_cameras)} available camera(s): {available_cameras}")
    return available_cameras

if __name__ == "__main__":
    print("Arducam Camera Properties Tester")
    print("=" * 50)
    
    # List available cameras
    cameras = list_available_cameras()
    
    if not cameras:
        print("\nNo cameras found. Please check your camera connection.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # Test each available camera
    for camera_id in cameras:
        print(f"\n{'='*50}")
        print(f"TESTING CAMERA {camera_id}")
        print(f"{'='*50}")
        
        success = test_camera_properties(camera_id)
        
        if not success:
            print(f"Failed to test camera {camera_id}")
        
        print("\nPress Enter to continue to next camera (or 'q' to quit)...")
        user_input = input().strip().lower()
        if user_input == 'q':
            break
    
    print("\nCamera testing complete!")
