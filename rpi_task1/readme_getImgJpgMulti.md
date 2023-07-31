# program description

program: `getImgJpgMulti.py`

Run as:

`python getImgJpgMulti.py configFile`

## Purpose

starts capturing images with the HQ camera attached to the Raspberry Pi. The configuration file `configFile` provides parameters for the camera setting and defines the location to which captured images are stored. The program terminates regularly if the maximum number of images has been reached.

## Parameters

|parameter|description / type / usage|
|:---------|:-----------------------:|
|`configFile`              | json file|

**parameter:**` configFile`

json file; with parameters to control how images are captured and stored on the Raspberry Pi; example:

```
{
"width": 1920,
"height": 1080,
"wait_after_start": 2.0,
"__comment1": "exposure time as integer in microseconds; null indicates automatic exposure time setting",
"exposure_time": null,
"analogue_gain": 8.0,
"__comment2": "full path to directory; for capturing multiple images",
"img_dir": "/home/mbi1955/projects/picamera2/gallery",
"base_file_name": "img_jpg_.jpg",
"nr_of_files_in_gallery": 10,
"nr_of_files": 1000,
"min_delay_between_img_capture": 1.0
}
```

**keys**

The keys of this configuration file are described here:

`width` : nr. of pixels (width) for capturing images

`height` : nr. of pixels (height) for capturing images

`wait_after_start` : after initialisation of camera has completed the program waits for some time before the capturing process starts. (in the example above a value of 2.0 corresponds to 2 seconds)

`exposure_time`: exposure time as integer in microseconds; if set to `null` the exposure time is set automatically

`analogue_gain` : a larger value increases the sensitivity and allows for a shorter exposure time

`img_dir` : full path to directory into which captured images shall be stored

`base_file_name` : string from which the file name of the captured image will be created. the string shall include the extension .jpg or .png. The full path name of the captured image is formed by joining the directory name `img_dir` with `base_file_name` (and inserting a count value before the extension).

`nr_of_files_in_gallery` : the maximum number of different count values. 

`nr_of_files` : total number of captured images / files; after having reached this number the program terminates.

Note: the count value which is added to each file name is formed by this formula: count_value = (actual image count mod nr_of_files_in_gallery)

`min_delay_between_img_capture`: seconds to wait before capturing the next image; 

## Screenshot

The screenshot shows the command to start the program and its output. The program has been aborted by entering CTRL-C.

![screenshot](start_of_getImgJpgMulti.png)
