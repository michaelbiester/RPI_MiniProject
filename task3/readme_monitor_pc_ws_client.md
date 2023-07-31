# program description

program: `monitor_pc_ws_client.py`

**prerequisite**: It is assumed that the following programs have already been started on the Raspberry PI:

1. `getImgJpgMulti.py`

2. `monitor_rpi_ws_server.py`

Run as:

`python monitor_pc_ws_client.py sshCredentialsJS configJS resultJS`

## Parameters

|parameter|description|
|---------|-----------|
|sshCredentials| json files with credentials for SSH/SFTP login |
|configJS| json file with configuration data |
|resultJS| optional json file into which debug information is written |

**parameter:** `sshCredentialsJS`
    
    json file; with parameters to login to the remote computer; example:
    
    ```{
    "ip_address": "192.168.0.50",
    "user": "username",
    "password": "some_pass_word",
    "passphrase": null
    }```

---    

**parameter:** `configJS`

json file; with parameters which configure this program `monitor_pc_ws_client.py`; example:

{
    "logging": {
        "use_logging": false,
        "log_dir": "log",
        "log_file_base": "log_monitor_pc_ws_client_.log",
        "clear_old_logs": true
    },

    "mqtt_broker": {
        "use_mqtt": true,
        "service_name": "RabbitMQ",
        "hostname": "127.0.0.1",
        "port": 15675,
        "username": null,
        "password" : null,
        "clean_session": null
    },

    "database": {
        "use_db": false,
        "host": "127.0.0.1",
        "dbname": "analysis",
        "port": 5432,
        "user": "postgres",
        "password" : "waldheim55"
    },
    
    "monitor_rpi": {
        "camera_app": {
            "program_start_stop": "C:/Users/micha/projects/raspi4/projects_rpi/monitoring_p1/task1/startStopRemoteProgram.py",
            "args": [
                "C:/Users/micha/projects/raspi4/projects_rpi/monitoring_p1/task4/ssh_credentials.json",
                "C:/Users/micha/projects/raspi4/projects_rpi/monitoring_p1/task1/startStopRemote_getJpgMulti.json",
                "y",
                "y",
                "C:/Users/micha/projects/raspi4/projects_rpi/monitoring_p1/task4/result_getJpgMulti.json"
            ]
        },
        "ws_server_app": {
            "program_start_stop": "C:/Users/micha/projects/raspi4/projects_rpi/monitoring_p1/task1/startStopRemoteProgram.py",
            "args": [
                "C:/Users/micha/projects/raspi4/projects_rpi/monitoring_p1/task4/ssh_credentials.json",
                "C:/Users/micha/projects/raspi4/projects_rpi/monitoring_p1/task4/startStopRemote_rpi_ws_server.json",
                "y",
                "y",
                "C:/Users/micha/projects/raspi4/projects_rpi/monitoring_p1/task4/result_rpi_ws_server.json"
            ]
        }
    },

    "monitor_pc": {
        "uri": "ws://192.168.0.50:8001/some_path",
        "__comment1": "full path to directory; for storing multiple images",
        "img_dir": "C:/Users/micha/projects/raspi4/projects_rpi/monitoring_p1/task4/gallery",
        "base_file_name": "img_jpg_gallery_.jpg",
        "nr_of_files_in_gallery": 10
    }
}

The *top-level* keys of this configuration file are:

1. `logging` -> refers to a dictionary with several key / value pairs to configure logging; currently logging is not implemented

2. `mqtt_broker` -> refers to a dictionary with key / value pairs to configure the MQTT broker / message queue 

3. `database` -> refers to a dictionary with key / value pairs to configure database access; currently accessing a database is not implemented

4. `monitor_rpi` -> refers to two sub dictionaries `camera_app` and `ws_server_app`

    1. `camera_app` -> refers to a dictionary with key/value pairs to configure program `getImgJpgMulti.py` which captures/stores images on the Raspberry PI

    2. `ws_server_app` -> refers to a dictionary with key/value pairs to configure program `monitor_rpi_ws_server.py` on the Raspberry PI.

    

5. `monitor_pc` -> refers to a dictionary with several key / value pairs to configure this application



**parameter:**` resultJS`

json file; this parameter is optional. If the parameter is provide addtional debug information about the execution of the program is collected into this file; example: