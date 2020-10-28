import sys
import glob
import serial
import json
import time
from _thread import start_new_thread
from db_util import insert_record


def parse_input(s, status):
    try:
        payload = json.loads(s)

        # update status
        if payload['room_id'] not in status['data']:
            status['data'][payload['room_id']] = {}

        sensor_id = None
        if 'sensor_id' in payload:
            sensor_id = payload['sensor_id']
        elif 'Id' in payload:
            sensor_id = payload['Id']

        sensor_value = None
        if 'sensor_value' in payload:
            sensor_value = payload['sensor_value']
        elif 'mac_count' in payload:
            sensor_value = payload['mac_count']

        status['data'][payload['room_id']][sensor_id] = sensor_value
        status['data'][payload['room_id']]['ts'] = int(round(time.time() * 1000))

        # update database
        insert_record(payload['room_id'], sensor_id, int(sensor_value))
    except:
        e = sys.exc_info()[0]
        print('Error when handling input: {0}\n e = {1}'.format(s, e))


def get_serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def select_serial_ports(_id, status):
    print('selected port id: {0}'.format(_id))

    # open serial
    status['ser'] = serial.Serial(_id, 9600)

    # start task
    start_new_thread(serial_monitor_thread_task, (_id, status))

    # start monitor tread
    status['serial_working'] = True

    return True


def serial_monitor_thread_task(_id, status):
    while True:
        try:
            incoming = status['ser'].readline().strip()
            data = incoming.decode()
            print('read << {0}'.format(data))

            parse_input(data, status)
        except:
            e = sys.exc_info()[0]
            print('Error when handling input: {0}\n e = {1}'.format(data, e))


# !!! TEST !!!
# parse_input('{123sas {"room_id":"room_01","sensor_id":"air_sensor","value":131}')
# parse_input('{"room_id":"room_01","sensor_id":"air_sensor","value":131}')
# parse_input('{ "room_id": "room_01", "Id" : "air_sensor" , "sensor_value" :51 }', {
#     'serial_working': False,
#     'ser': None,
#     'data': {}
# })
