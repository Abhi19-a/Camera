#!/usr/bin/env python3
"""
Original Arducam Controller - Restores factory settings
Back to original autofocus behavior as it was initially
"""

import cv2
import time
import threading

class OriginalArducamController:
    def __init__(self, camera_id=1):
        self.camera_id = camera_id
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.capture_thread = None
        
    def connect(self):
        """Connect to camera with original factory settings"""
        print(f"Connecting to Camera {self.camera_id}...")
        print("Restoring original factory settings with autofocus...")
        
        # Connect with MSMF backend
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_MSMF)
        
        if not self.cap.isOpened():
            print("Failed to open camera")
            return False
        
        # Use original resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Test frame
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to capture test frame")
            self.cap.release()
            return False
        
        print(f"Camera connected: {frame.shape}")
        
        # RESTORE ORIGINAL AUTOFOCUS SETTINGS
        print("Restoring original autofocus settings...")
        
        # Enable autofocus (back to original)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        
        # Don't set manual focus - let camera control it
        # This restores the original autofocus behavior
        
        # Check original settings
        time.sleep(0.5)
        autofocus = self.cap.get(cv2.CAP_PROP_AUTOFOCUS)
        focus = self.cap.get(cv2.CAP_PROP_FOCUS)
        
        print(f"Autofocus status: {autofocus} (1 = ENABLED - Original)")
        print(f"Focus value: {focus} (Camera controlled)")
        
        return True
    
    def start_capture(self):
        """Start frame capture"""
        self.is_running = True
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        print("Started frame capture with original autofocus")
    
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
    
    def get_camera_status(self):
        """Get current camera settings"""
        if self.cap and self.cap.isOpened():
            autofocus = self.cap.get(cv2.CAP_PROP_AUTOFOCUS)
            focus = self.cap.get(cv2.CAP_PROP_FOCUS)
            return autofocus, focus
        return None, None
    
    def stop(self):
        """Stop camera"""
        self.is_running = False
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2.0)
        if self.cap:
            self.cap.release()
        print("Camera stopped")

def main():
    print("Original Arducam Controller - Factory Settings")
    print("=" * 50)
    print("This restores your camera to original autofocus behavior")
    print("Exactly as it was when we first started")
    print("=" * 50)
    
    controller = OriginalArducamController(camera_id=1)
    
    try:
        if controller.connect():
            controller.start_capture()
            
            print("\nCamera Status:")
            print("✓ Autofocus: ENABLED (Original)")
            print("✓ Focus: Camera controlled (Original)")
            print("✓ Resolution: 640x480 (Original)")
            
            print("\nControls:")
            print("Q - Quit")
            print("S - Show current autofocus status")
            
            frame_count = 0
            
            while True:
                ret, frame = controller.get_frame()
                if ret:
                    frame_count += 1
                    
                    # Get current status
                    autofocus, focus = controller.get_camera_status()
                    af_status = "AUTO ON" if autofocus == 1 else "AUTO OFF"
                    
                    # Add info to frame
                    cv2.putText(frame, f"Arducam 16MP - Original", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Autofocus: {af_status}", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Focus: {focus:.0f} (Auto)", (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Frames: {frame_count}", (10, 120),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, "Q: Quit, S: Status", (10, 150),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    cv2.imshow('Arducam - Original Factory Settings', frame)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key == ord('s'):
                        print(f"\nCurrent Status:")
                        print(f"Autofocus: {autofocus} ({'ENABLED' if autofocus == 1 else 'DISABLED'})")
                        print(f"Focus: {focus}")
                        print(f"This is the original camera behavior")
                else:
                    print("No frame available")
                    time.sleep(0.1)
            
            cv2.destroyAllWindows()
            print(f"\nCaptured {frame_count} frames with original autofocus")
        else:
            print("Failed to connect to camera")
    
    finally:
        controller.stop()

if __name__ == "__main__":
    main()
