from pathlib import Path


# Arduino
ARDUINO_PORTA = "/dev/ttyUSB0"
ARDUINO_BAUD = 115200


# ESP32-CAM
ESP_IP = "192.168.0.107"
ESP_CAPTURE_URL = f"http://{ESP_IP}/capture"


# Pastas
BASE_DIR = Path(__file__).resolve().parent

PASTA_CAPTURAS = BASE_DIR / "capturas"
PASTA_LOGS = BASE_DIR / "logs"


# Tempo mínimo entre duas capturas
COOLDOWN_CAPTURA = 2.0
