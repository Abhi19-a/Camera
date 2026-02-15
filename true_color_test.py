#!/usr/bin/env python3
"""
True Color Test - Forces actual color format
"""

import cv2
import time
import numpy as np

def test_true_color():
    print("Testing True Color Mode")
    print("=" * 40)
    
    # Try different color formats
    formats = [
        ("MJPEG", cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')),
        ("YUY2", cv2.VideoWriter_fourcc('Y', 'U', 'Y', '2')),
        ("YUYV", cv2.VideoWriter_fourcc('Y', 'U', 'Y', 'V')),
        ("UYVY", cv2.VideoWriter_fourcc('U', 'Y', 'V', 'Y')),
    ]
    
    for format_name, fourcc in formats:
        print(f"\nTrying {format_name} format...")
        
        cap = cv2.VideoCapture(1, cv2.CAP_MSMF)
        
        if not cap.isOpened():
            print("Failed to open camera")
            continue
        
        # Set color format FIRST
        cap.set(cv2.CAP_PROP_FOURCC, fourcc)
        time.sleep(0.5)
        
        # Set resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Wait for camera to adjust
        time.sleep(2.0)
        
        # Test frames
        true_color_frames = 0
        total_frames = 0
        
        for i in range(30):  # Test 30 frames
            ret, frame = cap.read()
            if ret and frame is not None:
                total_frames += 1
                
                # Check for TRUE color (not just variance)
                if len(frame.shape) == 3 and frame.shape[2] == 3:
                    h, w = frame.shape[:2]
                    
                    # Sample multiple points and check for actual color differences
                    color_points = 0
                    sample_points = [
                        (w//4, h//4), (w//2, h//4), (3*w//4, h//4),
                        (w//4, h//2), (w//2, h//2), (3*w//4, h//2),
                        (w//4, 3*h//4), (w//2, 3*h//4), (3*w//4, 3*h//4)
                    ]
                    
                    for x, y in sample_points:
                        if 0 <= x < w and 0 <= y < h:
                            b, g, r = frame[y, x]
                            
                            # Check for significant color differences
                            diff_rg = abs(r - g)
                            diff_rb = abs(r - b)
                            diff_gb = abs(g - b)
                            
                            # Also check that pixel isn't neutral gray
                            max_diff = max(diff_rg, diff_rb, diff_gb)
                            pixel_sum = r + g + b
                            
                            # True color: significant differences + not neutral
                            if max_diff > 25 and 50 < pixel_sum < 650:
                                color_points += 1
                    
                    if color_points >= 3:  # At least 3 points show true color
                        true_color_frames += 1
                        
                        if i == 0:  # Show first frame details
                            print(f"  Frame shape: {frame.shape}")
                            print(f"  Sample center pixel: {frame[h//2, w//2]}")
                            print(f"  Color points detected: {color_points}/9")
                
                # Show the frame
                cv2.imshow(f'True Color Test - {format_name}', frame)
                
                key = cv2.waitKey(100) & 0xFF  # Short delay
                if key == ord('q'):
                    break
            else:
                print("  Failed to capture frame")
                time.sleep(0.1)
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Results for this format
        if total_frames > 0:
            color_ratio = true_color_frames / total_frames
            print(f"  {format_name}: {true_color_frames}/{total_frames} frames with true color ({color_ratio:.1%})")
            
            if color_ratio >= 0.7:
                print(f"  ✅ {format_name} format shows TRUE COLOR!")
                print(f"  Your camera is working in color with {format_name} format!")
                return True
            else:
                print(f"  ❌ {format_name} format still grayscale")
    
    print("\n" + "=" * 40)
    print("TRUE COLOR TEST RESULTS")
    print("=" * 40)
    print("❌ No format showed true color")
    print("\nYour camera may need:")
    print("1. Arducam's official software to enable color")
    print("2. Restart your computer after driver installation")
    print("3. Different USB port (USB 3.0 recommended)")
    print("4. Camera firmware update")
    
    return False

if __name__ == "__main__":
    test_true_color()
