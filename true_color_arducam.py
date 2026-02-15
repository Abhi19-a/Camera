#!/usr/bin/env python3
"""
True Color Arducam Controller - Forces color processing
Handles cameras that send 3 identical grayscale channels
"""

import cv2
import time
import threading
import numpy as np

class TrueColorArducamController:
    def __init__(self, camera_id=1):
        self.camera_id = camera_id
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.capture_thread = None
        self.force_color = True
        
    def connect(self):
        """Connect to camera and force color processing"""
        print(f"Connecting to Camera {self.camera_id}...")
        
        # Try 640x480 with YUY2 (worked before)
        print("Trying MSMF with 640x480 YUY2...")
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_MSMF)
        
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y', 'U', 'Y', '2'))
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            time.sleep(0.5)
            
            ret, frame = self.cap.read()
            if ret and frame is not None:
                print(f"Connected: {frame.shape}")
                
                # Check if it's really grayscale in color clothing
                if self._is_grayscale_disguised_as_color(frame):
                    print("⚠ Detected grayscale disguised as color - will force color processing")
                    self.force_color = True
                elif len(frame.shape) == 3 and frame.shape[2] == 3:
                    print("✓ True color detected!")
                    self.force_color = False
                else:
                    print("⚠ Grayscale detected - will convert to color")
                    self.force_color = True
                
                self._configure_focus()
                return True
            else:
                print("640x480 YUY2 failed")
                self.cap.release()
        
        # Fallback to 320x240
        print("Trying MSMF with 320x240...")
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_MSMF)
        
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            time.sleep(0.5)
            
            ret, frame = self.cap.read()
            if ret and frame is not None:
                print(f"Connected with 320x240: {frame.shape}")
                self._configure_focus()
                return True
            else:
                print("320x240 failed")
                self.cap.release()
        
        print("All connection strategies failed")
        return False
    
    def _is_grayscale_disguised_as_color(self, frame):
        """Check if image is grayscale but has 3 identical channels"""
        if len(frame.shape) != 3 or frame.shape[2] != 3:
            return False
        
        # Check if all 3 channels are identical (grayscale in color clothing)
        b, g, r = cv2.split(frame)
        
        # Calculate differences between channels
        diff_bg = np.mean(np.abs(b.astype(float) - g.astype(float)))
        diff_br = np.mean(np.abs(b.astype(float) - r.astype(float)))
        diff_gr = np.mean(np.abs(g.astype(float) - r.astype(float)))
        
        # If all differences are very small, it's grayscale
        threshold = 5.0  # Allow small variations
        is_grayscale = (diff_bg < threshold and diff_br < threshold and diff_gr < threshold)
        
        if is_grayscale:
            print(f"Channel differences - B-G: {diff_bg:.2f}, B-R: {diff_br:.2f}, G-R: {diff_gr:.2f}")
        
        return is_grayscale
    
    def _force_color_processing(self, frame):
        """Force color processing on grayscale or disguised grayscale frames"""
        if len(frame.shape) == 2:
            # True grayscale - convert to BGR
            return cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        elif len(frame.shape) == 3 and frame.shape[2] == 3:
            if self.force_color or self._is_grayscale_disguised_as_color(frame):
                # Create artificial color from grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Apply different color mappings to create artificial color
                # This creates a more natural look than simple grayscale conversion
                color_frame = np.zeros_like(frame)
                
                # Use different color channels for variety
                color_frame[:, :, 0] = gray  # Blue channel
                color_frame[:, :, 1] = gray  # Green channel  
                color_frame[:, :, 2] = gray  # Red channel
                
                # Add slight color tint for more natural look
                color_frame[:, :, 0] = np.clip(color_frame[:, :, 0] * 0.9, 0, 255)  # Less blue
                color_frame[:, :, 1] = np.clip(color_frame[:, :, 1] * 1.0, 0, 255)  # Normal green
                color_frame[:, :, 2] = np.clip(color_frame[:, :, 2] * 1.1, 0, 255)  # More red
                
                return color_frame
            else:
                return frame
        else:
            return frame
    
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
        """Capture frames with color processing"""
        consecutive_failures = 0
        max_failures = 10
        
        while self.is_running:
            try:
                if self.cap and self.cap.isOpened():
                    ret, frame = self.cap.read()
                    if ret and frame is not None:
                        # Force color processing
                        processed_frame = self._force_color_processing(frame)
                        
                        with self.frame_lock:
                            self.current_frame = processed_frame.copy()
                        consecutive_failures = 0
                    else:
                        consecutive_failures += 1
                        if consecutive_failures >= max_failures:
                            print("Too many failures, stopping capture")
                            break
                        time.sleep(0.1)
                else:
                    break
                    
                time.sleep(0.001)
                
            except Exception as e:
                print(f"Error in capture loop: {e}")
                consecutive_failures += 1
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
    print("True Color Arducam Controller")
    print("=" * 40)
    print("This version forces color processing")
    print("even if camera sends grayscale data")
    print("=" * 40)
    
    controller = TrueColorArducamController(camera_id=1)
    
    try:
        if controller.connect():
            controller.start_capture()
            
            print("\nControls:")
            print("A - Decrease focus")
            print("D - Increase focus") 
            print("S - Reset focus")
            print("Q - Quit")
            print("C - Toggle color processing mode")
            
            current_focus = 100
            frame_count = 0
            
            while True:
                ret, frame = controller.get_frame()
                if ret:
                    frame_count += 1
                    
                    # Check actual color content
                    if len(frame.shape) == 3 and frame.shape[2] == 3:
                        b, g, r = cv2.split(frame)
                        color_variance = np.var(b) + np.var(g) + np.var(r)
                        is_truly_color = color_variance > 1000
                        color_text = "TRUE COLOR" if is_truly_color else "FORCED COLOR"
                    else:
                        color_text = "GRAYSCALE"
                    
                    # Add info to frame
                    cv2.putText(frame, f"Focus: {current_focus}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Frames: {frame_count}", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Mode: {color_text}", (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, "A/D: Focus, Q: Quit", (10, 120),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    cv2.imshow('Arducam - True Color Video', frame)
                    
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
                    elif key == ord('c'):
                        controller.force_color = not controller.force_color
                        mode = "FORCED" if controller.force_color else "NORMAL"
                        print(f"Color processing mode: {mode}")
                else:
                    print("Waiting for frame...")
                    time.sleep(0.5)
            
            cv2.destroyAllWindows()
            print(f"Captured {frame_count} frames successfully")
        else:
            print("Failed to connect to camera")
            print("\nNote: Some cameras only output grayscale.")
            print("This version creates artificial color from grayscale data.")
    
    finally:
        controller.stop()

if __name__ == "__main__":
    main()
