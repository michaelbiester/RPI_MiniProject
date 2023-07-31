# program description

program: `startStopRemoteProgram.py`

Run as:

`python startStopRemoteProgram.py sshCredentialsJS configJS kill_running_processes start_program`

start/stops a program running on a remote computer (eg. Raspberry Pi) with Linux operating system. The remote program is started with several options.

## Parameters

|parameter|description / type / usage|
|:---------|:-----------------------:|
|`sshCredentialsJS`      | json file |
|`configJS`              | json file|
|`kill_running_processes`| string |
|`start_program`         | string |

**parameter:** `sshCredentialsJS`
    
    json file; with parameters to login to the remote computer; example:
    
    ```{
    "ip_address": "192.168.0.50",
    "user": "username",
    "password": "some_pass_word",
    "passphrase": null
    }```

---    

**parameter:**` configJS`

json file; with parameters control a program that will be started on the remote computer; example:

```
{
"pyIntRemote": "/usr/bin/python3",
"pyProgramRemote": "/home/mbi1955/projects/linux_experiments/programs/pyTestBackground.py",
"args": ["/home/mbi1955/projects/linux_experiments/programs/pyTestBackground.json"],
"config_rpi": "/home/mbi1955/projects/linux_experiments/programs/pyTestBackground.json",
"redirect_rpi_c": "~/projects/linux_experiments/programs/out_stdout_stderr.txt",
"redirect_rpi": "/dev/null",
"config_pc": "C:/Users/micha/projects/raspi4/projects_rpi/monitoring_p1/task1/pyTestBackground.json"
}

```

**keys**

`pyIntRemote` -> path to python on  remote computer

`pyProgramRemote` -> full path to python program that shall be started/stopped/configured

`config_pc` -> full path to a configuration file on the local PC (runs this program); depending on other arguments provided to the program this file will be copied to the remote computer to a location determined by key `config_rpi`

`config_rpi` -> full path to the configuration file on the remote computer; depending on other arguments provided to program `startStopRemoteProgram.py` a configuration file in `config_pc` to copied via SFTP to the remote computer.

`redirect_rpi` -> once the program `pyProgramRemote` has been started any output to stdout and stderr is redirected to a file pointed to by key `redirect_rp`. Either a full path to a file is provided or output is redirected to `"/dev/null"`.

---

**parameter:** `kill_running_processes`

the parameter is string parameter with one of the following values: `y`, `Y`, `n`, `N`

case: `y` or `Y` -> any already running instances of the program on the remote computer are terminated. Thus a clean start of the program is ensured.

case: `n` or `N` -> already running instances of the program on the remote computer are not terminated.

---

**parameter:** `start_program`

the parameter is string parameter with one of the following values: `y`, `Y`, `n`, `N`

case: `y` or `Y` -> the program is started on the remote computer

case: `n` or `N` -> the program is *not* started on the remote computer 

---
---

# Usage

Some frequently encountered use cases are explained here: 

The use cases differ in the choice of program parameters `kill_running_processes` and `start_program`

## case A: starting program and abort program(s) which are already running

`python startStopRemoteProgram.py sshCredentialsJS configJS kill_running_processes start_program`

with: `kill_running_processes` = `J` oder `j` **and** `start_program` = `J` oder `j`

## case B: starting program; a program already running shall continue to run

`python startStopRemoteProgram.py sshCredentialsJS configJS kill_running_processes start_program`

with: `kill_running_processes` = `n` oder `N` **and** `start_program` = `J` oder `j`

## case C: stopping running program(s) but do not start a program 

`python startStopRemoteProgram.py sshCredentialsJS configJS kill_running_processes start_program`

with: `kill_running_processes` = `J` oder `n` **and** `start_program` = `N` oder `n`
