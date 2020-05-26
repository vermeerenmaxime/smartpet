# pylint: skip-file
from repositories.DataRepository import DataRepository
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS


import time
import threading

# Custom imports
from repositories.klasseknop import Button
from repositories.DataRepository import DataRepository
from repositories.RGB import RGB
from repositories.Servo import Servo
from RPi import GPIO

# Start app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'smartpet_secret!'

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# pins
pin_servo = 21

pins_rgb = [4, 17, 27]

pins_lcd_data = [16, 12, 25, 24, 23, 26, 19, 13]
pin_lcd_rs = 18
pin_lcd_e = 3

pin_hx711_data = 5
pin_hx711_clock = 6

servo = Servo(pin_servo)

# data
gewicht_voederbak = 200
gewicht_voederbak_huidig = 0

# def setup():
    
#     GPIO.cleanup()
    





# endpoint
endpoint = '/api/v1'

@app.route(endpoint + '/history', methods=['GET'])
def get_history():
    if request.method == 'GET':
        s = DataRepository.read_history()
        return jsonify(s), 200


@app.route(endpoint + '/history/today', methods=['GET'])
def get_history_today():
    if request.method == 'GET':
        s = DataRepository.read_history_today()
        return jsonify(s), 200


@app.route(endpoint + '/history/week', methods=['GET'])
def get_history_week():
    if request.method == 'GET':
        s = DataRepository.read_history_week()
        return jsonify(s), 200


@app.route(endpoint + '/feedaverage/<days>', methods=['GET'])
def get_feed_average(days):
    if request.method == 'GET':
        s = DataRepository.read_feed_average(days)
        return jsonify(s), 200


@app.route(endpoint + '/add_hoeveelheid', methods=['POST'])
def add_hoeveelheid():
    if request.method == 'POST':
        gegevens = DataRepository.json_or_formdata(request)
        data = DataRepository.add_hoeveelheid(
            gegevens['hoeveelheid'])
        #fill(gevens['hoeveelheid'])
        
        return jsonify(data), 201


@app.route(endpoint + '/app_settings', methods=['GET', 'PUT'])
def app_settings():
    if request.method == 'GET':
        s = DataRepository.read_settings()
        return jsonify(s), 200
    if request.method == 'PUT':

        gegevens = DataRepository.json_or_formdata(request)
        print(gegevens)
        data = DataRepository.update_settings(
            gegevens['daily_goal'], gegevens['daily_range'])
        if data is not None:
            print(data)
            return jsonify(gegevens), 200
        else:
            return jsonify("ERROR: Update niet gelukt"), 404


# SOCKET IO
@socketio.on('connect')
def initial_connection():
    print('A new client connect')
    # # Send to the client!
    
@socketio.on('F2B_add_hoeveelheid')
def add_hoeveelheid_socket(data):
    fill(data)

def fill(data):
    print(data)
    print("huts")
    led_proces.start()
    while(gewicht_voederbak+hoeveelheid <= gewicht_voederbak_huidig):
        servo.start()
    else:
        servo.stop()
        gewicht_voederbak = gewicht_voederbak_huidig

def enable_led():
    rgb = RGB(pins_rgb)
    colors = [1, 0, 1]
    for i in range(0,6):
        print("LED Activate")
        rgb.led_knipper(colors)
        time.sleep(1)

led_proces = threading.Thread(target=enable_led)
led_proces.start()

# Start app
if __name__ == '__main__':
    print("** SmartPET start **")
    app.run(host="0.0.0.0", port=5000, debug=False)
    # try:
    #     setup()
    #     servo = Servo(pin_servo)
    #     servo.start()
    #     while True:
    #         time.sleep(2)

    # except KeyboardInterrupt as e:
    #     print(e)
    # finally:
    #     GPIO.cleanup()
    #     print("Finish")