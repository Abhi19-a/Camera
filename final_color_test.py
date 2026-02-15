#!/usr/bin/env python3
"""
Final Color Test - Handles all camera formats properly
"""

import cv2
import time
import numpy as np

def test_all_formats():
    print("Final Arducam Color Test")
    print("=" * 50)
    print("Testing all possible color formats...")
    print("=" * 50)
    
    # Test different approaches
    approaches = [
        ("Default MSMF", lambda cap: None),
        ("MSMF + MJPG", lambda cap: cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))),
        ("MSMF + YUY2", lambda cap: cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y', 'U', 'Y', '2'))),
        ("DSHOW Default", lambda cap: None),
        ("DSHOW + MJPG", lambda cap: cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))),
        ("DSHOW + YUY2", lambda cap: cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y', 'U', 'Y', '2'))),
    ]
    
    for approach_name, setup_func in approaches:
        print(f"\nTrying: {approach_name}")
        
        # Try both backends
        for backend_name, backend in [("MSMF", cv2.CAP_MSMF), ("DSHOW", cv2.CAP_DSHOW)]:
            if approach_name.startswith(backend_name):
                continue  # Skip if backend doesn't match approach
                
            print(f"  Backend: {backend_name}")
            
            cap = cv2.VideoCapture(1, backend)
            
            if not cap.isOpened():
                print(f"    Failed to open camera")
                continue
            
            # Apply setup function
            if setup_func:
                try:
                    setup_func(cap)
                    time.sleep(0.5)
                except:
                    print(f"    Setup failed")
                    cap.release()
                    continue
            
            # Set resolution
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Wait for camera
            time.sleep(1.0)
            
            # Test frames
            color_frames = 0
            total_frames = 0
            
            for i in range(20):  # Test 20 frames
                ret, frame = cap.read()
                if ret and frame is not None:
                    total_frames += 1
                    
                    # Handle different frame formats
                    if len(frame.shape) == 3 and frame.shape[2] == 3:
                        # 3-channel BGR - check for true color
                        h, w = frame.shape[:2]
                        center_pixel = frame[h//2, w//2]
                        b, g, r = center_pixel
                        
                        # Check if it's real color
                        if abs(r-g) > 30 or abs(r-b) > 30 or abs(g-b) > 30:
                            color_frames += 1
                            
                            if i == 0:
                                print(f"    ✅ 3-channel color detected!")
                                print(f"    Center pixel RGB: [{b} {g} {r}]")
                    
                    elif len(frame.shape) == 2:
                        # Grayscale - convert to BGR for display
                        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                        total_frames += 1
                        
                        if i == 0:
                            print(f"    ⚫ 2-channel grayscale detected")
                            print(f"    Frame shape: {frame.shape}")
                    
                    # Show frame
                    try:
                        cv2.imshow(f'Camera Test - {approach_name}', frame_bgr if len(frame.shape) == 2 else frame)
                        
                        if cv2.waitKey(50) & 0xFF == ord('q'):
                            break
                    except:
                        pass  # Ignore display errors
                
                time.sleep(0.05)
            
            cap.release()
            cv2.destroyAllWindows()
            
            # Results
            if total_frames > 0:
                color_ratio = color_frames / total_frames
                print(f"    Results: {color_frames}/{total_frames} frames with color ({color_ratio:.1%})")
                
                if color_ratio > 0:
                    print(f"    ✅ SUCCESS: {approach_name} + {backend_name} shows color!")
                    print(f"    Your camera is working in color mode!")
                    print(f"    Use this approach for your projects!")
                    return True
            
            time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print("FINAL RESULT:")
    print("=" * 50)
    print("❌ No approach produced true color")
    print("\nYour camera may need:")
    print("1. Arducam's official software to enable color")
    print("2. Hardware color mode switch")
    print("3. Different USB cable or port")
    print("4. Camera firmware update")
    
    return False

def main():
    success = test_all_formats()
    
    if success:
        print("\n🎨 COLOR ENABLED! 🎨")
        print("Your Arducam is ready for color video!")
    else:
        print("\n⚫ GRAYSCALE ONLY")
        print("Camera works perfectly, but in grayscale mode")

if __name__ == "__main__":
    main()
