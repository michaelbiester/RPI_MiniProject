# monitor_rpi_ws_server.py
# 23.06.2023
import os
import sys
import asyncio
import itertools
import json
import time
import random
import websockets
from functools import partial
from getImgJpgMulti import getImgJpgMulti
from fileWatcherUtils import findFiles

#--- coroutines for specific tasks ---

# coroutine to receive query and return data depending on query
async def processQuery(websocket, img_dir):
        
    async for message in websocket:
        query = json.loads(message)
        query_type = query['type']

        if query_type == 'get_new_img':
            # find newes image
            files_in_dir = findFiles(img_dir)
            newest_file, newest_date = files_in_dir[0]
            # sending image: read, convert to blob, send
            with open(newest_file, mode='rb') as fid:
                data = bytearray(fid.read())
            print(f"image size (bytes): {len(data)}")
            await websocket.send(data)
        else:
            # do some work depending on query
            print(f"currently this query will only be echoed: {query}")
            await websocket.send(json.dumps(query))
        
async def watchFile(websocket, img_dir, check_interval_s):
    """
        fileDir : directory which shall be watched / monitored for changes
        check_interval_s : time in seconds between successive checks
    """
    newest_file = newest_date = None
    files_in_dir = findFiles(img_dir)
    if files_in_dir is not None:
        newest_file, newest_date = files_in_dir[0]
    
    while True:
        await asyncio.sleep(check_interval_s)
        current_files_in_dir = findFiles(img_dir)
        if current_files_in_dir is not None:
            cur_newest_file, cur_newest_date = current_files_in_dir[0]
            if (newest_date is not None) and (cur_newest_date > newest_date):
                newest_file = cur_newest_file
                newest_date = cur_newest_date
                print(f"new file detected: {newest_file} with date {newest_date}")     
                message = {"type": "new_img", "value": newest_date, "path": newest_file.path}
                await websocket.send(json.dumps(message))   
                
# coroutine to produce random data items and send to client
async def randomDataProducer(websocket, data_min, data_max, time_between_data):
    """
    websocket: a initalised websocket object for communication
    data_min: minimum value (float) of data
    data_max: maximum value (float) of data
    time_between_data: random data value are produced at regulator intervals in seconds
    """
    while True:
        value = random.randint(data_min, data_max)
        msg = {"type": 'random_data', "value": value}
        await websocket.send(json.dumps(msg))
        print(f"produced and sent random data: {msg}")
        await asyncio.sleep(time_between_data)
        
# placeholder coroutines generating fake sensor data
# will be later replacement by data from real sensors attached to the 
# Raspberry Pi 

async def pirSensor(websocket, t_next_event_min, t_next_event_max):
    """
    websocket: a initalised websocket object for communication
    t_next_event_min : minimum time interval is seconds (float) between sucsessive events
    t_next_event_max : maximum time interval is seconds (float) between sucsessive events
    """
    # this coroutine emulates a PIR sensor
    # True : PIR sensor sensed event 
    # False: PIR sensor event disappeared
    pir_last = False
    while True:
        # the event data 
        pir_current = random.choice([True, False])
        # the time for the next sensor data
        t_next_event = random.uniform(t_next_event_min, t_next_event_max)
        if pir_current != pir_last:
            msg = {"type": 'pir_sensor', "value": pir_current}
            await websocket.send(json.dumps(msg))
            print(f"produced and sent PIR event message: {msg}")
            # update state
            pir_last = pir_current  
        await asyncio.sleep(t_next_event)

async def temperatureSensor(websocket, temperature_min, temperature_max, time_between_data):
    """
    websocket: a initalised websocket object for communication
    temperature_min: minimum temperature that can be measured
    temperature_max: maximum temperature that can be measured
    """
    # this coroutine emulates a temperature sensor
    # 
    temperatur_step = 0.5
    temperature_last = 20.0
    while True:
        # the event data 
        temperature_current = temperature_last + random.choice([-1, 0, 1]) * temperatur_step
        # apply min/max temperature limits
        temperature_current = temperature_min if temperature_current <= temperature_min else temperature_current
        temperature_current = temperature_max if temperature_current >= temperature_max else temperature_current
        
        if temperature_current != temperature_last:
            msg = {"type": 'temp_sensor', "value": temperature_current}
            await websocket.send(json.dumps(msg))
            print(f"produced and sent temperature event message: {msg}")
            # update state
            temperature_last = temperature_current  
        await asyncio.sleep(time_between_data)

async def lightSensor(websocket, light_min, light_max, time_between_data):
    # this coroutine emulates a light sensor
    # 
    light_step = 1.0
    light_last = 40.0
    
    while True:
        # the event data 
        light_current = light_last + random.choice([-1, 0, 1]) * light_step
        
        if light_current != light_last:
            msg = {"type": 'light_sensor', "value": light_current}
            await websocket.send(json.dumps(msg))
            print(f"produced and sent light event message: {msg}")
            # update state
            light_last = light_current  
        await asyncio.sleep(time_between_data)
                               
async def handler(monitor_D, websocket, path_str):
    # getting function parameters from configuration dictionary
    # camera
    img_dir = monitor_D['camera']['img_dir']
    img_check_interval_s = monitor_D['camera']['check_interval_s']
    # random data producer
    rnd_data_min, rnd_data_max = monitor_D['random_data']['data_range']
    rnd_time_between_data = monitor_D['random_data']['time_between_data']
    # pir sensor
    pir_off, pir_on = monitor_D['pir_sensor']['data_range']
    pir_t_next_event_min = monitor_D['pir_sensor']['t_next_event_min']
    pir_t_next_event_max = monitor_D['pir_sensor']['t_next_event_max']
    # temperature sensor
    temperature_min, temperature_max = monitor_D['temp_sensor']['data_range']
    temp_time_between_data = monitor_D['temp_sensor']['time_between_data']
    # light sensor
    light_min, light_max = monitor_D['light_sensor']['data_range']
    light_time_between_data = monitor_D['light_sensor']['time_between_data']
    
    print(f"handler args: {monitor_D}")
    # setting up coroutines
    coro1 = processQuery(websocket, img_dir)
    coro2 = watchFile(websocket, img_dir, img_check_interval_s)
    coro3 = randomDataProducer(websocket, rnd_data_min, rnd_data_max, rnd_time_between_data)
    coro4 = pirSensor(websocket, pir_t_next_event_min, pir_t_next_event_max)
    coro5 = temperatureSensor(websocket, temperature_min, temperature_max, temp_time_between_data)
    coro6 = lightSensor(websocket, light_min, light_max, light_time_between_data)
    # letting coroutines run concurrently
    print(f"starting coroutines")
    res = await asyncio.gather(coro1, coro2, coro3, coro4, coro5, coro6)

async def main(monitor_D, host, port):
    # an event to notify if new image has been captured
    # wrapping handler function to pass in some params
    wrapped_handler = partial(handler, monitor_D)

    # start server
    print("start server")
    async with websockets.serve(wrapped_handler, host, port):
        await asyncio.Future()  # run forever

#---------------------------------------------------
if __name__ == "__main__":
    from argparse import ArgumentParser
    import json
    from subprocess import Popen
    
    # before running this program a program capturing images must be started
    # on the Raspberry PI
    
    parser = ArgumentParser()
    parser.add_argument("monitorJS", help="full path to configuration for monitor app")
    args = parser.parse_args()
    
    with open(args.monitorJS) as fid:
        monitor_D = json.load(fid)
            
    asyncio.run(main(monitor_D, "", 8001))