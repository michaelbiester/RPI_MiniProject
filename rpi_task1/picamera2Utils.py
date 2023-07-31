# picamera2Utils.py
# 01.03.2023

from picamera2 import Picamera2
import time
import numpy as np
import cv2
import os

def initCamera(cameraConfig_D, verbose=True):
    """
    initialises the camera module
    
    args:
        cameraConfig_D: dictionary 
            {
                "width": <int> ,
                "height": <int>,
                "wait_after_start": <float>,
                "exposure_time": <int> (exposer time in microsecs),
                "analogue_gain": <float> 1.0
            }
        verbose: <bool> , if True print configuration parameters
    return:
        picam2 : the initialised camera module
    """
    width = cameraConfig_D['width']
    height = cameraConfig_D['height']
    wait_after_start = cameraConfig_D['wait_after_start']
    exposure_time = cameraConfig_D['exposure_time']
    analogue_gain = cameraConfig_D['analogue_gain']
    
    picam2 = Picamera2()
    camera_config = picam2.create_still_configuration(main={"size": (width, height)})
    picam2.configure(camera_config)
    control_dict = dict()
    control_dict["AnalogueGain"] = analogue_gain
    if exposure_time is not None: 
        control_dict["ExposureTime"] = exposure_time 
                   
    picam2.set_controls(control_dict)
    picam2.start()
    time.sleep(wait_after_start)
    
    if verbose:
        print("\nconfigured Raspi camera2 :\n")
        print(f"size (width, height): ({width}, {height})")
        print(f"wait after start: {wait_after_start}")
        print(f"exposure time (microseconds): {exposure_time}")
        print(f"analogue gain : {analogue_gain}")
    # return the initialised camera object
    return picam2