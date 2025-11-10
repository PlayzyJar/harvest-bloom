from flask import Flask, jsonify
from flask_cors import CORS
import lgpio
import adafruit_dht
import board
import time
import threading

# --- Configurações de pinos ---
LED_PIN = 18
PUMP_RELAY_PIN = 6
TRIGGER_PIN = 24
ECHO_PIN = 25
LDR_PIN = 21
DHT_PIN = board.D12
READ_INTERVAL = 1.0
HUMIDITY_SETPOINT = 40


# --- Inicialização do GPIO ---
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, LED_PIN)
lgpio.gpio_claim_output(h, PUMP_RELAY_PIN)
lgpio.gpio_write(h, PUMP_RELAY_PIN, 1)
lgpio.gpio_claim_output(h, TRIGGER_PIN)
lgpio.gpio_claim_input(h, ECHO_PIN)
lgpio.gpio_claim_input(h, LDR_PIN)

# --- Inicialização do DHT11 ---
dht_sensor = adafruit_dht.DHT11(DHT_PIN)

# --- Variáveis globais ---
latest_ldr_value = None
stop_thread = False

app = Flask(__name__)
CORS(app)

pump_last_off = 0
pump_on = False


def bomba_auto_control():
    global pump_on, pump_last_off
    while True:
        try:
            humid = dht_sensor.humidity
            # Se leitura falhar, ignora este ciclo
            if humid is None:
                time.sleep(3)
                continue
            # Lógica: liga se abaixo do setpoint, desliga se acima
            if humid < HUMIDITY_SETPOINT and not pump_on:
                lgpio.gpio_write(h, PUMP_RELAY_PIN, 1)
                pump_on = True
                print(f"BOMBA: LIGADA (umidade={humid:.1f}%)")
            elif humid >= HUMIDITY_SETPOINT and pump_on:
                lgpio.gpio_write(h, PUMP_RELAY_PIN, 0)
                pump_on = False
                pump_last_off = time.time()
                print(f"BOMBA: DESLIGADA (umidade={humid:.1f}%)")
        except Exception as e:
            print(f"Erro controle bomba: {e}")
        time.sleep(3)  # Delay entre leituras


t_bomba = threading.Thread(target=bomba_auto_control, daemon=True)
t_bomba.start()

# --- Função de leitura simples de LDR (RC timing) ---


def read_ldr():
    lgpio.gpio_claim_output(h, LDR_PIN)
    lgpio.gpio_write(h, LDR_PIN, 0)
    time.sleep(0.1)
    lgpio.gpio_claim_input(h, LDR_PIN)
    count = 0
    while lgpio.gpio_read(h, LDR_PIN) == 0 and count < 100000:
        count += 1
    return count


# --- Thread para leitura contínua do LDR ---
def ldr_background_task():
    global latest_ldr_value, stop_thread
    print("[INFO] Thread LDR iniciada.")
    while not stop_thread:
        try:
            latest_ldr_value = read_ldr()
            print(f"[LDR] {latest_ldr_value}")
        except Exception as e:
            print(f"[ERRO] Falha LDR: {e}")
        time.sleep(READ_INTERVAL)
    print("[INFO] Thread LDR encerrada.")


# --- Rotas da API ---
@app.route('/api/led/on', methods=['POST'])
def led_on():
    lgpio.gpio_write(h, LED_PIN, 1)
    return jsonify({'status': 'on'})


@app.route('/api/led/off', methods=['POST'])
def led_off():
    lgpio.gpio_write(h, LED_PIN, 0)
    return jsonify({'status': 'off'})


@app.route('/api/led/status', methods=['GET'])
def led_status():
    state = lgpio.gpio_read(h, LED_PIN)
    return jsonify({'status': 'on' if state else 'off'})


@app.route('/api/pump/on', methods=['POST'])
def pump_on():
    """Liga a bomba de irrigação"""
    lgpio.gpio_write(h, PUMP_RELAY_PIN, 1)  # LOW = LIGA relé
    return jsonify({'status': 'on'})


@app.route('/api/pump/off', methods=['POST'])
def pump_off():
    """Desliga a bomba de irrigação"""
    lgpio.gpio_write(h, PUMP_RELAY_PIN, 0)  # HIGH = DESLIGA relé
    return jsonify({'status': 'off'})


@app.route('/api/pump/status', methods=['GET'])
def pump_status():
    """Retorna o estado atual da bomba"""
    state = lgpio.gpio_read(h, PUMP_RELAY_PIN)
    # Se ativo-baixo: 0=on, 1=off
    return jsonify({'status': 'off' if state else 'on'})


@app.route('/api/ldr', methods=['GET'])
def get_ldr_value():
    return jsonify({'ldr': latest_ldr_value})


@app.route('/api/ultrasonic', methods=['GET'])
def get_distance():
    try:
        lgpio.gpio_write(h, TRIGGER_PIN, 1)
        time.sleep(0.00001)
        lgpio.gpio_write(h, TRIGGER_PIN, 0)

        while lgpio.gpio_read(h, ECHO_PIN) == 0:
            pulse_start = time.time()
        while lgpio.gpio_read(h, ECHO_PIN) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 34300 / 2
        return jsonify({'distance_cm': round(distance, 2)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sensor/dht11', methods=['GET'])
def dht11_api():
    try:
        temp = dht_sensor.temperature
        humid = dht_sensor.humidity
        if temp is not None and humid is not None:
            return jsonify({
                "success": True,
                "temperature": temp,
                "humidity": humid,
                "unit_temp": "°C",
                "unit_humid": "%"
            })
        else:
            return jsonify({"success": False, "error": "Leitura inválida"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# --- Execução principal ---
if __name__ == '__main__':
    try:
        ldr_thread = threading.Thread(target=ldr_background_task, daemon=True)
        ldr_thread.start()
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n[INFO] Interrompido pelo usuário.")
    finally:
        stop_thread = True
        lgpio.gpiochip_close(h)
        print("[INFO] GPIO fechado. Encerrando.")
