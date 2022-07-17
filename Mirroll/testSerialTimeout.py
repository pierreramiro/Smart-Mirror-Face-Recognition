import serial #uart

ser=serial.Serial ("/dev/ttyS0", 9600,timeout=1)
#ser=serial.Serial ("/dev/tty0", 9600,timeout=1)

while True:
    received_data = ser.read()              #read serial port
    print("longitud data:",len(received_data))
        