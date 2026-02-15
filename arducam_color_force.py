#!/usr/bin/env python3
"""
Arducam Color Force - Forces color format properly
Uses specific color format settings for Arducam 16MP
"""

import cv2
import time
import threading

class ArducamColorForce:
    def __init__(self, camera_id=1):
        self.camera_id = camera_id
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.capture_thread = None
        
    def connect(self):
        """Connect with forced color format"""
        print(f"Connecting to Arducam Camera {self.camera_id}...")
        print("Forcing color format...")
        
        # Try different backends and formats
        backends_formats = [
            (cv2.CAP_MSMF, cv2.VideoWriter_fourcc('Y', 'U', 'Y', '2')),
            (cv2.CAP_MSMF, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')),
            (cv2.CAP_DSHOW, cv2.VideoWriter_fourcc('Y', 'U', 'Y', '2')),
            (cv2.CAP_DSHOW, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')),
        ]
        
        for backend, fourcc in backends_formats:
            print(f"Trying backend with color format...")
            
            self.cap = cv2.VideoCapture(self.camera_id, backend)
            
            if not self.cap.isOpened():
                continue
            
            # Set color format FIRST
            print(f"Setting color format...")
            self.cap.set(cv2.CAP_PROP_FOURCC, fourcc)
            time.sleep(0.5)  # Wait for format to apply
            
            # Set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Wait for camera to adjust
            time.sleep(2.0)
            
            # Test frame and check for color
            ret, frame = self.cap.read()
            if ret and frame is not None:
                print(f"Frame captured: {frame.shape}")
                
                # Check if it's color
                if self._check_color(frame):
                    print("✓ COLOR DETECTED!")
                    
                    # Enable autofocus
                    self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
                    time.sleep(0.5)
                    
                    autofocus = self.cap.get(cv2.CAP_PROP_AUTOFOCUS)
                    focus = self.cap.get(cv2.CAP_PROP_FOCUS)
                    
                    print(f"Autofocus: {autofocus}")
                    print(f"Focus: {focus}")
                    
                    return True
                else:
                    print("Still grayscale, trying next...")
                    self.cap.release()
            else:
                print("No frame captured")
                self.cap.release()
        
        print("Could not enable color with any method")
        return False
    
    def _check_color(self, frame):
        """Check if frame has actual color"""
        if len(frame.shape) != 3 or frame.shape[2] != 3:
            return False
        
        # Sample multiple pixels
        h, w = frame.shape[:2]
        color_pixels = 0
        
        for y in range(h//4, 3*h//4, h//8):
            for x in range(w//4, 3*w//4, w//8):
                if 0 <= x < w and 0 <= y < h:
                    b, g, r = frame[y, x]
                    
                    # Check for color differences
                    if abs(r-g) > 20 or abs(r-b) > 20 or abs(g-b) > 20:
                        color_pixels += 1
        
        return color_pixels >= 3
    
    def start_capture(self):
        """Start frame capture"""
        self.is_running = True
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        print("Started color capture")
    
    def _capture_loop(self):
        """Capture frames"""
        while self.is_running:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    with self.frame_lock:
                        self.current_frame = frame.copy()
                else:
                    time.sleep(0.01)
            time.sleep(0.001)
    
    def get_frame(self):
        """Get latest frame"""
        with self.frame_lock:
            if self.current_frame is not None:
                return True, self.current_frame.copy()
            return False, None
    
    def stop(self):
        """Stop camera"""
        self.is_running = False
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2.0)
        if self.cap:
            self.cap.release()
        print("Camera stopped")

def main():
    print("Arducam Color Force")
    print("=" * 40)
    print("Forcing color format for Arducam 16MP")
    print("=" * 40)
    
    controller = ArducamColorForce(camera_id=1)
    
    try:
        if controller.connect():
            controller.start_capture()
            
            print("\n🎨 COLOR ENABLED! 🎨")
            print("\nControls:")
            print("Q - Quit")
            
            frame_count = 0
            
            while True:
                ret, frame = controller.get_frame()
                if ret:
                    frame_count += 1
                    
                    # Check color
                    is_color = controller._check_color(frame)
                    color_text = "🎨 COLOR" if is_color else "⚫ GRAY"
                    
                    # Add info to frame
                    cv2.putText(frame, f"Arducam 16MP - {color_text}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Frames: {frame_count}", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, "Q: Quit", (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    cv2.imshow('Arducam 16MP - Color Forced', frame)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                else:
                    print("No frame available")
                    time.sleep(0.1)
            
            cv2.destroyAllWindows()
            print(f"Captured {frame_count} frames")
        else:
            print("\n❌ Color force failed")
            print("\nYour Arducam may need:")
            print("1. Official Arducam software to enable color")
            print("2. Specific drivers for color processing")
            print("3. Hardware settings for color mode")
    
    finally:
        controller.stop()

if __name__ == "__main__":
    main()
