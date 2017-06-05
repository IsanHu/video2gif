#!/bin/bash
nohup python app.py 5555  > ~/log/port_5555.log &
nohup python app.py 5000  > ~/log/port_5000.log &
nohup python app.py 5005  > ~/log/port_5005.log &