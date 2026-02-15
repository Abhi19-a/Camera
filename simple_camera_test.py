#!/usr/bin/env python3
"""
Simple camera test to identify Arducam and check focus properties
"""

import cv2
import sys

def test_camera_simple(camera_id):
    """Simple test for camera focus properties"""
    print(f"\n=== Testing Camera {camera_id} ===")
    
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        print(f"Camera {camera_id}: Cannot open")
        return False
    
    # Get basic info
    backend = cap.getBackendName()
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"Backend: {backend}")
    print(f"Resolution: {width}x{height}")
    
    # Test focus properties
    autofocus = cap.get(cv2.CAP_PROP_AUTOFOCUS)
    focus = cap.get(cv2.CAP_PROP_FOCUS)
    
    print(f"Auto Focus property: {autofocus}")
    print(f"Focus property: {focus}")
    
    # Try to disable autofocus
    print("\nAttempting to disable autofocus...")
    result = cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    print(f"Set autofocus to 0: {'Success' if result else 'Failed'}")
    
    # Check if it worked
    new_autofocus = cap.get(cv2.CAP_PROP_AUTOFOCUS)
    print(f"Auto focus after setting: {new_autofocus}")
    
    # Try to set focus
    print("\nTesting manual focus...")
    test_focus = 100
    result = cap.set(cv2.CAP_PROP_FOCUS, test_focus)
    print(f"Set focus to {test_focus}: {'Success' if result else 'Failed'}")
    
    # Check focus value
    new_focus = cap.get(cv2.CAP_PROP_FOCUS)
    print(f"Focus after setting: {new_focus}")
    
    # Test frame capture
    ret, frame = cap.read()
    if ret:
        print(f"Frame capture: Success ({frame.shape})")
        
        # Show the frame briefly
        cv2.imshow(f'Camera {camera_id} Test', frame)
        print("Showing frame for 3 seconds...")
        cv2.waitKey(3000)
        cv2.destroyAllWindows()
    else:
        print("Frame capture: Failed")
    
    cap.release()
    return True

if __name__ == "__main__":
    print("Simple Camera Test for Arducam")
    print("=" * 40)
    
    # Test both cameras
    for camera_id in [0, 1]:
        test_camera_simple(camera_id)
        
        if camera_id < 1:
            print("\nPress Enter to test next camera...")
            input()
    
    print("\nTest complete!")
