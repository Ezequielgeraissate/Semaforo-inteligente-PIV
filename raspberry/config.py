from pathlib import Path


# =====================================================
# DIRETORIOS
# =====================================================

BASE_DIR = Path(
    __file__
).resolve().parent


PASTA_CAPTURAS = (
    BASE_DIR
    / "capturas"
)


PASTA_LOGS = (
    BASE_DIR
    / "logs"
)


# =====================================================
# BLUETOOTH HC-05
# =====================================================

HC05_MAC = "20:18:07:20:05:40"

HC05_CHANNEL = 1


# Porta criada pelo RFCOMM
ARDUINO_PORTA = "/dev/rfcomm0"

# Comunicação UART do HC-05
ARDUINO_BAUD = 9600


# =====================================================
# CAMERA RASPBERRY
# =====================================================

CAMERA_WIDTH = 2048

CAMERA_HEIGHT = 1536

CAMERA_TIMEOUT_MS = 1000


# Intervalo mínimo entre capturas
COOLDOWN_CAPTURA = 2.0


# =====================================================
# DASHBOARD
# =====================================================

DASHBOARD_HOST = "0.0.0.0"

DASHBOARD_PORT = 8000


# =====================================================
# YOLO
# =====================================================

# False enquanto seu colega
# ainda estiver integrando o modelo
YOLO_HABILITADO = True
