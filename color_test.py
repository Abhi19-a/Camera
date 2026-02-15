#!/usr/bin/env python3
"""
Color Test Script - Test if color is working after driver installation
"""

import cv2
import time
import numpy as np

def test_color():
    print("Testing Arducam Color Mode")
    print("=" * 40)
    
    cap = cv2.VideoCapture(1, cv2.CAP_MSMF)
    
    if not cap.isOpened():
        print("Failed to open camera")
        return
    
    # Set good resolution for color
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print("Testing color output...")
    
    frame_count = 0
    color_frames = 0
    
    while frame_count < 100:  # Test 100 frames
        ret, frame = cap.read()
        if ret and frame is not None:
            frame_count += 1
            
            # Check for color
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                # Sample center area for color
                h, w = frame.shape[:2]
                center_region = frame[h//4:3*h//4, w//4:3*w//4]
                
                # Check color variance
                b_var = np.var(center_region[:, :, 0])
                g_var = np.var(center_region[:, :, 1])
                r_var = np.var(center_region[:, :, 2])
                
                total_var = b_var + g_var + r_var
                
                if total_var > 1000:  # Threshold for color
                    color_frames += 1
                    
                    if frame_count == 1:  # Show first frame info
                        print(f"Frame shape: {frame.shape}")
                        print(f"Color variance: {total_var:.1f}")
                        
                        # Sample center pixel
                        center_pixel = frame[h//2, w//2]
                        print(f"Center pixel RGB: {center_pixel}")
            
            if frame_count % 20 == 0:
                print(f"Tested {frame_count} frames...")
            
            # Show the frame
            cv2.imshow('Color Test - Press Q to quit', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Failed to capture frame")
            time.sleep(0.1)
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Results
    color_ratio = color_frames / frame_count if frame_count > 0 else 0
    
    print("\n" + "=" * 40)
    print("COLOR TEST RESULTS")
    print("=" * 40)
    print(f"Total frames tested: {frame_count}")
    print(f"Color frames detected: {color_frames}")
    print(f"Color ratio: {color_ratio:.1%}")
    
    if color_ratio >= 0.8:
        print("✅ EXCELLENT: Color is working perfectly!")
    elif color_ratio >= 0.5:
        print("✅ GOOD: Color is working mostly")
    elif color_ratio >= 0.2:
        print("⚠️  PARTIAL: Some color detected")
    else:
        print("❌ NO COLOR: Still grayscale")
        print("\nTry restarting your computer and testing again.")
    
    print("=" * 40)

if __name__ == "__main__":
    test_color()