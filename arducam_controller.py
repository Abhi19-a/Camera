#!/usr/bin/env python3
"""
Arducam Camera Controller with Manual Focus
Production-ready camera control for Arducam 16MP USB autofocus camera
Disables hardware autofocus and enables manual focus control
"""

import cv2
import yaml
import time
import logging
import threading
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class CameraConfig:
    """Camera configuration data class"""
    device_id: int = 0
    width: int = 1920
    height: int = 1080
    fps: int = 30
    auto_focus: bool = False
    manual_focus: int = 100
    focus_lock: bool = True
    brightness: int = 0
    contrast: int = 0
    saturation: int = 0
    sharpness: int = 0
    gamma: int = 0
    auto_exposure: int = 1
    exposure: int = -6
    auto_wb: int = 1
    white_balance: int = 4000
    buffer_size: int = 1
    connection_timeout: float = 5.0
    frame_timeout: float = 1.0
    max_retries: int = 3
    retry_delay: float = 1.0
    prefer_dshow: bool = True

class ArducamController:
    """
    Arducam 16MP USB Camera Controller
    Provides manual focus control and stable video capture
    """
    
    def __init__(self, config_path: str = "camera_config.yaml"):
        """Initialize camera controller with configuration"""
        self.config = self._load_config(config_path)
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.capture_thread: Optional[threading.Thread] = None
        
        # Camera property constants
        self.PROPERTIES = {
            'auto_focus': cv2.CAP_PROP_AUTOFOCUS,
            'focus': cv2.CAP_PROP_FOCUS,
            'brightness': cv2.CAP_PROP_BRIGHTNESS,
            'contrast': cv2.CAP_PROP_CONTRAST,
            'saturation': cv2.CAP_PROP_SATURATION,
            'sharpness': cv2.CAP_PROP_SHARPNESS,
            'gamma': cv2.CAP_PROP_GAMMA,
            'auto_exposure': cv2.CAP_PROP_AUTO_EXPOSURE,
            'exposure': cv2.CAP_PROP_EXPOSURE,
        }
        
    def _load_config(self, config_path: str) -> CameraConfig:
        """Load configuration from YAML file"""
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                # Extract camera settings
                camera_config = config_data.get('camera', {})
                resolution_config = config_data.get('resolution', {})
                focus_config = config_data.get('focus', {})
                image_config = config_data.get('image', {})
                advanced_config = config_data.get('advanced', {})
                windows_config = config_data.get('windows', {})
                
                return CameraConfig(
                    device_id=camera_config.get('device_id', 0),
                    width=resolution_config.get('width', 1920),
                    height=resolution_config.get('height', 1080),
                    fps=resolution_config.get('fps', 30),
                    auto_focus=focus_config.get('auto_focus', False),
                    manual_focus=focus_config.get('manual_focus', 100),
                    focus_lock=focus_config.get('focus_lock', True),
                    brightness=image_config.get('brightness', 0),
                    contrast=image_config.get('contrast', 0),
                    saturation=image_config.get('saturation', 0),
                    sharpness=image_config.get('sharpness', 0),
                    gamma=image_config.get('gamma', 0),
                    auto_exposure=image_config.get('auto_exposure', 1),
                    exposure=image_config.get('exposure', -6),
                    auto_wb=image_config.get('auto_wb', 1),
                    white_balance=image_config.get('white_balance', 4000),
                    buffer_size=advanced_config.get('buffer_size', 1),
                    connection_timeout=advanced_config.get('connection_timeout', 5.0),
                    frame_timeout=advanced_config.get('frame_timeout', 1.0),
                    max_retries=advanced_config.get('max_retries', 3),
                    retry_delay=advanced_config.get('retry_delay', 1.0),
                    prefer_dshow=windows_config.get('prefer_dshow', True),
                )
            else:
                logger.warning(f"Config file {config_path} not found, using defaults")
                return CameraConfig()
                
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return CameraConfig()
    
    def connect(self) -> bool:
        """Connect to camera with retry logic"""
        for attempt in range(self.config.max_retries):
            try:
                logger.info(f"Connecting to camera (attempt {attempt + 1}/{self.config.max_retries})")
                
                # Try different backends on Windows
                backends_to_try = []
                if self.config.prefer_dshow:
                    backends_to_try.extend([cv2.CAP_DSHOW, cv2.CAP_MSMF])
                else:
                    backends_to_try.extend([cv2.CAP_MSMF, cv2.CAP_DSHOW])
                backends_to_try.append(cv2.CAP_ANY)
                
                for backend in backends_to_try:
                    try:
                        self.cap = cv2.VideoCapture(self.config.device_id, backend)
                        
                        if self.cap.isOpened():
                            logger.info(f"Connected with backend: {self.cap.getBackendName()}")
                            break
                        else:
                            self.cap.release()
                            
                    except Exception as e:
                        logger.debug(f"Backend {backend} failed: {e}")
                        continue
                
                if self.cap is None or not self.cap.isOpened():
                    logger.error("Failed to open camera with any backend")
                    continue
                
                # Configure camera settings
                if self._configure_camera():
                    logger.info("Camera configured successfully")
                    return True
                else:
                    logger.error("Failed to configure camera")
                    self.disconnect()
                    
            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                if self.cap:
                    self.cap.release()
                    self.cap = None
            
            if attempt < self.config.max_retries - 1:
                time.sleep(self.config.retry_delay)
        
        logger.error("Failed to connect to camera after all retries")
        return False
    
    def _configure_camera(self) -> bool:
        """Configure camera with manual focus and other settings"""
        if not self.cap or not self.cap.isOpened():
            return False
        
        logger.info("Configuring camera settings...")
        
        # Set resolution and FPS
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.config.fps)
        
        # Set buffer size for minimal latency
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, self.config.buffer_size)
        
        # CRITICAL: Disable autofocus first
        logger.info("Disabling autofocus...")
        if not self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0):
            logger.warning("Failed to disable autofocus - camera may not support this feature")
        
        # Verify autofocus is disabled
        time.sleep(0.1)
        autofocus_status = self.cap.get(cv2.CAP_PROP_AUTOFOCUS)
        if autofocus_status != 0:
            logger.warning(f"Autofocus still enabled (status: {autofocus_status})")
        else:
            logger.info("Autofocus successfully disabled")
        
        # Set manual focus
        logger.info(f"Setting manual focus to {self.config.manual_focus}...")
        if not self.cap.set(cv2.CAP_PROP_FOCUS, self.config.manual_focus):
            logger.warning("Failed to set manual focus")
        
        # Verify focus setting
        time.sleep(0.1)
        current_focus = self.cap.get(cv2.CAP_PROP_FOCUS)
        logger.info(f"Current focus value: {current_focus}")
        
        # Configure image settings
        settings_to_apply = [
            ('brightness', self.config.brightness),
            ('contrast', self.config.contrast),
            ('saturation', self.config.saturation),
            ('sharpness', self.config.sharpness),
            ('gamma', self.config.gamma),
            ('auto_exposure', self.config.auto_exposure),
            ('exposure', self.config.exposure),
        ]
        
        for setting_name, value in settings_to_apply:
            prop_id = self.PROPERTIES.get(setting_name)
            if prop_id is not None:
                if self.cap.set(prop_id, value):
                    logger.debug(f"Set {setting_name} to {value}")
                else:
                    logger.warning(f"Failed to set {setting_name} to {value}")
        
        # Verify final settings
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        logger.info(f"Actual camera settings: {actual_width}x{actual_height} @ {actual_fps} FPS")
        
        # Test frame capture
        ret, frame = self.cap.read()
        if not ret or frame is None:
            logger.error("Failed to capture test frame")
            return False
        
        logger.info(f"Test frame captured: {frame.shape}")
        return True
    
    def start_capture(self) -> bool:
        """Start continuous frame capture in separate thread"""
        if self.is_running:
            logger.warning("Capture already running")
            return True
        
        if not self.cap or not self.cap.isOpened():
            logger.error("Camera not connected")
            return False
        
        self.is_running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        
        logger.info("Started frame capture")
        return True
    
    def _capture_loop(self):
        """Continuous frame capture loop"""
        while self.is_running:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    with self.frame_lock:
                        self.current_frame = frame.copy()
                else:
                    logger.warning("Failed to capture frame")
                    time.sleep(0.01)
            else:
                logger.error("Camera disconnected during capture")
                break
            
            time.sleep(0.001)  # Small delay to prevent CPU overload
    
    def get_frame(self) -> Optional[Tuple[bool, Any]]:
        """Get latest frame"""
        with self.frame_lock:
            if self.current_frame is not None:
                return True, self.current_frame.copy()
            else:
                return False, None
    
    def set_focus(self, focus_value: int) -> bool:
        """Set manual focus value"""
        if not self.cap or not self.cap.isOpened():
            logger.error("Camera not connected")
            return False
        
        # Ensure autofocus is disabled
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        
        # Set focus
        result = self.cap.set(cv2.CAP_PROP_FOCUS, focus_value)
        
        if result:
            logger.info(f"Focus set to {focus_value}")
            # Verify
            time.sleep(0.1)
            actual_focus = self.cap.get(cv2.CAP_PROP_FOCUS)
            logger.debug(f"Actual focus: {actual_focus}")
        else:
            logger.error(f"Failed to set focus to {focus_value}")
        
        return result
    
    def get_camera_info(self) -> Dict[str, Any]:
        """Get current camera information and settings"""
        if not self.cap or not self.cap.isOpened():
            return {"error": "Camera not connected"}
        
        info = {
            "backend": self.cap.getBackendName(),
            "resolution": {
                "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            },
            "fps": self.cap.get(cv2.CAP_PROP_FPS),
            "focus": {
                "auto_focus": self.cap.get(cv2.CAP_PROP_AUTOFOCUS),
                "focus": self.cap.get(cv2.CAP_PROP_FOCUS)
            },
            "image_settings": {
                "brightness": self.cap.get(cv2.CAP_PROP_BRIGHTNESS),
                "contrast": self.cap.get(cv2.CAP_PROP_CONTRAST),
                "saturation": self.cap.get(cv2.CAP_PROP_SATURATION),
                "sharpness": self.cap.get(cv2.CAP_PROP_SHARPNESS),
                "gamma": self.cap.get(cv2.CAP_PROP_GAMMA),
                "exposure": self.cap.get(cv2.CAP_PROP_EXPOSURE),
                "auto_exposure": self.cap.get(cv2.CAP_PROP_AUTO_EXPOSURE),
            }
        }
        
        return info
    
    def stop_capture(self):
        """Stop frame capture"""
        self.is_running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
        logger.info("Stopped frame capture")
    
    def disconnect(self):
        """Disconnect from camera"""
        self.stop_capture()
        if self.cap:
            self.cap.release()
            self.cap = None
        logger.info("Camera disconnected")
    
    def __enter__(self):
        """Context manager entry"""
        if self.connect():
            self.start_capture()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

def main():
    """Main function for testing camera controller"""
    print("Arducam Camera Controller Test")
    print("=" * 50)
    
    # Create camera controller
    controller = ArducamController()
    
    try:
        # Connect and start capture
        with controller:
            # Get camera info
            info = controller.get_camera_info()
            print("\nCamera Information:")
            print(f"Backend: {info['backend']}")
            print(f"Resolution: {info['resolution']['width']}x{info['resolution']['height']}")
            print(f"FPS: {info['fps']}")
            print(f"Autofocus: {info['focus']['auto_focus']}")
            print(f"Focus: {info['focus']['focus']}")
            
            # Test focus adjustment
            print("\nTesting focus adjustment...")
            focus_values = [0, 50, 100, 150, 200, 255]
            
            for focus_val in focus_values:
                controller.set_focus(focus_val)
                time.sleep(0.5)
                
                # Get a frame
                ret, frame = controller.get_frame()
                if ret:
                    print(f"Focus {focus_val}: Frame captured {frame.shape}")
                else:
                    print(f"Focus {focus_val}: No frame")
            
            # Display live feed with focus control
            print("\nLive feed with focus control")
            print("Press:")
            print("  'q' - Quit")
            print("  'a' - Decrease focus")
            print("  'd' - Increase focus")
            print("  's' - Reset focus to center")
            
            current_focus = controller.config.manual_focus
            
            while True:
                ret, frame = controller.get_frame()
                if ret:
                    # Add focus info to frame
                    cv2.putText(frame, f"Focus: {current_focus}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame, "Press Q to quit, A/D for focus", (10, 70),
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
            
    except Exception as e:
        logger.error(f"Error in main: {e}")
    
    print("\nCamera test complete!")

if __name__ == "__main__":
    main()
