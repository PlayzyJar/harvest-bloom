from flask import Flask, jsonify
from flask_cors import CORS
from gpiozero import LED

app = Flask(__name__)
CORS(app)

LED_PIN = 18   # Coloque o número BCM do GPIO que está usando
led = LED(LED_PIN)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
