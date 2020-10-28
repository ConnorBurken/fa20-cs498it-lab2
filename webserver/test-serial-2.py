import serial

ser = serial.Serial('/dev/tty.usbserial-D3070K0N', 9600)

while True:
    try:
        incoming = ser.readline().strip()
        print ('%s' %incoming.decode())
    except (RuntimeError, serial.SerialException):
        print('Error when reading from port')
    # string = input("") + '\n'
    # ser.write(string.encode())
