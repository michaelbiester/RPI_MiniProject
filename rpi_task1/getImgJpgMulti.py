# getImgJpgMulti.py
# 12.03.2023

from subprocess import Popen
from argparse import ArgumentParser
import json
import sys
import os
import time
from picamera2Utils import initCamera
from picamera2 import Picamera2
import asyncio

def getImgJpgMulti(cameraConfig_D, verbose=True):
    # get an initialised camera object
    width = cameraConfig_D['width']
    height = cameraConfig_D['height']
    wait_after_start = cameraConfig_D['wait_after_start']
    exposure_time = cameraConfig_D['exposure_time']
    analogue_gain = cameraConfig_D['analogue_gain']
    img_dir = cameraConfig_D['img_dir']
    base_file_name =  cameraConfig_D['base_file_name']
    nr_of_files_in_gallery = cameraConfig_D['nr_of_files_in_gallery']
    nr_of_files = cameraConfig_D['nr_of_files']
    min_delay_between_img_capture = cameraConfig_D['min_delay_between_img_capture']
    
    picam2 = Picamera2()
    # applying the configuration
    camera_config = picam2.create_still_configuration(main={"size": (width, height)})
    picam2.configure(camera_config)
    
    # configuring exposure time and analogue gain
    if exposure_time is None:
        # camera chooses exposure time
        picam2.set_controls({"AnalogueGain": analogue_gain})
    else:
        picam2.set_controls({"ExposureTime": exposure_time, "AnalogueGain": analogue_gain})
    
    picam2.start()
    time.sleep(wait_after_start)
    if verbose:
        print(f"initalised picamera2: {picam2}")  
    # capture single image directly to file as jpeg
    
    imgFileBase, extension = os.path.splitext(base_file_name)
    count_total = 0
    count_mod = 0
    
    # loop / capturing and storing images
    while True:
        if nr_of_files is not None:
            if count_total >= nr_of_files:
                break
        img_file_full = os.path.join(img_dir, imgFileBase + str(count_mod) + extension)
        
        t1 = time.perf_counter()
        picam2.capture_file(img_file_full)
        if verbose:
            print(f"count: {count_total}  captured file: {img_file_full}")
                    
        # if capturing and storing of image takes < min_delay_between_img_capture seconds
        # delay a bit before capturing next image
        t_elapsed = time.perf_counter() - t1
        delay =  min_delay_between_img_capture - t_elapsed
        if delay > 0:
            time.sleep(delay)
        # update counters
        count_mod = (count_mod + 1) % nr_of_files_in_gallery
        count_total += 1
        
    print("done")

if __name__ == "__main__":
    
    parser = ArgumentParser()
    parser.add_argument("cameraConfigJS", help="json file to initalise camera module")
    args = parser.parse_args()
    
    # converting config file to dictionaries
    with open(args.cameraConfigJS, 'r') as fid:
        cameraConfig_D = json.load(fid)
      
    verbose = True
    # capturing
    getImgJpgMulti(cameraConfig_D, verbose=True)
    print("done")