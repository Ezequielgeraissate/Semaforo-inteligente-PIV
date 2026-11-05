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

YOLO_HABILITADO = True


# =====================================================
# MAPEAMENTO DAS VIAS NA IMAGEM
# =====================================================

# Classes utilizadas pelo modelo.
#
# IMPORTANTE:
# confirmar posteriormente se a ordem usada
# no treinamento foi realmente:
#
# 0 = veiculo
# 1 = especial
YOLO_CLASSES = {
    0: "veiculo",
    1: "especial"
}


# A saída do C++ já utiliza threshold.
YOLO_SCORE_MIN = 0.0


# Classes que recebem prioridade especial.
CLASSES_PRIORITARIAS = {
    "especial"
}


# =====================================================
# REGIOES DAS VIAS
# =====================================================
#
# Coordenadas NORMALIZADAS:
#
# (0.0, 0.0) = canto superior esquerdo
# (1.0, 1.0) = canto inferior direito
#
# Estas regiões são apenas uma calibração INICIAL.
#
# Quando tivermos uma foto real da câmera instalada
# na posição definitiva da maquete, vamos ajustar
# os polígonos corretamente.
#
#              VIA A
#
#        ┌─────────────────┐
#        │      \   /      │
#        │       \ /       │
# VIA D  │        X        │ VIA B
#        │       / \       │
#        │      /   \      │
#        └─────────────────┘
#
#              VIA C
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

    # 1 ou 2 veículos
    "baixo": 2,

    # 3 ou 4 veículos
    "moderado": 4

    # Acima disso = alto
}


# =====================================================
# LOGICA DE DECISAO
# =====================================================

# Cada veículo vale 10 pontos.
PESO_VEICULO = 10.0


# Cada segundo esperando acrescenta
# 0.20 ponto.
PESO_ESPERA = 0.20


# Sensor ativo acrescenta 1 ponto.
PESO_SENSOR = 1.0


# Veículo especial recebe grande prioridade.
PESO_VEICULO_PRIORITARIO = 100.0


# Pequeno bônus para manter a via que
# já está aberta e evitar trocas desnecessárias.
BONUS_MANTER_VIA = 2.0


# Limite de tempo usado na pontuação.
TEMPO_ESPERA_MAX_PONTUACAO = 120.0


# Impede envio de comandos em sequência muito rápida.
INTERVALO_MIN_DECISAO = 5.0


# Solicita periodicamente o estado ao Arduino.
INTERVALO_STATUS_ARDUINO = 1.0
