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
from repositories.Ultrasonic import Ultrasonic


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

pins_ultrasonic = [2, 3]

# def setup():
GPIO.cleanup()
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

hx = HX711(pins_load_voederbak[0], pins_load_voederbak[1])
mcp = MCP3008()
rgb_led = RGB(pins_rgb)
display = LCD(pins_lcd)
afstandsensor = Ultrasonic(pins_ultrasonic)


# data
gewicht_voederbak = 0
gewicht_voederbak_huidig = 0
gewicht_voederbak_vorig = 0
gewicht_voederbak_live = 0


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

        data = DataRepository.update_settings(
            gegevens['daily_goal'], gegevens['daily_range'])
        if data is not None:
            return jsonify(gegevens), 200
        else:
            return jsonify("ERROR: Update niet gelukt"), 404


@app.route(endpoint + '/metingen', methods=['GET'])
def read_metingen():
    if request.method == 'GET':
        s = DataRepository.read_metingen()
        return jsonify(s), 200


@app.route(endpoint + '/wijzigingen', methods=['GET'])
def read_wijzigingen():
    if request.method == 'GET':
        s = DataRepository.read_wijzigingen()
        return jsonify(s), 200

# SOCKET IO


@socketio.on('connect')
def initial_connection():
    print('A new client connect')
    # # Send to the client!


@socketio.on('F2B_add_hoeveelheid')
def add_hoeveelheid_socket(data):
    fill(data)


@socketio.on('F2B_add_opslag')
def add_opslag_socket(data):
    huidig_settings = DataRepository.read_settings()
    Data = DataRepository.opslag_vullen(huidig_settings['daily_goal'], huidig_settings['daily_range'], (int(huidig_settings['opslag'])+int(data['opslag'])), huidig_settings['appname'])


def fill(data):
    global gewicht_voederbak, gewicht_voederbak_huidig, gewicht_voederbak_live

    hoeveelheid=int(data['hoeveelheid'])
    
    servo=Servo(pin_servo)
    gewicht_voederbak_vorig=max(0, int(hx.get_weight(5)))
    i = 0
    while(gewicht_voederbak_vorig+hoeveelheid >= gewicht_voederbak_live):
        
        if(i%2 == 0):

            servo.start()
            print('rechts')
        else:
            servo.start_links()
            print('links')
        data=DataRepository.servo_on()
        
        print(
            f"Vorig: {gewicht_voederbak_vorig} {hoeveelheid} Huidig gewicht: {gewicht_voederbak_live}")
        data = DataRepository.opslag_legen(hoeveelheid)

        time.sleep(1)
        i += 1

    else:
        servo.stop()
        data=DataRepository.servo_off()
        gewicht_voederbak_vorig=gewicht_voederbak_huidig


def ldr_inlezen():
    waarde_ldr=mcp.read_channel(0)
    
    if(waarde_ldr > 300):
        rgb_led.led_branden([1, 1, 1])
        socketio.emit('B2F_rgb', 1)
        data=DataRepository.ldr_inlezen(waarde_ldr)
    else:
        rgb_led.led_doven()
        socketio.emit('B2F_rgb', 0)

    threading.Timer(5,ldr_inlezen).start()

def gewicht_inlezen_voederbak_setup():
    global gewicht_voederbak
    hx.set_reading_format("MSB", "MSB")
    hx.set_reference_unit(413)
    hx.reset()
    hx.tare()
    
    gewicht_voederbak=max(0, int(hx.get_weight(5)))
    print(gewicht_voederbak)
    gewicht_voederbak_inlezen()

def gewicht_voederbak_inlezen():
    global gewicht_voederbak_live
    gewicht_voederbak_live=max(0, int(hx.get_weight(5)))
    threading.Timer(0.2,gewicht_voederbak_inlezen).start()
    hx.power_down()
    hx.power_up()

def gewicht_inlezen_voederbak():
    global gewicht_voederbak_live, gewicht_voederbak, gewicht_voederbak_huidig, gewicht_voederbak_vorig, daily_goal, daily_range
    
    #gewicht_voederbak_live=max(0, int(hx.get_weight(5)))
    
    socketio.emit('B2F_current_weight_bowl', gewicht_voederbak_live)
    if(gewicht_voederbak_live != gewicht_voederbak_huidig and gewicht_voederbak_live != gewicht_voederbak_huidig+1):
        gewicht_voederbak_huidig=gewicht_voederbak_live

        verschil=gewicht_voederbak_huidig - \
            gewicht_voederbak  # VERSCHIL TUSSEN VORIGE WAARDE
        gewicht_voederbak=gewicht_voederbak_huidig  # NIEUW VASTE WAARDE
        if(verschil < 0):  # pet has eaten
            data=DataRepository.add_eaten(abs(verschil))
            gewicht_voederbak_vorig=gewicht_voederbak
            socketio.emit('B2F_food_eaten', verschil)
        else:
            socketio.emit('B2F_food_add')
        print(
            f"WIJZIGING {gewicht_voederbak_huidig}g - verschil: {verschil}")

    else:
        gewicht_voederbak_huidig=gewicht_voederbak_live

    settings = DataRepository.read_settings()

    if(gewicht_voederbak_live < 25):

        gewicht_gegeten_vandaag=DataRepository.read_feed_today()
        if(gewicht_gegeten_vandaag):
            if(gewicht_gegeten_vandaag['sum_hoeveelheid'] < settings['daily_goal']+settings['daily_range']):
                fill({"hoeveelheid": 5})
                
            else:
                print("Teveel gegeten, voederbak wordt nietmeer automatisch bijgevuld")
            socketio.emit("B2F_feed_today",gewicht_gegeten_vandaag['sum_hoeveelheid'])
        else:
            socketio.emit("B2F_feed_today",0)
            fill({"hoeveelheid": 25})

            
    
    if(settings['opslag'] < 100):
        # print("hoi")
        socketio.emit("B2F_notification","De opslag is bijna leeg! Vul hem zo snel mogelijk aan.")

    # hx.power_down()
    # hx.power_up()
    
def ip_tonen():
    display.write_status()
    threading.Timer(10,ip_tonen).start()

def afstand_meten():
    # afstand=afstandsensor.meten()

    if(10 < 25):
        # print("Beweging voor voederbak")
        gewicht_inlezen_voederbak()
        time.sleep(1)
    else:
        # print("Geen beweging voor voederbak")
        pass
        
    threading.Timer(0.2,afstand_meten).start()

def start_processen():
    gewicht_inlezen_voederbak_setup()
    ldr_inlezen()
    # gewicht_voederbak_proces.start()
    ip_tonen()
    afstand_meten()
    # gewicht_voederbak_inlezen()
    # threading.Timer(2,afstand_meten).start() # wachten met afstand 2 seconden

# Start app
start_processen()
if __name__ == '__main__':
    print("** SmartPET start **")
    try:
        
        socketio.run(app, host="0.0.0.0", port=5000, debug=False)
    except KeyboardInterrupt as ex:
        print(ex)
    finally:
        GPIO.cleanup()
        print("finish")
