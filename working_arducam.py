#!/usr/bin/env python3
"""
Simple Working Arducam Controller
Back to the basic version that was working
"""

import cv2
import time
import threading

class SimpleArducamController:
    def __init__(self, camera_id=1):
        self.camera_id = camera_id
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.capture_thread = None
        
    def connect(self):
        """Connect to camera with working settings"""
        print(f"Connecting to Camera {self.camera_id}...")
        
        # Use MSMF backend (working for your camera)
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_MSMF)
        
        if not self.cap.isOpened():
            print("Failed to open camera")
            return False
        
        # Use working resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Test frame
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to capture test frame")
            self.cap.release()
            return False
        
        print(f"Camera connected: {frame.shape}")
        
        # Focus settings
        print("Configuring focus...")
        
        # Try to disable autofocus (may not work, but that's OK)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        
        # Set manual focus
        self.cap.set(cv2.CAP_PROP_FOCUS, 100)
        
        # Check focus status
        autofocus = self.cap.get(cv2.CAP_PROP_AUTOFOCUS)
        focus = self.cap.get(cv2.CAP_PROP_FOCUS)
        
        print(f"Autofocus status: {autofocus}")
        print(f"Focus value: {focus}")
        
        return True
    
    def start_capture(self):
        """Start frame capture"""
        self.is_running = True
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        print("Started frame capture")
    
    def _capture_loop(self):
        """Capture frames continuously"""
        while self.is_running:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    with self.frame_lock:
                        self.current_frame = frame.copy()
                else:
                    print("Warning: Failed to capture frame")
                    time.sleep(0.01)
            time.sleep(0.001)
    
    def get_frame(self):
        """Get latest frame"""
        with self.frame_lock:
            if self.current_frame is not None:
                return True, self.current_frame.copy()
            return False, None
    
    def set_focus(self, focus_value):
        """Set focus value"""
        if self.cap and self.cap.isOpened():
            # Ensure autofocus is off
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            
            # Set focus
            result = self.cap.set(cv2.CAP_PROP_FOCUS, focus_value)
            
            # Check result
            time.sleep(0.1)
            actual_focus = self.cap.get(cv2.CAP_PROP_FOCUS)
            print(f"Focus set to {focus_value}, actual: {actual_focus}")
            return result
        return False
    
    def stop(self):
        """Stop camera"""
        self.is_running = False
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2.0)
        if self.cap:
            self.cap.release()
        print("Camera stopped")

def main():
    print("Simple Working Arducam Controller")
    print("=" * 40)
    
    controller = SimpleArducamController(camera_id=1)
    
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
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame, "A/D: Focus, Q: Quit", (10, 70),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    cv2.imshow('Arducam Camera - Manual Focus', frame)
                    
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
                    print("No frame available")
                    time.sleep(0.1)
            
            cv2.destroyAllWindows()
        else:
            print("Failed to connect to camera")
    
    finally:
        controller.stop()

if __name__ == "__main__":
    main()
