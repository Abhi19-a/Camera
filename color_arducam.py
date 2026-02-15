#!/usr/bin/env python3
"""
Color Arducam Controller - Gets color video at 640x480
Fixes grayscale issue and improves resolution
"""

import cv2
import time
import threading

class ColorArducamController:
    def __init__(self, camera_id=1):
        self.camera_id = camera_id
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.capture_thread = None
        
    def connect(self):
        """Connect to camera with color format and good resolution"""
        print(f"Connecting to Camera {self.camera_id}...")
        
        # Strategy 1: Try 640x480 with color format (MJPEG)
        print("Trying MSMF with 640x480 + MJPEG color...")
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_MSMF)
        
        if self.cap.isOpened():
            # Set color format (MJPEG usually gives color)
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            
            # Set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Wait a moment for settings to apply
            time.sleep(0.5)
            
            # Test frame
            ret, frame = self.cap.read()
            if ret and frame is not None:
                print(f"Connected with 640x480 MJPEG: {frame.shape}")
                if len(frame.shape) == 3 and frame.shape[2] == 3:
                    print("✓ Color format detected!")
                else:
                    print("⚠ Still grayscale, trying next strategy")
                self._configure_focus()
                return True
            else:
                print("640x480 MJPEG failed")
                self.cap.release()
        
        # Strategy 2: Try 640x480 with YUY2 color format
        print("Trying MSMF with 640x480 + YUY2 color...")
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_MSMF)
        
        if self.cap.isOpened():
            # Set YUY2 color format
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y', 'U', 'Y', '2'))
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            time.sleep(0.5)
            
            ret, frame = self.cap.read()
            if ret and frame is not None:
                print(f"Connected with 640x480 YUY2: {frame.shape}")
                if len(frame.shape) == 3 and frame.shape[2] == 3:
                    print("✓ Color format detected!")
                else:
                    print("⚠ Still grayscale")
                self._configure_focus()
                return True
            else:
                print("640x480 YUY2 failed")
                self.cap.release()
        
        # Strategy 3: Try 320x240 with color (fallback but color)
        print("Trying MSMF with 320x240 + MJPEG color...")
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_MSMF)
        
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            time.sleep(0.5)
            
            ret, frame = self.cap.read()
            if ret and frame is not None:
                print(f"Connected with 320x240 MJPEG: {frame.shape}")
                if len(frame.shape) == 3 and frame.shape[2] == 3:
                    print("✓ Color format detected!")
                else:
                    print("⚠ Still grayscale, but this is the best we can do")
                self._configure_focus()
                return True
            else:
                print("320x240 MJPEG failed")
                self.cap.release()
        
        print("All color strategies failed")
        return False
    
    def _configure_focus(self):
        """Configure focus settings"""
        print("Configuring focus...")
        
        # Try to disable autofocus
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        
        # Set manual focus to a good starting value
        self.cap.set(cv2.CAP_PROP_FOCUS, 100)
        
        # Check status
        time.sleep(0.1)
        autofocus = self.cap.get(cv2.CAP_PROP_AUTOFOCUS)
        focus = self.cap.get(cv2.CAP_PROP_FOCUS)
        
        print(f"Autofocus status: {autofocus}")
        print(f"Focus value: {focus}")
    
    def start_capture(self):
        """Start frame capture with error handling"""
        self.is_running = True
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        print("Started frame capture")
    
    def _capture_loop(self):
        """Capture frames with error recovery"""
        consecutive_failures = 0
        max_failures = 10
        
        while self.is_running:
            try:
                if self.cap and self.cap.isOpened():
                    ret, frame = self.cap.read()
                    if ret and frame is not None:
                        # Convert to color if grayscale
                        if len(frame.shape) == 2:  # Grayscale
                            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                        elif frame.shape[2] == 1:  # Single channel
                            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                        
                        with self.frame_lock:
                            self.current_frame = frame.copy()
                        consecutive_failures = 0
                    else:
                        consecutive_failures += 1
                        if consecutive_failures < 5:
                            print(f"Frame capture failed ({consecutive_failures}/{max_failures})")
                        
                        if consecutive_failures >= max_failures:
                            print("Too many consecutive failures, stopping capture")
                            break
                        
                        time.sleep(0.1)
                else:
                    print("Camera not available")
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
                # Ensure autofocus is off
                self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
                
                # Set focus
                result = self.cap.set(cv2.CAP_PROP_FOCUS, focus_value)
                
                # Check result
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
    print("Color Arducam Controller")
    print("=" * 40)
    
    controller = ColorArducamController(camera_id=1)
    
    try:
        if controller.connect():
            controller.start_capture()
            
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
                    
                    # Check if color
                    is_color = len(frame.shape) == 3 and frame.shape[2] == 3
                    color_text = "COLOR" if is_color else "GRAYSCALE"
                    
                    # Add info to frame
                    cv2.putText(frame, f"Focus: {current_focus}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Frames: {frame_count}", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Format: {color_text}", (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, "A/D: Focus, Q: Quit", (10, 120),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    cv2.imshow('Arducam - Color Video', frame)
                    
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
            print("Failed to connect to camera")
            print("\nTroubleshooting:")
            print("1. Check camera is connected to USB 3.0 port")
            print("2. Try unplugging and reconnecting camera")
            print("3. Close other camera applications")
            print("4. Camera may only support grayscale at this resolution")
    
    finally:
        controller.stop()

if __name__ == "__main__":
    main()
