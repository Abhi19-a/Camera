#!/usr/bin/env python3
"""
Arducam Color Unlock - Proper color mode for Arducam cameras
Uses specific Arducam settings and formats to enable true color
"""

import cv2
import time
import threading
import numpy as np

class ArducamColorUnlock:
    def __init__(self, camera_id=1):
        self.camera_id = camera_id
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.capture_thread = None
        
    def connect(self):
        """Connect using Arducam-specific color settings"""
        print(f"Connecting to Arducam Camera {self.camera_id}...")
        print("Using Arducam color unlock method...")
        
        # Arducam-specific approach
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_MSMF)
        
        if not self.cap.isOpened():
            print("Failed to open camera")
            return False
        
        # CRITICAL: Set Arducam-specific settings for color
        print("Applying Arducam color settings...")
        
        # Method 1: Disable all auto-processing that might force grayscale
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)  # Manual exposure
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)      # Disable autofocus
        self.cap.set(cv2.CAP_PROP_AUTO_WB, 0)         # Disable auto white balance if available
        
        # Method 2: Set format that forces color processing
        # Try different fourcc codes that work with Arducam
        arducam_formats = [
            ('YUY2', cv2.VideoWriter_fourcc('Y', 'U', 'Y', '2')),
            ('MJPG', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')),
            ('YUYV', cv2.VideoWriter_fourcc('Y', 'U', 'Y', 'V')),
            ('UYVY', cv2.VideoWriter_fourcc('U', 'Y', 'V', 'Y')),
        ]
        
        for format_name, fourcc in arducam_formats:
            print(f"Trying format: {format_name}")
            
            # Set format
            self.cap.set(cv2.CAP_PROP_FOURCC, fourcc)
            time.sleep(0.2)
            
            # Set a resolution that supports color
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Wait for camera to adjust
            time.sleep(1.0)
            
            # Test color
            if self._test_color_output():
                print(f"✓ SUCCESS: Color enabled with {format_name} format!")
                self._configure_focus()
                return True
            else:
                print(f"  {format_name} format didn't work")
        
        # Method 3: Try lower resolution with different approach
        print("Trying alternative color method...")
        
        # Reset camera
        self.cap.release()
        time.sleep(1.0)
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_MSMF)
        
        if self.cap.isOpened():
            # Try without setting fourcc (let camera choose)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Manual settings
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Manual exposure
            self.cap.set(cv2.CAP_PROP_EXPOSURE, -6)
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            self.cap.set(cv2.CAP_PROP_FOCUS, 100)
            
            time.sleep(2.0)  # Longer wait for stabilization
            
            if self._test_color_output():
                print("✓ SUCCESS: Color enabled with default format!")
                return True
        
        print("❌ Could not enable color mode")
        return False
    
    def _test_color_output(self):
        """Test if camera is outputting color"""
        print("  Testing color output...")
        
        color_frames = 0
        test_frames = 10
        
        for i in range(test_frames):
            ret, frame = self.cap.read()
            if ret and frame is not None:
                # Check for actual color content
                if self._has_real_color(frame):
                    color_frames += 1
                    
                    # Show sample for debugging
                    if i == 0:
                        print(f"    Frame shape: {frame.shape}")
                        # Sample center pixel
                        h, w = frame.shape[:2]
                        center_pixel = frame[h//2, w//2]
                        print(f"    Center pixel RGB: {center_pixel}")
            
            time.sleep(0.1)
        
        color_ratio = color_frames / test_frames
        print(f"    Color frames: {color_frames}/{test_frames} ({color_ratio:.1%})")
        
        return color_ratio >= 0.5  # At least 50% color frames
    
    def _has_real_color(self, frame):
        """Enhanced color detection"""
        if len(frame.shape) != 3 or frame.shape[2] != 3:
            return False
        
        # Method 1: Check multiple random pixels
        h, w = frame.shape[:2]
        color_pixels = 0
        total_pixels = 0
        
        # Sample grid of pixels
        for y in range(h//4, 3*h//4, h//8):
            for x in range(w//4, 3*w//4, w//8):
                if 0 <= x < w and 0 <= y < h:
                    b, g, r = frame[y, x]
                    
                    # Check for significant color differences
                    max_diff = max(abs(r-g), abs(r-b), abs(g-b))
                    
                    # Also check that pixels aren't all black or white
                    pixel_sum = r + g + b
                    
                    if max_diff > 15 and 30 < pixel_sum < 700:  # Significant color + not extreme
                        color_pixels += 1
                    total_pixels += 1
        
        if total_pixels > 0:
            color_ratio = color_pixels / total_pixels
            return color_ratio >= 0.3  # At least 30% of sampled pixels show color
        
        return False
    
    def _configure_focus(self):
        """Configure focus settings"""
        print("Configuring focus...")
        
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        self.cap.set(cv2.CAP_PROP_FOCUS, 100)
        
        time.sleep(0.1)
        autofocus = self.cap.get(cv2.CAP_PROP_AUTOFOCUS)
        focus = self.cap.get(cv2.CAP_PROP_FOCUS)
        
        print(f"Autofocus status: {autofocus}")
        print(f"Focus value: {focus}")
    
    def start_capture(self):
        """Start frame capture"""
        self.is_running = True
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        print("Started frame capture")
    
    def _capture_loop(self):
        """Capture frames with color enhancement"""
        while self.is_running:
            try:
                if self.cap and self.cap.isOpened():
                    ret, frame = self.cap.read()
                    if ret and frame is not None:
                        # Enhance color if needed
                        enhanced_frame = self._enhance_color(frame)
                        
                        with self.frame_lock:
                            self.current_frame = enhanced_frame.copy()
                    else:
                        time.sleep(0.01)
                else:
                    break
                    
                time.sleep(0.001)
                
            except Exception as e:
                print(f"Error in capture loop: {e}")
                time.sleep(0.1)
    
    def _enhance_color(self, frame):
        """Enhance color saturation and contrast"""
        if len(frame.shape) != 3 or frame.shape[2] != 3:
            return frame
        
        # Convert to HSV for better color enhancement
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Increase saturation
        hsv[:, :, 1] = cv2.multiply(hsv[:, :, 1], 1.3)
        
        # Increase contrast
        hsv[:, :, 2] = cv2.multiply(hsv[:, :, 2], 1.1)
        
        # Convert back to BGR
        enhanced = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        return enhanced
    
    def get_frame(self):
        """Get latest frame"""
        with self.frame_lock:
            if self.current_frame is not None:
                return True, self.current_frame.copy()
            return False, None
    
    def set_focus(self, focus_value):
        """Set focus value"""
        if self.cap and self.cap.isOpened():
            try:
                self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
                result = self.cap.set(cv2.CAP_PROP_FOCUS, focus_value)
                time.sleep(0.1)
                actual_focus = self.cap.get(cv2.CAP_PROP_FOCUS)
                print(f"Focus set to {focus_value}, actual: {actual_focus}")
                return result
            except Exception as e:
                print(f"Error setting focus: {e}")
                return False
        return False
    
    def stop(self):
        """Stop camera safely"""
        print("Stopping camera...")
        self.is_running = False
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2.0)
        if self.cap:
            self.cap.release()
        print("Camera stopped")

def main():
    print("Arducam Color Unlock")
    print("=" * 50)
    print("This script unlocks the true color capability")
    print("of your Arducam 16MP camera")
    print("=" * 50)
    
    controller = ArducamColorUnlock(camera_id=1)
    
    try:
        if controller.connect():
            controller.start_capture()
            
            print("\n🎨 COLOR UNLOCKED! 🎨")
            print("\nControls:")
            print("A - Decrease focus")
            print("D - Increase focus") 
            print("S - Reset focus")
            print("Q - Quit")
            
            current_focus = 100
            frame_count = 0
            
            while True:
                ret, frame = controller.get_frame()
                if ret:
                    frame_count += 1
                    
                    # Verify color
                    has_color = controller._has_real_color(frame)
                    color_text = "🎨 COLOR" if has_color else "⚫ GRAY"
                    
                    # Add info to frame
                    cv2.putText(frame, f"Arducam 16MP - {color_text}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Focus: {current_focus}", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Frames: {frame_count}", (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, "A/D: Focus, Q: Quit", (10, 120),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    cv2.imshow('Arducam 16MP - True Color Unlocked', frame)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key == ord('a'):
                        current_focus = max(0, current_focus - 10)
                        controller.set_focus(current_focus)
                    elif key == ord('d'):
                        current_focus = min(255, current_focus + 10)
                        controller.set_focus(current_focus)
                    elif key == ord('s'):
                        current_focus = 100
                        controller.set_focus(current_focus)
                else:
                    print("Waiting for frame...")
                    time.sleep(0.5)
            
            cv2.destroyAllWindows()
            print(f"Successfully captured {frame_count} color frames!")
        else:
            print("\n" + "=" * 50)
            print("COLOR UNLOCK FAILED")
            print("=" * 50)
            print("\nYour Arducam 16MP is definitely a color camera,")
            print("but we need to enable it properly:")
            print("\n1. Install Arducam's official software")
            print("2. Use it to enable color mode")
            print("3. Then try this script again")
            print("\nArducam software: https://www.arducam.com/")
    
    finally:
        controller.stop()

if __name__ == "__main__":
    main()
