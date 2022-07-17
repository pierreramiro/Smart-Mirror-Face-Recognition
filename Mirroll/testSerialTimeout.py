import serial #uart

ser=serial.Serial ("/dev/ttyS0", 9600)

while True:
    received_data = ser.read()              #read serial port
    print("sec")
        