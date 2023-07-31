#tst_pc_ws_client.py
# 23.06.2023

import asyncio
import websockets
import json
import sys
import os
import subprocess

async def main(client_D):
    uri = client_D['uri']
    
    img_dir = client_D['img_dir']
    base_file_name = client_D['base_file_name']
    nr_of_files_in_gallery = client_D['nr_of_files_in_gallery']
    
    base_name, extension = os.path.splitext(base_file_name)
    count = 0
    
    # connect to websocket
    async with websockets.connect(uri) as websocket:    
        while True:
            data = await websocket.recv()
            data_type = type(data).__name__
            # we expect either 'str' or 'bytes' for data_type
            print(f"data_type : {data_type}")
            
            if data_type == 'str':
                msg_D = json.loads(data)
                msg_type = msg_D['type']
                
                if msg_type == 'new_img':
                    # request image
                    print(f"img notification received: {msg_D}")
                    query = {'type': "get_new_img", 'value': "get a new image from server"}
                    query_s = json.dumps(query)
                    await websocket.send(query_s)
                    
                elif msg_type == 'random_data':
                    print(f"random data received: {msg_D}")
                    # publish to message broker
                elif msg_type == 'pir_sensor':
                    print(f"pir_sensor data received: {msg_D}")
                    # publish to message broker
                elif msg_type == 'temp_sensor':
                    print(f"temp_sensor data received: {msg_D}")
                    # publish to message broker
                elif msg_type == 'light_sensor':
                    print(f"light_sensor data received: {msg_D}")
                    # publish to message broker
                else:
                    print(f"unknown message received: {msg_D}")
                    
            # image data received as bytes
            elif data_type == 'bytes': 
                file_img = os.path.join(img_dir, f"{base_name}{count}{extension}")
                with open(file_img, 'wb') as fid:
                    fid.write(data)
                print(f"image stored in: {file_img}")
                count = (count + 1) % nr_of_files_in_gallery
                # publish to message broker
            else:
                print(f"data type: {data_type} is not expected or implemented")
            
            
if __name__ == "__main__":
    from argparse import ArgumentParser
    from subprocess import Popen
    import json
    import os
    import sys
    import time
    
    pyInt = sys.executable
    cwd = os.chdir(os.path.dirname(__file__))
    print(f"cwd: {os.getcwd()}")
    
    parser = ArgumentParser()
    parser.add_argument("configJS", help="configuration file (*.json)")
    args = parser.parse_args()

    with open(args.configJS, 'r') as fid:
        config_D = json.load(fid)
        # extracting sub-dictionaries
        logging_D = config_D['logging']
        use_logging = logging_D['use_logging']
        mqtt_broker_D = config_D['mqtt_broker']
        use_mqtt = mqtt_broker_D['use_mqtt']
        database_D = config_D['database']
        use_db = database_D['use_db']
        server_D = config_D['server']
        client_D = config_D['client']

    # Starting the monitoring program on this computer 
    asyncio.run(main(client_D))