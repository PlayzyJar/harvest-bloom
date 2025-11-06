from flask import Flask, jsonify
from flask_cors import CORS
from gpiozero import LED, DistanceSensor
import RPi.GPIO as GPIO
import time

app = Flask(__name__)
CORS(app)

LED_PIN = 18
led = LED(LED_PIN)

sensor = DistanceSensor(echo=25, trigger=24, max_distance=2)

LDR_PIN = 21  # GPIO21 (BCM), pino físico 40. Troque conforme sua ligação
MAX_COUNT = 1000000


def read_ldr(pin=LDR_PIN):
    GPIO.setmode(GPIO.BCM)
    reading = 0
    try:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.1)
        GPIO.setup(pin, GPIO.IN)
        while GPIO.input(pin) == GPIO.LOW and reading < MAX_COUNT:
            reading += 1
        return reading
    except Exception as e:
        print(f"Erro ao ler LDR: {e}")
        return -1
    finally:
        GPIO.cleanup()


@app.route('/api/ldr', methods=['GET'])
def ldr_value():
    valor = read_ldr()
    return jsonify({'ldr': valor})


@app.route('/api/led/on', methods=['POST'])
def led_on():
    led.on()
    return jsonify({'status': 'on'})


@app.route('/api/led/off', methods=['POST'])
def led_off():
    led.off()
    return jsonify({'status': 'off'})


@app.route('/api/led/status', methods=['GET'])
def led_status():
    return jsonify({'status': 'on' if led.is_lit else 'off'})


@app.route('/api/ultrasonic', methods=['GET'])
def get_distance():
    dist = sensor.distance * 100
    return jsonify({'distance_cm': round(dist, 1)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
