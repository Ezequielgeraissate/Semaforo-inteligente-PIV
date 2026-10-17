from pathlib import Path


# =====================================================
# BLUETOOTH HC-05
# =====================================================

HC05_MAC = "20:18:07:20:05:40"

HC05_CHANNEL = 1


# Porta criada pelo RFCOMM
ARDUINO_PORTA = "/dev/rfcomm0"

# UART do HC-05
ARDUINO_BAUD = 9600


# =====================================================
# CAMERA OV5647
# =====================================================

CAMERA_WIDTH = 2048

CAMERA_HEIGHT = 1536

CAMERA_TIMEOUT_MS = 1000


# =====================================================
# PASTAS
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
# CAPTURA
# =====================================================

COOLDOWN_CAPTURA = 2.0
