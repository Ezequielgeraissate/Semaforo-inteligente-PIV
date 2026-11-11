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

CAMERA_WIDTH = 2048
CAMERA_HEIGHT = 1536
CAMERA_TIMEOUT_MS = 1000

COOLDOWN_CAPTURA = 2.0


# =====================================================
# MODO DE TESTE
# =====================================================

# False:
# calcula tudo, mas NÃO manda a decisão ao Arduino.
#
# True:
# envia automaticamente A/B/C/D.
DECISAO_AUTOMATICA_HABILITADA = False


# True:
# mantém as imagens para conferência.
MANTER_IMAGENS_TESTE = True


# =====================================================
# DASHBOARD
# =====================================================

DASHBOARD_HOST = "0.0.0.0"
DASHBOARD_PORT = 8000


# =====================================================
# YOLO
# =====================================================

YOLO_HABILITADO = True

YOLO_CLASSES = {
    0: "veiculo",
    1: "especial"
}

YOLO_SCORE_MIN = 0.0

CLASSES_PRIORITARIAS = {
    "especial"
}


# =====================================================
# REGIOES DAS VIAS
# =====================================================
#
# VALORES PROVISORIOS.
#
# Precisaremos recalibrar usando uma imagem real
# capturada pela câmera na posição definitiva.
#

REGIOES_VIAS = {

    "A": [
        (0.33, 0.00),
        (0.67, 0.00),
        (0.58, 0.42),
        (0.42, 0.42)
    ],

    "B": [
        (0.58, 0.42),
        (1.00, 0.33),
        (1.00, 0.67),
        (0.58, 0.58)
    ],

    "C": [
        (0.42, 0.58),
        (0.58, 0.58),
        (0.67, 1.00),
        (0.33, 1.00)
    ],

    "D": [
        (0.00, 0.33),
        (0.42, 0.42),
        (0.42, 0.58),
        (0.00, 0.67)
    ]
}


# =====================================================
# CONGESTIONAMENTO
# =====================================================

LIMIARES_CONGESTIONAMENTO = {
    "baixo": 2,
    "moderado": 4
}


# =====================================================
# LOGICA DE DECISAO
# =====================================================

PESO_VEICULO = 10.0
PESO_ESPERA = 0.20
PESO_SENSOR = 1.0
PESO_VEICULO_PRIORITARIO = 100.0

BONUS_MANTER_VIA = 2.0

TEMPO_ESPERA_MAX_PONTUACAO = 120.0

INTERVALO_MIN_DECISAO = 5.0
INTERVALO_STATUS_ARDUINO = 1.0
