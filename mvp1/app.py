# pylint: skip-file
from repositories.DataRepository import DataRepository
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS

import time
import threading

# Custom imports
from repositories.DataRepository import DataRepository

# Start app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'smartpet_secret!'

#socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# pins
pin_servo = 21

pins_rgb = [4, 17, 27]

pins_lcd_data = [16, 12, 25, 24, 23, 26, 19, 13]
pin_lcd_rs = 18
pin_lcd_e = 3

pin_hx711_data = 5
pin_hx711_clock = 6


#data
gewicht_voederbak = 0
gewicht_voederbak_huidig = 0


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
        print(gegevens)
        data = DataRepository.add_hoeveelheid(
            gegevens['hoeveelheid'])
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


def fill(hoeveelheid):
    while(gewicht_voederbak+hoeveelheid <= gewicht_voederbak_huidig):
        # 0 graden (neutraal)
        servo.ChangeDutyCycle(6)
        print(0)
        time.sleep(1)
    
        # -90 graden (rechts)
        servo.ChangeDutyCycle(2.5)
        print(-90)
        time.sleep(1)
    
        # 0 graden (neutraal)
        servo.ChangeDutyCycle(6)
        print(0)
        time.sleep(1)
    
        # 90 graden (links)
        servo.ChangeDutyCycle(11)
        print(90)
        time.sleep(1)
        


def setup():
    GPIO.setup(pin_servo, GPIO.OUT)
    servo = GPIO.PWM(pin_servo, 50)


    # Start app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
    try:
        setup()


    except KeyboardInterrupt as e:
        print(e)
    finally:
        spi.close()
        servo.stop()
        GPIO.cleanup()
        print("Finish")