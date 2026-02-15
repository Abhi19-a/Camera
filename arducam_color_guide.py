#!/usr/bin/env python3
"""
Arducam Color Setup Guide
Helps you enable color mode for Arducam 16MP camera
"""

import cv2
import time

def show_color_setup_guide():
    print("=" * 60)
    print("ARDUCAM 16MP COLOR ENABLE GUIDE")
    print("=" * 60)
    print()
    print("Your Arducam 16MP is definitely a color camera!")
    print("But it needs proper setup to enable color mode.")
    print()
    print("METHOD 1: ARDUCAM OFFICIAL SOFTWARE (Recommended)")
    print("-" * 50)
    print("1. Download Arducam's official software:")
    print("   https://www.arducam.com/arducam-usb-camera-shield-software/")
    print()
    print("2. Install the Arducam USB Camera Shield software")
    print()
    print("3. In the software:")
    print("   - Select your camera")
    print("   - Go to 'Color Settings' or 'Image Settings'")
    print("   - Enable 'Color Mode' (not grayscale)")
    print("   - Set format to YUY2 or MJPG")
    print("   - Click 'Apply' or 'Save Settings'")
    print()
    print("4. After setting color mode in Arducam software,")
    print("   run this Python script again to test.")
    print()
    print("METHOD 2: WINDOWS CAMERA SETTINGS")
    print("-" * 50)
    print("1. Open Windows Camera app")
    print("2. Go to Settings (gear icon)")
    print("3. Look for 'Pro mode' or 'Advanced settings'")
    print("4. Enable color mode if available")
    print()
    print("METHOD 3: DEVICE MANAGER")
    print("-" * 50)
    print("1. Open Device Manager")
    print("2. Find your Arducam under 'Cameras'")
    print("3. Right-click → Properties")
    print("4. Look for color/grayscale settings")
    print()
    print("METHOD 4: HARDWARE CHECK")
    print("-" * 50)
    print("Some Arducam cameras have:")
    print("- Jumper settings for color/grayscale")
    print("- Switches for color mode")
    print("- Firmware settings for color")
    print()
    print("Check your camera's manual for color mode settings.")
    print()
    print("=" * 60)
    print("AFTER ENABLING COLOR:")
    print("=" * 60)
    print("Once you enable color mode using any method above,")
    print("run this test script to verify:")
    print()
    print("python color_test.py")
    print()
    print("This will check if color is working and show you")
    print("the best settings for your camera.")
    print()

def create_color_test():
    """Create a simple color test script"""
    color_test_code = '''#!/usr/bin/env python3
"""
Color Test Script - Test if color is working after setup
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
    
    print("\\n" + "=" * 40)
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
        print("\\nTry the color setup methods again.")
    
    print("=" * 40)

if __name__ == "__main__":
    test_color()
'''
    
    with open('color_test.py', 'w') as f:
        f.write(color_test_code)
    
    print("✅ Created color_test.py for testing after setup")

def main():
    show_color_setup_guide()
    create_color_test()
    
    print("\n" + "=" * 60)
    print("QUICK TEST CURRENT CAMERA:")
    print("=" * 60)
    
    # Quick test to show current status
    cap = cv2.VideoCapture(1, cv2.CAP_MSMF)
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            print(f"Current resolution: {frame.shape}")
            
            # Check if it's really color
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                h, w = frame.shape[:2]
                center_pixel = frame[h//2, w//2]
                print(f"Center pixel RGB: {center_pixel}")
                
                # Check if all channels are identical (grayscale)
                b, g, r = center_pixel
                if abs(r-g) < 5 and abs(r-b) < 5 and abs(g-b) < 5:
                    print("❌ Current status: Grayscale (all channels identical)")
                else:
                    print("✅ Current status: Color detected!")
            else:
                print("❌ Current status: Not 3-channel")
        else:
            print("❌ Cannot capture frame")
        
        cap.release()
    else:
        print("❌ Cannot open camera")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. Follow the setup guide above")
    print("2. Enable color mode using Arducam software")
    print("3. Test with: python color_test.py")
    print("4. Your camera will show beautiful color! 🎨")

if __name__ == "__main__":
    main()
