# monitor_pc_ws_client.py
# 23.06.2023

import asyncio
import asyncio_mqtt as aiomqtt
import paho.mqtt as mqtt
import websockets
import json
import sys
import os
import psutil
import psycopg
import paramiko
import subprocess
import datetime

# default dictionary for configuring MQTT
# keys of the dict may be overwritten before the settings
# are used for configuration

mqtt_params_D = {
        "hostname": "127.0.0.1",  # The only non-optional parameter
        "port": 15675,
        "username": "rpi_monitor",
        "password" : "rpi_monitor",
        "logger": None,
        "client_id": None,
        "tls_context": None,
        "tls_params": None,
        "proxy": None,
        "protocol": mqtt.client.MQTTv311,
        "will": None,
        "clean_session": None,
        "transport": "websockets",
        "keepalive": 60,
        "bind_address": "",
        "bind_port": 0,
        "clean_start": mqtt.client.MQTT_CLEAN_START_FIRST_ONLY,
        "properties": None,
        "message_retry_set": 20,
        "socket_options": (),
        "max_concurrent_outgoing_calls": None,
        "websocket_path": "/ws",
        "websocket_headers": None}

async def main(client_D, mqtt_params_D):
    uri = client_D['uri']
    
    img_dir = client_D['img_dir']
    base_file_name = client_D['base_file_name']
    nr_of_files_in_gallery = client_D['nr_of_files_in_gallery']
    
    base_name, extension = os.path.splitext(base_file_name)
    count = 0
    
    # connect to websocket
    async with websockets.connect(uri) as websocket:
        async with aiomqtt.Client(**mqtt_params_D) as mqtt_client:   
            while True:
                data = await websocket.recv()
                data_type = type(data).__name__
                # we expect either 'str' or 'bytes' for data_type
                print(f"data_type : {data_type}")
                timestamp = datetime.datetime.now().strftime("%y-%m-%d %H.%M.%S.%f")
                
                if data_type == 'str':
                    msg_D = json.loads(data)
                    msg_type = msg_D['type']
                    msg_D['timestamp'] = timestamp
                    payload = json.dumps(msg_D)
                    
                    if msg_type == 'new_img':
                        # request image
                        print(f"img notification received: {msg_D}")
                        query = {'type': "get_new_img", 'value': "get a new image from server"}
                        query_s = json.dumps(query)
                        await websocket.send(query_s)
                        # publish to message broker
                        await mqtt_client.publish('rpi/new_image', payload=payload, qos=1, retain=True)
                        
                    elif msg_type == 'random_data':
                        print(f"random data received: {msg_D}")
                        # publish to message broker
                        await mqtt_client.publish('rpi/random_data', payload=payload, qos=1, retain=True)
                    elif msg_type == 'pir_sensor':
                        print(f"pir_sensor data received: {msg_D}")
                        # publish to message broker
                        await mqtt_client.publish('rpi/pir_sensor', payload=payload, qos=1, retain=True)
                    elif msg_type == 'temp_sensor':
                        print(f"temp_sensor data received: {msg_D}")
                        # publish to message broker
                        await mqtt_client.publish('rpi/temp_sensor', payload=payload, qos=1, retain=True)
                    elif msg_type == 'light_sensor':
                        print(f"light_sensor data received: {msg_D}")
                        # publish to message broker
                        await mqtt_client.publish('rpi/light_sensor', payload=payload, qos=1, retain=True)
                    else:
                        print(f"unknown message received: {msg_D}")
                        
                # image data received as bytes
                elif data_type == 'bytes': 
                    file_name_base = f"{base_name}{count}{extension}"
                    file_img = os.path.join(img_dir, file_name_base)
                    with open(file_img, 'wb') as fid:
                        fid.write(data)
                    print(f"image stored in: {file_img}")
                    count = (count + 1) % nr_of_files_in_gallery
                    # publish to message broker
                    payload = json.dumps(dict(type=data_type, timestamp=timestamp, img=file_name_base))
                    await mqtt_client.publish('rpi/camera', payload=payload, qos=1, retain=True)
                else:
                    print(f"data type: {data_type} is not expected or implemented")
                    await mqtt_client.publish('rpi/unknown', payload=str("not yet implemented message"), qos=1, retain=True)
                
if __name__ == "__main__":
    from argparse import ArgumentParser
    from subprocess import Popen
    import json
    import os
    import sys
    import time
    import asyncio_mqtt as aiomqtt
    import paho.mqtt as mqtt
    
    pyInt = sys.executable
    cwd = os.chdir(os.path.dirname(__file__))
    print(f"cwd: {os.getcwd()}")
    
    parser = ArgumentParser()
    parser.add_argument("sshCredentialsJS", help="credentials file (host, user, pwd, etc)")
    parser.add_argument("configJS", help="configuration file (*.json)")
    parser.add_argument("--resultJS", default=None, help="some important information may be collected in this file (json)")
    args = parser.parse_args()
    
    with open(args.sshCredentialsJS, 'r') as fid:
        sshCredentials_D = json.load(fid)

    with open(args.configJS, 'r') as fid:
        config_D = json.load(fid)
        # extracting sub-dictionaries
        logging_D = config_D['logging']
        use_logging = logging_D['use_logging']
        mqtt_broker_D = config_D['mqtt_broker']
        use_mqtt = mqtt_broker_D['use_mqtt']
        database_D = config_D['database']
        use_db = database_D['use_db']
        rpi_cfg_D = config_D['monitor_rpi']
        pc_cfg_D = config_D['monitor_pc']
        
    # check if logging shall be enabled
    if use_logging:
        log_dir = os.path.join(os.path.dirname(__file__), logging_D['log_dir'])
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            print(f"created log-dir: {log_dir}")
              
    # check for message broker running
    if use_mqtt:
        try:
            broker_info_D = psutil.win_service_get(mqtt_broker_D['service_name']).as_dict()
            if broker_info_D['status'] != 'running':
                print("MQTT broker service not running -> exit program")
            else:
                print("MQTT broker running")
        except Exception as ex:
            print(f"checking for message broker failed: {ex}")
        
    # check for running database
    if use_db:
        try:
            conn = psycopg.connect(dbname=database_D['dbname'], user=database_D['user'], password=database_D['password'],
                                   host=database_D['host'], port=database_D['port'])
            print(f"can connect to db: {conn}")
            conn.close()
        except Exception as ex:
            print(f"failed to connect to db: {ex}") 
    
    # check if Raspberry PI is running and that credentials are ok ...
    try:
        sshClient = paramiko.client.SSHClient()
        sshClient.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)
        sshClient.connect(sshCredentials_D['ip_address'], port=sshCredentials_D['port'], 
                        username=sshCredentials_D['user'], password=sshCredentials_D['password'])
        time.sleep(2.0)
        sshClient.close()
        print(f"can connect to Raspberrry Pi with ip: {sshCredentials_D['ip_address']}")
    except Exception as ex:
        print(f"failed to connect to Raspberry PI: {ex}")        
    
    #--------------------------------------------------------------------
    # Starting programs on the Raspberry PI (RPI)
    #
    
    # start capturing images (RPI)
    pyStartStop = rpi_cfg_D['camera_app']['program_start_stop']
    camera_args = rpi_cfg_D['camera_app']['args']
    print(f"starting camera app on RPI")
    img_process = subprocess.run([pyInt, pyStartStop, *camera_args], text=True, capture_output=True)
    print(f"return code: {img_process.returncode}\n")
    print(f"output stdout: {img_process.stdout}\n")
    print(f"output stderr: {img_process.stderr}\n")
    with open(camera_args[-1], 'r') as fid:
        result_D = json.load(fid)
        print(f"running: {result_D['running']} ; nr running: {result_D['nr_running']}")
        if result_D['nr_running'] != 1:
            sys.exit("only one camera instance is allowed to run -> exit program")
    time.sleep(2.0)
    
    # start the websocket server (RPI)
    pyStartStop = rpi_cfg_D['ws_server_app']['program_start_stop']
    ws_server_args = rpi_cfg_D['ws_server_app']['args']
    print(f"starting websocket server on RPI")
    ws_server_process = subprocess.run([pyInt, pyStartStop, *ws_server_args], text=True, capture_output=True)
    print(f"return code: {ws_server_process.returncode}\n")
    print(f"output stdout: {ws_server_process.stdout}\n")
    print(f"output stderr: {ws_server_process.stderr}\n")
    with open(ws_server_args[-1], 'r') as fid:
        result_D = json.load(fid)
        print(f"running: {result_D['running']} ; nr running: {result_D['nr_running']}")
        if result_D['nr_running'] != 1:
            sys.exit("only one ws_server_app is allowed to run -> exit program")
    time.sleep(2.0)

    
    #-----------------------------------------------------------
    # Starting the monitoring program on this computer 
    # library asyncio_mqtt requires a specific event loop on Windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main(pc_cfg_D, mqtt_params_D))