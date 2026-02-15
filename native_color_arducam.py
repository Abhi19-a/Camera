#!/usr/bin/env python3
"""
Native Color Arducam Controller - Tries camera's native color modes
Attempts different resolutions and formats to get true color
"""

import cv2
import time
import threading
import numpy as np

class NativeColorArducamController:
    def __init__(self, camera_id=1):
        self.camera_id = camera_id
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.capture_thread = None
        self.current_mode = ""
        
    def connect(self):
        """Try different strategies to get native color"""
        print(f"Connecting to Camera {self.camera_id}...")
        
        # Strategy 1: Try maximum resolution with native color
        strategies = [
            ("4656x3496 (16MP)", 4656, 3496, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')),
            ("3840x2160 (4K)", 3840, 2160, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')),
            ("1920x1080 (FHD)", 1920, 1080, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')),
            ("1280x720 (HD)", 1280, 720, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')),
            ("640x480 (VGA)", 640, 480, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')),
            ("640x480 YUV", 640, 480, cv2.VideoWriter_fourcc('Y', 'U', 'Y', '2')),
            ("320x240", 320, 240, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')),
        ]
        
        for mode_name, width, height, fourcc in strategies:
            print(f"Trying {mode_name}...")
            
            self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_MSMF)
            
            if self.cap.isOpened():
                # Set format first
                self.cap.set(cv2.CAP_PROP_FOURCC, fourcc)
                time.sleep(0.1)
                
                # Set resolution
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                # Wait for settings to apply
                time.sleep(1.0)
                
                # Test multiple frames
                color_frames = 0
                for i in range(5):
                    ret, frame = self.cap.read()
                    if ret and frame is not None:
                        if self._has_true_color(frame):
                            color_frames += 1
                
                if color_frames >= 3:  # At least 3 out of 5 frames have color
                    actual_w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    actual_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    print(f"✓ SUCCESS: {mode_name} - {actual_w}x{actual_h} - TRUE COLOR DETECTED!")
                    self.current_mode = f"{mode_name} ({actual_w}x{actual_h})"
                    self._configure_focus()
                    return True
                else:
                    print(f"  No true color detected")
                    self.cap.release()
            else:
                print(f"  Failed to open camera")
                time.sleep(0.5)
        
        print("No true color mode found. Camera may be grayscale-only.")
        return False
    
    def _has_true_color(self, frame):
        """Check if frame has true color content"""
        if len(frame.shape) != 3 or frame.shape[2] != 3:
            return False
        
        # Sample pixels from different areas
        h, w = frame.shape[:2]
        sample_points = [
            (w//4, h//4), (3*w//4, h//4),  # Top area
            (w//4, 3*h//4), (3*w//4, 3*h//4),  # Bottom area
            (w//2, h//2)  # Center
        ]
        
        color_pixels = 0
        for x, y in sample_points:
            if 0 <= x < w and 0 <= y < h:
                b, g, r = frame[y, x]
                # Check if RGB values are significantly different
                diff_rg = abs(r - g)
                diff_rb = abs(r - b)
                diff_gb = abs(g - b)
                
                # If any channel differs by more than 10, consider it color
                if diff_rg > 10 or diff_rb > 10 or diff_gb > 10:
                    color_pixels += 1
        
        return color_pixels >= 2  # At least 2 sample points show color
    
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
        """Capture frames"""
        while self.is_running:
            try:
                if self.cap and self.cap.isOpened():
                    ret, frame = self.cap.read()
                    if ret and frame is not None:
                        with self.frame_lock:
                            self.current_frame = frame.copy()
                    else:
                        time.sleep(0.01)
                else:
                    break
                    
                time.sleep(0.001)
                
            except Exception as e:
                print(f"Error in capture loop: {e}")
                time.sleep(0.1)
    
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
    print("Native Color Arducam Controller")
    print("=" * 50)
    print("Searching for camera's native color mode...")
    print("This may take a moment...")
    print("=" * 50)
    
    controller = NativeColorArducamController(camera_id=1)
    
    try:
        if controller.connect():
            controller.start_capture()
            
            print(f"\n✓ Connected in mode: {controller.current_mode}")
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
                    
                    # Check color quality
                    has_color = controller._has_true_color(frame)
                    color_text = "TRUE COLOR" if has_color else "NO COLOR"
                    
                    # Add info to frame
                    cv2.putText(frame, f"Mode: {controller.current_mode}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    cv2.putText(frame, f"Focus: {current_focus}", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    cv2.putText(frame, f"Color: {color_text}", (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    cv2.putText(frame, f"Frames: {frame_count}", (10, 120),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    cv2.putText(frame, "A/D: Focus, Q: Quit", (10, 150),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    cv2.imshow('Arducam - Native Color', frame)
                    
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
            print(f"Captured {frame_count} frames successfully")
        else:
            print("\n" + "=" * 50)
            print("COLOR MODE SEARCH COMPLETE")
            print("=" * 50)
            print("❌ No true color mode found")
            print("\nPossible reasons:")
            print("1. Camera only supports grayscale at these resolutions")
            print("2. Camera needs specific drivers for color")
            print("3. Camera color mode disabled in hardware")
            print("4. USB bandwidth limitation at high resolutions")
            print("\nSolutions:")
            print("• Use Arducam's official software to enable color")
            print("• Try USB 3.0 port with high-quality cable")
            print("• Check camera documentation for color settings")
            print("• Some 16MP cameras use color filter arrays that")
            print("  require special processing")
    
    finally:
        controller.stop()

if __name__ == "__main__":
    main()
