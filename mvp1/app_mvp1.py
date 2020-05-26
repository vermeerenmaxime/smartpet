# pylint: skip-file
from repositories.DataRepository import DataRepository
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS

import time
import threading

# Code voor led
from helpers.klasseknop import Button
from helpers.rgb import Rgb
from RPi import GPIO

led1 = 21
pin_knop1 = 24
knop1 = Button(pin_knop1)
pins_rgb = [4, 17, 27]
#Red, Green, Blue


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(led1, GPIO.OUT)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'smartpet_secret!'

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)


# API ENDPOINTS
@app.route('/')
def hallo():
    return "Server is running, er zijn momenteel geen API endpoints beschikbaar."

# SOCKET IO
@socketio.on('connect')
def initial_connection():
    print('A new client connect')
    # # Send to the client!


def lees_knop(pin):
    print("button pressed")

def lees_LDR():
    


def enable_led():
    rgb = Rgb(pins_rgb)
    colors = [1, 0, 1]
    for i in range(0,6):
        print("Hello")
        rgb.led_knipper(colors)
        time.sleep(1)

led_proces = threading.Thread(target=enable_led)
led_proces.start()

knop1.on_press(lees_knop)


if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')
    


        
