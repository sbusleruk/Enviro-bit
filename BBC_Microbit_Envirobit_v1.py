import bme280
import time
import microbit

bme = bme280.bme280()

while True:
    sendData = 1
    try:
        current_temp = float(bme.temperature() )
        current_hum = float(bme.humidity() )
        current_pres = float(bme.pressure() )
        br = microbit.display.read_light_level()
    except floatError:
        sendData = 0
        continue
    if sendData == 1:
        print ( current_temp, current_hum, round(current_pres, 1), br )
    time.sleep(1)