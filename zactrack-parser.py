# Configuration files

import logging
from logging.handlers import TimedRotatingFileHandler

import pyzabbix
from pyzabbix import ZabbixMetric, ZabbixSender

import configparser

import sys
from time import sleep
import json
import os

import socketio

from Actor import Actor

logger = logging.getLogger('zactrack-parse')
configPath = filename=os.path.join(sys.path[0], "config.ini")


zabbix_ip="192.168.0.116"
zabbix_packet = []

log_file_handler = TimedRotatingFileHandler(filename=os.path.join(sys.path[0], "runtime.log"), when='D', interval=1, backupCount=10,
                                    encoding='utf-8',
                                    delay=False)

log_console_handler = logging.StreamHandler(sys.stdout)

log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

log_file_handler.setFormatter(log_formatter)
log_console_handler.setFormatter(log_formatter)


logger.setLevel(logging.DEBUG)

logger.addHandler(log_file_handler)
logger.addHandler(log_console_handler)

logger.info("Entering program")

# Logging initialised

zabbixServer = ZabbixSender(zabbix_server=zabbix_ip, timeout=1)


sio = socketio.Client()

sio.connect("ws://192.168.3.24:8082/socket.io/")

sio.emit("zactrack-room-control-join", ("room-system-states", False))
sio.emit("zactrack-room-control-join", ("room-version-license-information", None))
sio.emit("zactrack-room-control-join", ("room-client-live-info", None))
sio.emit("zactrack-room-control-join", ("room-active-show-history-entry", None))
sio.emit("zactrack-room-control-join", ("room-anchor-live-infos", None))
sio.emit("zactrack-room-control-join", ("room-all-anchor-tracking-infos", None))
sio.emit("zactrack-room-control-join", ("room-actor-live-infos", None))
sio.emit("zactrack-room-control-join", ("room-all-sensor-tracking-information", False))
sio.emit("zactrack-room-control-join", ("room-fixture-live-runtime-values", None))

@sio.on("actor-live-infos")
def on_actor_message(data):
    zabbix_packet = []

    for actor in data:
        if actor['state'] == 2:
            item = "Battery.Percentage." + str(actor['id'])
            zabbix_packet.append(ZabbixMetric("Zactrack", item, actor['battery']))
        logger.info(str(actor['id']) + ": " + str(actor['state']) + "   " + str(actor['battery']))

    if len(zabbix_packet) > 0:
        try:
            zabbixServer.send(zabbix_packet)
        except:
            logger.warning("Failed to send to zabbix server")

while True:
    continue