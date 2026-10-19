from pathlib import Path


# =====================================================
# DIRETORIOS
# =====================================================

BASE_DIR = Path(__file__).resolve().parent

PASTA_CAPTURAS = BASE_DIR / "capturas"
PASTA_LOGS = BASE_DIR / "logs"


# =====================================================
# BLUETOOTH HC-05
# =====================================================

HC05_MAC = "20:18:07:20:05:40"
HC05_CHANNEL = 1

ARDUINO_PORTA = "/dev/rfcomm0"
ARDUINO_BAUD = 9600


# =====================================================
# CAMERA
# =====================================================

# Nesta versao temporaria a camera NAO sera utilizada.
CAMERA_HABILITADA = False

CAMERA_WIDTH = 2048
CAMERA_HEIGHT = 1536
CAMERA_TIMEOUT_MS = 1000


# =====================================================
# YOLO
# =====================================================

YOLO_HABILITADO = False


# =====================================================
# DASHBOARD
# =====================================================

DASHBOARD_HOST = "0.0.0.0"
DASHBOARD_PORT = 8000


# =====================================================
# TESTE TEMPORARIO - FILA DE VIAS
# =====================================================

# Tempo que cada via permanece verde.
TEMPO_VERDE_TESTE = 5.0

# Intervalo do loop principal.
LOOP_DELAY = 0.05
