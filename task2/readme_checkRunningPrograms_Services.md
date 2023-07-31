# program description

program: `checkRunningPrograms_Services.py`

Run as:

`python checkRunningPrograms_Services.py configJS resultJS`

Dependig on the content of configuration file `configJS` the programs goes through a list of programs / services. For each
program / services it checks the status. A summary is written to a json file `resultJS`. A short summary is written to the console / stdout.


## Parameters

|parameter|description / type / usage|
|:---------|:-----------------------:|
|`configJS`              | json file (list of programs & services to check)|
|`resultJS`| json file (summary of output) |

## example of configuration file `configJS`

```
{
    "programs": ["erl.exe", "erlsrv.exe" ],
    "services": ["RabbitMQ"]
}
```
key `programs` is a list of programs which shall be checked.

Here two programs `erl.exe` and `erlsrv.exe` shall be checked.

key `services` is a list of services which shall be checked.

Here only one service `RabbitMQ` shall be checked.

## example of result file `resultJS`

```
{
  "programs": {
    "erl.exe": [
      {
        "name": "erl.exe",
        "status": "running",
        "pid": 5468,
        "username": null
      }
    ],
    "erlsrv.exe": [
      {
        "name": "erlsrv.exe",
        "status": "running",
        "pid": 12260,
        "username": null
      }
    ]
  },
  "services": {
    "RabbitMQ": {
      "display_name": "RabbitMQ",
      "binpath": "\"C:\\Program Files\\Erlang OTP\\erts-13.2.2\\bin\\erlsrv.exe\"",
      "username": "LocalSystem",
      "start_type": "automatic",
      "status": "running",
      "pid": 12260,
      "name": "RabbitMQ",
      "description": "Multi-protocol open source messaging broker"
    }
  }
}
```
The output shows that programs `erl.exe`, `erlsrv.exe` and service `RabbitMQ` are running.

The output of the program to the console / stdout provides a summary of this check:

```
all programs running            : True
all services running            : True
all programs & services running : True
```

