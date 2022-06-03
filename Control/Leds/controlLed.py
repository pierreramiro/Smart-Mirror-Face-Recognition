import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BOARD)
gpio.setup(12, gpio.OUT)

for  x in range ( 0, 10):

    gpio.output(12, True)
    time.sleep(0.5)
    gpio.output(12, False)
    time.sleep(0.5)

print "Ejecución finalizada"