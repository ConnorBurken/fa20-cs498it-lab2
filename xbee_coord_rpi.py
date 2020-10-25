import serial, time
from xbee import XBee
import time
import json

SERIAL_PORT = "/dev/ttyS0"
BAUD_RATE = 9600

def handle_mac(count):
    print(count)

def handle_air_quality(value):
    print("Air Sensor: " + str(value))

def handle_smoke_sensor(value):
    print("Smoke Sensor: " + str(value))

def handle_sound_sensor(value):
    print("Sound Sensor: " + str(value))


# handler for whenever data is received from transmitters - operates asynchronously
def receive_data(data):
    # print("Received data: {}".format(data))
    rx = data['rf_data'].decode('utf-8')
    print(rx)
    payload  = json.loads(rx)

    if payload["Id"] == "mac":
       handle_mac(payload["mac_count"])
    elif payload["Id"] == "air_sensor":
       handle_air_quality(payload['sensor_value'])

    elif payload["Id"] == "smoke_sensor":
       handle_smoke_sensor(payload['sensor_value'])

    elif payload["Id"] == "sound_sensor":
       handle_sound_sensor(payload['sensor_value'])



# configure the xbee and enable asynchronous mode
ser = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE)
xbee = XBee(ser, callback=receive_data, escaped=False)

# main loop/functionality
while True:
    try:
        # operate in async mode where all messages will go to handler
        time.sleep(0.001)
    except KeyboardInterrupt:
        break

# clean up
xbee.halt()
ser.close()
