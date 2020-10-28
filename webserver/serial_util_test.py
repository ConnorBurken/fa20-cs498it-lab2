from _thread import start_new_thread
import time
from serial_util import parse_input

counter = 0

def get_serial_ports():
    return [
        '/dev/tty.bluetooth.001',
        '/dev/tty.usbmodem.001',
        '/dev/tty.serialport.001',
    ]


def select_serial_ports(_id, status):
    print('selected port id: {0}'.format(_id))

    # start task
    start_new_thread(serial_monitor_thread_task, (_id, status))

    # start monitor tread
    status['serial_working'] = True

    return True


def serial_monitor_thread_task(_id, status):
    global counter

    while True:
        time.sleep(1.)
        counter += 1
        parse_input('{"room_id":"room_01","sensor_id":"air_sensor","sensor_value":' + str(counter) + '}', status)
        parse_input('{"room_id":"room_02","sensor_id":"mac","sensor_value":' + str(counter) + '}', status)
