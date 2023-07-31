# program description

program: `monitor_rpi_ws_server.py`

Run as:

`python monitor_rpi_ws_server.py configFile`

## Purpose

monitors a couple of sensors and images which are captured by a program which runs in its own process.

Currently no real sensors are attached to the Raspberry PI. So the program uses a collection of *fake* sensors which generate data. Eventually these fake sensors will be replaced by physical sensor.

The currently implemented *fake* sensors are:

|sensor name| description|
|---------|-----------|
|random_data| generates numerical values at regular intervals values are chosen randomly from a range.|
|pir_sensor| generates boolean data values `true` or  `false` at randomly distributed time intervals; emulates a PIR sensor where `true` indicates an event occurred|
|temp_sensor|generates random fake temperature value in a given range at regular intervals |
|light_sensor|emulates a light sensor producing numeric values corresponding to the *light intenity*|

## configuration file

 The configuration file `configFile` provides parameters used to configure the properties of the *fake* sensors. 
 
 Additionally it provides a path to the directory into which captured images are written. This program checks the content of this directory periodically to detect for new images. The checking process is implemented by Python function `findFiles(fileDir)` defined in module `fileWatcherUtils.py`

## Parameters

|parameter|description / type / usage|
|:---------|:-----------------------:|
|`configFile`              | json file|

**example:** of content of` configFile` (json format)

```
{
    "camera": {
        "img_dir": "/home/mbi1955/projects/picamera2/gallery",
        "check_interval_s": 2.0
    },
    "random_data": {
        "data_range": [0.0, 100.0],
        "time_between_data": 2.0
    },
    "pir_sensor": {
        "data_range": [true, false],
        "t_next_event_min": 1.0,
        "t_next_event_max": 6.0
    },
    "temp_sensor": {
        "data_range": [-20.0, 60.0],
        "time_between_data": 4.0
    },
    "light_sensor": {
        "data_range": [0, 100.0],
        "time_between_data": 4.5
    }
}
```
The keys used in the configuration file are described here:

**keys**

The keys of this configuration file are described here:

`camera` : a sub-dictionary with keys `img_dir` and `check_interval_s`. `img_dir` points to the dictionary into which images captured with the HQ camera are written. The capturing process must have been already started in a separate process. ` check_interval_s` stores the number of seconds the application shall wait before checking whether new images have been inserted into the directory. 

`random_data` : a sub-dictionary with keys `data_range` and `time_between_data.` 
`data_range` is a list of 2 entries. These entries define the range (minimum, maximum) of randomly generated data. The generation of random numeric data repeats periodically with the time period stored under key `time_between_data`. The periodic generation of random data shall emulate a sensor emitting data.

`pir_sensor` : a sub-dictionary with keys `data_range`, `t_next_event_min` and `t_next_event_max`. `data_range` is a list with entries `true` and `false`. These shall denote the possible states of a PIR sensor attached to the Raspberry Pi. `True` defines PIR sensor has sensed an object. Data (`true`, `false`) are generated at randomly. The duration between two consecutive events is selected randomly in the interval [`t_next_event_min`, `t_next_event_max`]. Again the data generation process shall emulate a PIR sensor.

`temp_sensor` : a sub-dictionary with keys `data_range` and `time_between_data.` Temperature values are assigned randomly from minimum/maximum value in `data_range`. Time between *temperature measurements* is determined by the value in `time_between_data`.

`light_sensor` : a sub-dictionary with keys `data_range` and `time_between_data.` 

---

# Functional description

here is a short description how the program is organised:

coroutine `main` is started via `asyncio.run()`. Configuration parameters which have been extracted from the configuration file are passed into function `main` as a dictionary. 

In `main` a websocket server is started. The server waits for a connection request and invokes an asynchronous handler function `wrapped_handler` if successful.

Coroutine `wrapped_handler` has been created before by wrapping a coroutine `handler` with additional parameters provided in dictionary `monitor_D`. Note: the wrapping is done using function `partial` of the `functools` library.

Coroutine `handler` accepts function parameters `monitor_D`, `websocket`, `path_str`.

Within `handler` coroutines `processQuery`, `watchFile`, `randomDataProducer`, `pirSensor`, `temperatureSensor`, `lightSensor` are setup (provided with their respective parameters).

All coroutines are started to run concurrently using `await asyncio.gather(...)`.

A short overview of what these coroutines do is provided here:

1. `processQuery` : runs in an infinite loop watching for messages received from a websocket. The type of the message is analysed. For a type of `get_new_message` the newest available image is identified (`findFiles`) and send via websocket as blob to the requesting client. For all other message types the message is just echoed back to the client.

2. `watchFile` : runs in an infinite loop to check at regular time intervals, if a captured image with a newer time stamp has been stored. In that case a message is set up to notify the client. The message of type `new_img` is sent via websocket.

3.  `randomDataProducer` : runs in a infinite loop and generate random numerical data. Each data item is inserted into a message of type `random_data` and sent to the client via websocket.

4. `pirSensor` : runs in an infinite loop and generates *fake* PIR sensor data. Each data item is inserted into a message of type `pir_sensor` and sent to the client via websocket.

5. `temperatureSensor` : runs in an infinite loop and generates *fake* temperature measurements. Each data item is inserted into a message of type `temp_sensor` and sent to the client via websocket.

6. `lightSensor` : runs in an infinite loop and generates *fake* light intensity measurements. Each data item is inserted into a message of type `light_sensor` and sent to the client via websocket.

