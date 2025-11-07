from flask import Flask, jsonify
from flask_cors import CORS
import RPi.GPIO as GPIO
import threading
import time
from gpiozero import LED, DistanceSensor
import board
import adafruit_dht

app = Flask(__name__)
CORS(app)

# --- Configurações ---
LDR_PIN = 21  # mesmo pino usado no teste-LDR.py
MAX_COUNT = 1000000
READ_INTERVAL = 1  # intervalo de leitura em segundos
LED_PIN = 18

# --- Inicialização de periféricos ---
led = LED(LED_PIN)
sensor = DistanceSensor(echo=25, trigger=24, max_distance=2)

# --- Variáveis globais ---
latest_ldr_value = None
stop_thread = False
gpio_lock = threading.Lock()

# --- Função idêntica ao seu teste-LDR.py ---


def read_ldr(pin=LDR_PIN):
    reading = 0
    with gpio_lock:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.1)
        GPIO.setup(pin, GPIO.IN)
        while GPIO.input(pin) == GPIO.LOW and reading < MAX_COUNT:
            reading += 1
    return reading

# --- Thread para leitura contínua ---


def ldr_background_task():
    global latest_ldr_value, stop_thread
    print("[INFO] Thread de leitura LDR iniciada.")
    while not stop_thread:
        try:
            valor = read_ldr()
            latest_ldr_value = valor
            print(f"[LDR] Valor lido: {valor}")
        except Exception as e:
            print(f"[ERRO] Falha ao ler LDR: {e}")
        time.sleep(READ_INTERVAL)
    print("[INFO] Thread de leitura LDR encerrada.")

# --- Rotas da API ---


@app.route('/api/ldr', methods=['GET'])
def get_ldr_value():
    if latest_ldr_value is None:
        return jsonify({'ldr': None, 'status': 'aguardando leitura'})
    return jsonify({'ldr': latest_ldr_value})


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


@app.route('/api/sensor/dht11', methods=['GET'])
def dht11_api():
    try:
        # Altere para outro GPIO se necessário
        sensor = adafruit_dht.DHT11(board.D12)
        temp = sensor.temperature
        humid = sensor.humidity
        sensor.exit()
        if temp is not None and humid is not None:
            return jsonify({
                "success": True,
                "temperature": temp,
                "humidity": humid,
                "unit_temp": "°C",
                "unit_humid": "%"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Leitura do DHT11 inválida"
            }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro ao acessar o DHT11: {e}"
        }), 500


# --- Execução principal ---
if __name__ == '__main__':
    try:
        # Inicia a thread em segundo plano
        ldr_thread = threading.Thread(target=ldr_background_task, daemon=True)
        ldr_thread.start()

        # Inicia o servidor Flask
        app.run(host='0.0.0.0', port=5000)

    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.")

    finally:
        stop_thread = True
        GPIO.cleanup()
        print("[INFO] GPIO limpo, encerrando o programa.")
