# Arducam 16MP USB Camera Control with Manual Focus

## Overview
This project provides a complete solution for controlling an Arducam 16MP USB autofocus camera on Windows, with emphasis on disabling hardware autofocus and enabling manual focus control for stable computer vision applications.

## Installation Requirements

### Python Environment
- **Python 3.14.0** ✅ (Already installed)
- **pip 25.3** ✅ (Already installed)

### Required Libraries (Already Installed)
```bash
pip install opencv-python          # Basic OpenCV
pip install opencv-contrib-python  # Extended OpenCV features
pip install numpy                  # Numerical operations
pip install matplotlib             # Plotting (optional)
pip install pyyaml                 # Configuration file support
```

## Files Created

### 1. `camera_config.yaml` - Camera Configuration
Configuration file with all camera settings including:
- Resolution and FPS settings
- Focus control parameters
- Image quality settings
- Windows-specific optimizations

### 2. `arducam_controller.py` - Main Camera Controller
Production-ready camera control class with:
- Manual focus control
- Stable video capture
- Configuration management
- Error handling and retry logic
- Thread-safe frame capture

### 3. `camera_tester.py` - Camera Properties Tester
Comprehensive testing script to:
- Detect available cameras
- Test all camera properties
- Validate focus control
- Check supported resolutions

### 4. `simple_camera_test.py` - Quick Camera Test
Simple test script to:
- Identify your Arducam camera
- Test basic focus functionality
- Quick validation

## Windows Camera Property Limitations

### Important Notes for Windows:
1. **DirectShow (DSHOW) vs Media Foundation (MSMF)**:
   - DSHOW typically offers more camera control options
   - MSMF is Microsoft's newer framework but may have limited property support
   - The controller tries DSHOW first on Windows

2. **Focus Property Support**:
   - `CAP_PROP_AUTOFOCUS`: May return -1 if not supported
   - `CAP_PROP_FOCUS`: May return -1 if not supported
   - Some UVC cameras don't expose focus controls through OpenCV on Windows

3. **White Balance Limitations**:
   - `CAP_PROP_WHITE_BALANCE` and `CAP_PROP_AUTO_WB` are not consistently supported
   - Removed from configuration to ensure compatibility

4. **Arducam Specific Considerations**:
   - Some Arducam models may require manufacturer-specific drivers
   - Focus range typically 0-255 but can vary by model
   - Auto-focus disable may not work through standard UVC controls

## Usage Instructions

### Step 1: Test Your Cameras
Run the simple test to identify your Arducam:
```bash
python simple_camera_test.py
```

### Step 2: Configure Camera Settings
Edit `camera_config.yaml` if needed:
- Set correct `device_id` (0 or 1 based on test results)
- Adjust `manual_focus` value (0-255)
- Modify resolution if needed

### Step 3: Run Main Controller
```bash
python arducam_controller.py
```

### Step 4: Manual Focus Control
When running the controller:
- Press 'A' to decrease focus
- Press 'D' to increase focus  
- Press 'S' to reset focus to center (100)
- Press 'Q' to quit

## Focus Value Guidelines
- **0**: Infinity focus (distant objects)
- **50-100**: Medium range (typical desktop distance)
- **150-200**: Close-up focus
- **255**: Minimum focus distance

## Troubleshooting

### If Autofocus Cannot Be Disabled:
1. **Check Camera Support**: Some UVC cameras don't support focus control
2. **Try Different Backends**: The controller automatically tries DSHOW and MSMF
3. **Manufacturer Software**: Use Arducam's official software to disable autofocus
4. **Hardware Switch**: Some cameras have physical autofocus switches

### If Focus Control Doesn't Work:
1. **Verify Camera Model**: Ensure your Arducam model supports manual focus
2. **Update Drivers**: Install latest Arducam drivers
3. **Test Different Values**: Focus range varies by camera model
4. **Check USB Port**: Use USB 3.0 port for best performance

### For Stable Computer Vision:
1. **Set Fixed Focus**: Find optimal focus value and lock it
2. **Use Adequate Lighting**: Consistent lighting improves focus stability
3. **Fixed Camera Position**: Prevent camera movement
4. **Configure Resolution**: Use appropriate resolution for your application

## Integration Examples

### Basic Usage:
```python
from arducam_controller import ArducamController

# Create controller
controller = ArducamController()

# Connect and start capture
with controller:
    # Set manual focus
    controller.set_focus(100)
    
    # Get frames
    ret, frame = controller.get_frame()
    if ret:
        # Process frame for computer vision
        pass
```

### Custom Configuration:
```python
controller = ArducamController("my_config.yaml")
controller.connect()
controller.set_focus(150)  # Close-up focus
controller.start_capture()
```

## Performance Considerations

### For Real-time Applications:
- Use lower resolution (1280x720 or 1920x1080)
- Set `buffer_size: 1` in config for minimal latency
- Disable unnecessary image processing

### For High-Quality Capture:
- Use maximum supported resolution
- Increase buffer size for stable frame rate
- Ensure USB 3.0 connection

## Next Steps

1. **Run Tests**: Identify your camera and test focus control
2. **Optimize Settings**: Find best focus value for your use case
3. **Integrate**: Use controller in your computer vision application
4. **Stability Testing**: Test focus stability over extended periods

## Support

For Arducam-specific issues:
- Check Arducam documentation
- Update camera firmware
- Contact Arducam support

For OpenCV issues:
- Verify OpenCV installation
- Check camera drivers
- Test with different USB ports
