# RPI_MiniProject
a mini project using Raspberry PI as a monitoring utility

## dir: rpi_task1
a Python program `getImgJpgMulti.py` runs on the Raspberry PI. See `readme_getImgJpgMulti.md`
for how to use this program and how to setup the configuration file.

Another Python program `monitor_rpi_ws_server.py` watches for captured images and if there are any, a PC connected via 
websockets is notified.

Additionally there are a couple of sensors which notifiy a PC of new data. Currently these sensors are only emulated.
Future modifications of the program are expected to use *real* sensors. See `readme_monitor_rpi_ws_server.md` for more
details how to use `monitor_rpi_ws_server.py`.

## dir: task1

program: `startStopRemoteProgram.py` serves to start a program on the Raspberry PI from a remote PC via SSH/SFTP loging

Run as:

`python startStopRemoteProgram.py sshCredentialsJS configJS kill_running_processes start_program`

For the RPI Mini-project this program is used to:

1) start image capturing on the RPI with program `getImgJpgMulti.py`
2) start monitoring program on the RPI with program `monitor_rpi_ws_server.py`

See `readme_startStopRemoteProgram.md` for more details how to use `startStopRemoteProgram.py`.   

## dir: task2

program `checkRunningPrograms_Services.py` is a utility program. It is configured via a configuration file to check whether a 
program (eg. `RabbitMQ` , `PostgreSQL`) is running .

See `readme_checkRunningPrograms_Services.md` on how to use this program.

## dir: task3
