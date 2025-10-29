import board
import adafruit_dht
from flask import Blueprint, jsonify

api = Blueprint('api', __name__)

# Configure o pino GPIO de acordo com seu hardware
dhtDevice = adafruit_dht.DHT11(board.D4)  # Use board.D4 para GPIO4


@api.route("/sensor", methods=["GET"])
def get_sensor_data():
    try:
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity
        return jsonify({
            "temperature": temperature,
            "humidity": humidity
        })
    except Exception as e:
        return jsonify({"error": f"Falha na leitura do sensor DHT11: {str(e)}"}), 500
