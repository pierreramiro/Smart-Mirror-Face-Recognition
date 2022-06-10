from machine import Pin,UART
uart = UART(0,9600)

Led_pin = 2
led = Pin(Led_pin, Pin.OUT)

while True:
    if uart.any():
        data = uart.readline()
        print(data)
        if data== b'1':
            led.high()
            print("LED is now ON!")
        elif data== b'0':
            led.low()
            print("LED is now OFF!")