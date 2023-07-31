# startStopRemoteProgram.py
# 21.06.2023
# m.biester

"""
with hohup 
"""

import sys
import os
import time
import paramiko
import json
from argparse import ArgumentParser

"""
- connecting remotely via SSH
- start a program on remote host and run in background
- exit from SSH -> program continue running
"""
parser = ArgumentParser()
parser.add_argument("sshCredentialsJS", help="credentials file (host, user, pwd, etc)")
parser.add_argument("configJS", help="configuration file")
parser.add_argument("kill_running_processes", choices=['y', 'Y', 'n', 'N'], help="kill all running instances ['y', 'Y', 'n', 'N']")
parser.add_argument("start_program", choices=['y', 'Y', 'n', 'N'], help="start program ['y', 'Y', 'n', 'N']")
parser.add_argument("resultJS", help="some important information may be collected in this file (json)")
args = parser.parse_args()
resultJS = args.resultJS

# processing input arguments
with open(args.sshCredentialsJS) as fid:
    credentials_D = json.load(fid)
    ip_address = credentials_D['ip_address']
    user = credentials_D['user']
    password = credentials_D['password']

with open(args.configJS) as fid:
    config_D = json.load(fid)
    # path to remote python interpreter
    pyIntRemote = config_D['pyIntRemote']
    # remote program to run
    pyProgramRemote = config_D['pyProgramRemote']
    config_pc = config_D['config_pc']
    config_rpi = config_D['config_rpi']
    redirect_rpi = config_D['redirect_rpi']
    copy_config_to_rpi = config_D.get('copy_config_to_rpi', False)
    
kill_running_processes = True if args.kill_running_processes.lower() == 'y' else False
start_program = True if args.start_program.lower() == 'y' else False

# connecting via SSH
sshClient = paramiko.client.SSHClient()
sshClient.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)
sshClient.connect(ip_address, port=22, username=user, password=password)

# is remote program running ?
cmd_str = f"pgrep -a python3"
print(f"command string: {cmd_str}\n")
stdin, stdout, stderr = sshClient.exec_command(cmd_str)
process_list = [line for line in [item.decode(encoding='utf-8') for item in stdout.read().splitlines(keepends=False)] if pyProgramRemote in line]

print(f"process info:\n")
if len(process_list) > 0:
    for process in process_list:
        print(f"{process}")
        if kill_running_processes:
            process_id = process.split()[0].strip()
            cmd_str = f"kill -9 {process_id}"            
            print(f"command string: {cmd_str}\n")
            stdin, stdout, stderr = sshClient.exec_command(cmd_str)
else:
    print("no matching processes found\n")  

# copy config file ?
if copy_config_to_rpi:
    # preparing for file transfers via SFTP
    sftpClient = sshClient.open_sftp()
    # sftpClient.chdir("/home/mbi1955")
    t_start = time.perf_counter()
    sftpClient.put(config_pc, config_rpi)
    t_elapsed = time.perf_counter() - t_start
    print(f"\ncopied file from local to remote in: {t_elapsed:0.3f} seconds\n")
    # cleaning up
    sftpClient.close()  

if start_program:
    result_D = dict()
    result_D['running'] = False
    result_D['nr_running'] = 0
    result_D["process_info"] = []
    
    # start program in background, set no hangup to keep the program running after closing SSH session
    # redirect outputs stdout, stderr
    cmd_str = f"nohup {pyIntRemote} {pyProgramRemote} {config_rpi} > {redirect_rpi} 2>&1 &"
    print(f"command string: {cmd_str}\n", flush=True)
    stdin, stdout, stderr = sshClient.exec_command(cmd_str)
    print(f"from stdout: {stdout.read()}")

    cmd_str = f"pgrep -a python3"
    print(f"command string: {cmd_str}\n", flush=True)
    stdin, stdout, stderr = sshClient.exec_command(cmd_str)
    process_list = [line for line in [item.decode(encoding='utf-8') for item in stdout.read().splitlines(keepends=False)] if pyProgramRemote in line]

    print(f"process info:\n")
    if len(process_list) > 0:
        for process in process_list:
            print(f"{process}")
            result_D["process_info"].append(process)
        result_D['running'] = True
        result_D['nr_running'] = len(process_list)
    else:
        print("no matching processes found\n")

# logging out from SSH session 
try:   
    time.sleep(3.0)
    sshClient.close()
except Exception as ex:
    print(f"exeption on closing SSH: {ex}")
finally:
    if resultJS is not None:
        with open(resultJS, 'w') as fid:
            json.dump(result_D, fid, indent=2)
