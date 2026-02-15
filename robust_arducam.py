#!/usr/bin/env python3
"""
Robust Arducam Controller - Handles MSMF errors
Multiple fallback strategies for stable operation
"""

import cv2
import time
import threading

class RobustArducamController:
    def __init__(self, camera_id=1):
        self.camera_id = camera_id
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.capture_thread = None
        
    def connect(self):
        """Connect to camera with multiple fallback strategies"""
        print(f"Connecting to Camera {self.camera_id}...")
        
        # Strategy 1: Try MSMF with 320x240 (most stable)
        print("Trying MSMF backend with 320x240...")
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_MSMF)
        
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Test frame
            ret, frame = self.cap.read()
            if ret and frame is not None:
                print(f"Connected with 320x240: {frame.shape}")
                self._configure_focus()
                return True
            else:
                print("MSMF with 320x240 failed")
                self.cap.release()
        
        # Strategy 2: Try MSMF with 640x480
        print("Trying MSMF backend with 640x480...")
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_MSMF)
        
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Test frame
            ret, frame = self.cap.read()
            if ret and frame is not None:
                print(f"Connected with 640x480: {frame.shape}")
                self._configure_focus()
                return True
            else:
                print("MSMF with 640x480 failed")
                self.cap.release()
        
        # Strategy 3: Try AUTO backend
        print("Trying AUTO backend...")
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_ANY)
        
        if self.cap.isOpened():
            # Try default settings first
            ret, frame = self.cap.read()
            if ret and frame is not None:
                print(f"Connected with AUTO backend: {frame.shape}")
                self._configure_focus()
                return True
            else:
                print("AUTO backend failed")
                self.cap.release()
        
        print("All connection strategies failed")
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
    print("Robust Arducam Controller")
    print("=" * 40)
    
    controller = RobustArducamController(camera_id=1)
    
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
                    
                    # Add info to frame
                    cv2.putText(frame, f"Focus: {current_focus}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Frames: {frame_count}", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, "A/D: Focus, Q: Quit", (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    cv2.imshow('Arducam - Manual Focus', frame)
                    
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
            print("3. Restart the application")
            print("4. Check if camera is being used by another application")
    
    finally:
        controller.stop()

if __name__ == "__main__":
    main()
