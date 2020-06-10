# pylint: skip-file
from repositories.DataRepository import DataRepository
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS


import time
import threading

# Custom imports
from RPi import GPIO
from repositories.klasseknop import Button
from repositories.DataRepository import DataRepository
from repositories.RGB import RGB
from repositories.Servo import Servo
from repositories.MCP3008 import MCP3008
from repositories.HX711 import HX711
from repositories.LCD import LCD
from repositories.Afstand import Ultrasonic


# Start app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'smartpet_secret!'

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# pins
pin_servo = 21

pins_rgb = [4, 17, 27]

pins_load_voederbak = [5, 6]

# E, RS, D0, D1 , D2, D3, D4, D5, D6, D7
pins_lcd = [20, 18, 16, 12, 25, 24, 23, 26, 19, 13]

pin_hx711_data = 5
pin_hx711_clock = 6

pins_ultrasonic = [2,3]

# def setup():
GPIO.cleanup()
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

hx = HX711(pins_load_voederbak[0], pins_load_voederbak[1])
mcp = MCP3008()
rgb_led = RGB(pins_rgb)
display = LCD(pins_lcd)



# data
gewicht_voederbak = 0
gewicht_voederbak_huidig = 0
gewicht_voederbak_vorig = 0


# endpoint
endpoint = '/api/v1'


@app.route(endpoint + '/history', methods=['GET'])
def get_history():
    if request.method == 'GET':
        s = DataRepository.read_history()
        return jsonify(s), 200


@app.route(endpoint + '/history/day', methods=['GET'])
def get_history_day():
    if request.method == 'GET':
        s = DataRepository.read_history_day()
        return jsonify(s), 200


@app.route(endpoint + '/history/week', methods=['GET'])
def get_history_week():
    if request.method == 'GET':
        s = DataRepository.read_history_week()
        return jsonify(s), 200


@app.route(endpoint + '/history/month', methods=['GET'])
def get_history_month():
    if request.method == 'GET':
        s = DataRepository.read_history_month()
        return jsonify(s), 200


@app.route(endpoint + '/history/year', methods=['GET'])
def get_history_year():
    if request.method == 'GET':
        s = DataRepository.read_history_year()
        return jsonify(s), 200


@app.route(endpoint + '/history/date/<date>', methods=['GET'])
def get_history_date(date):
    if request.method == 'GET':
        s = DataRepository.read_history_date(date)
        return jsonify(s), 200


@app.route(endpoint + '/fillhistory/day', methods=['GET'])
def get_fillhistory_day():
    if request.method == 'GET':
        s = DataRepository.read_fillhistory_day()
        return jsonify(s), 200


@app.route(endpoint + '/feedaverage/<days>', methods=['GET'])
def get_feed_average(days):
    if request.method == 'GET':
        s = DataRepository.read_feed_average(days)
        return jsonify(s), 200


@app.route(endpoint + '/feedcount/<days>', methods=['GET'])
def get_feed_count_today(days):
    if request.method == 'GET':
        s = DataRepository.read_feed_count_today(days)
        return jsonify(s), 200


@app.route(endpoint + '/add_hoeveelheid', methods=['POST'])
def add_hoeveelheid():
    if request.method == 'POST':
        gegevens = DataRepository.json_or_formdata(request)
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


@app.route(endpoint + '/metingen', methods=['GET'])
def read_metingen():
    if request.method == 'GET':
        s = DataRepository.read_metingen()
        return jsonify(s), 200

# SOCKET IO


@socketio.on('connect')
def initial_connection():
    print('A new client connect')
    # # Send to the client!


@socketio.on('F2B_add_hoeveelheid')
def add_hoeveelheid_socket(data):
    fill(data)


def fill(data):
    global gewicht_voederbak, gewicht_voederbak_huidig, gewicht_voederbak_vorig

    hoeveelheid = int(data['hoeveelheid'])
    #print(gewicht_voederbak_vorig, hoeveelheid)
    servo = Servo(pin_servo)
    while(gewicht_voederbak_vorig+hoeveelheid >= gewicht_voederbak_huidig):
        servo.start()
        data = DataRepository.servo_on()
        # gewicht_voederbak_huidig += 50
        print(
            f"Vorig: {gewicht_voederbak_vorig} {hoeveelheid} Huidig gewicht: {gewicht_voederbak_huidig}")
        time.sleep(1)
    else:
        servo.stop()
        data = DataRepository.servo_off()
        gewicht_voederbak_vorig = gewicht_voederbak_huidig


def ldr_inlezen():
    while True:

        waarde_ldr = mcp.read_channel(0)
        if(waarde_ldr > 500):
            rgb_led.led_branden([1, 1, 1])
            socketio.emit('B2F_rgb', "white")
            data = DataRepository.ldr_inlezen(waarde_ldr)
            print("LDR Branden", socketio.emit('B2F_rgb', "white"))
        else:
            rgb_led.led_doven()
            socketio.emit('B2F_rgb', 0)

        time.sleep(5)


def gewicht_inlezen_voederbak():
    hx.set_reading_format("MSB", "MSB")
    hx.set_reference_unit(413)
    hx.reset()
    hx.tare()
    global gewicht_voederbak_huidig, gewicht_voederbak, gewicht_voederbak_vorig
    gewicht_voederbak = max(0, int(hx.get_weight(5)))
    while True:
        hx_meting = max(0, int(hx.get_weight(5)))
        socketio.emit('B2F_current_weight_bowl', hx_meting)
        if(hx_meting != gewicht_voederbak_huidig and hx_meting != gewicht_voederbak_huidig+1):
            gewicht_voederbak_huidig = hx_meting

            verschil = gewicht_voederbak_huidig - \
                gewicht_voederbak  # VERSCHIL TUSSEN VORIGE WAARDE
            gewicht_voederbak = gewicht_voederbak_huidig  # NIEUW VASTE WAARDE
            if(verschil < 0):  # pet has eaten
                data = DataRepository.add_eaten(abs(verschil))
                gewicht_voederbak_vorig = gewicht_voederbak
                socketio.emit('B2F_food_eaten',verschil)
            else:
                socketio.emit('B2F_food_add')
            print(
                f"WIJZIGING {gewicht_voederbak_huidig}g - verschil: {verschil}")

        else:
            gewicht_voederbak_huidig = hx_meting
            # print(f"{gewicht_voederbak_huidig}g")

        # if(hx_meting < 50):
        #     fill({"hoeveelheid": 25})
        

        hx.power_down()
        hx.power_up()
        time.sleep(1)


def ip_tonen():
    while True:
        display.write_status()
        time.sleep(10)

def afstand_meten():
    afstandsensor = Ultrasonic(pins_ultrasonic)
    while True:
        afstand = afstandsensor.meten()
        if(afstand>10):
            print("WAJOO LANG")
            
        else:
            print("WAJOO KORT")
            gewicht_inlezen_voederbak()


        time.sleep(1)

def start_processen():

    ldr_proces.start()
    # gewicht_voederbak_proces.start()
    ip_proces.start()
    afstand_proces.start();


# processen
ldr_proces = threading.Thread(target=ldr_inlezen)
# ldr_proces_timer = threading.Timer(0, ldr_proces).start()
# thread.kill()

gewicht_voederbak_proces = threading.Thread(target=gewicht_inlezen_voederbak)
ip_proces = threading.Thread(target=ip_tonen)
afstand_proces = threading.Thread(target=afstand_meten)

# Start app
if __name__ == '__main__':
    print("** SmartPET start **")
    try:
        # setup()
        start_processen()
        socketio.run(app, host="0.0.0.0", port=5000, debug=False)
    except KeyboardInterrupt as ex:
        print(ex)
    finally:
        GPIO.cleanup()
        print("finish")
