from copy import deepcopy
from datetime import datetime
from queue import Queue, Empty
from threading import Lock


# =====================================================
# ESTADO GLOBAL DO SISTEMA
# =====================================================

_lock = Lock()
_fila_comandos = Queue()


_estado = {

    "sistema": {
        "bluetooth": False,
        "camera": False,
        "yolo": False,
        "fpga": None,
        "api": True,
    },

    "via_aberta": "X",

    "ultima_deteccao": None,

    "ultima_atualizacao": None,

    # Fila aguardando atendimento.
    "fila": [],

    "vias": {

        "A": {
            "semaforo": "vermelho",
            "sensor": False,
            "veiculos": None,
            "congestionamento": None,
            "veiculo_prioritario": False,
            "tipo_prioritario": None,
            "tempo_espera": None,
            "prioridade": None,
        },

        "B": {
            "semaforo": "vermelho",
            "sensor": False,
            "veiculos": None,
            "congestionamento": None,
            "veiculo_prioritario": False,
            "tipo_prioritario": None,
            "tempo_espera": None,
            "prioridade": None,
        },

        "C": {
            "semaforo": "vermelho",
            "sensor": False,
            "veiculos": None,
            "congestionamento": None,
            "veiculo_prioritario": False,
            "tipo_prioritario": None,
            "tempo_espera": None,
            "prioridade": None,
        },

        "D": {
            "semaforo": "vermelho",
            "sensor": False,
            "veiculos": None,
            "congestionamento": None,
            "veiculo_prioritario": False,
            "tipo_prioritario": None,
            "tempo_espera": None,
            "prioridade": None,
        },
    },
}


# =====================================================
# FUNCOES INTERNAS
# =====================================================

def _agora():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def _atualizar_timestamp():
    _estado["ultima_atualizacao"] = _agora()


# =====================================================
# LEITURA DO ESTADO
# =====================================================

def obter_estado():

    with _lock:
        return deepcopy(_estado)


# =====================================================
# STATUS DOS COMPONENTES
# =====================================================

def atualizar_status(componente, valor):

    with _lock:

        if componente in _estado["sistema"]:
            _estado["sistema"][componente] = valor

        _atualizar_timestamp()


# =====================================================
# DETECCAO DOS SENSORES
# =====================================================

def registrar_deteccao(via):

    via = via.upper()

    if via not in _estado["vias"]:
        return

    with _lock:

        # Deixa somente a ultima via detectada marcada.
        for nome_via in _estado["vias"]:
            _estado["vias"][nome_via]["sensor"] = False

        _estado["vias"][via]["sensor"] = True

        _estado["ultima_deteccao"] = via

        _atualizar_timestamp()


# =====================================================
# FILA
# =====================================================

def atualizar_fila(fila):

    with _lock:

        _estado["fila"] = list(fila)

        _atualizar_timestamp()


# =====================================================
# ESTADO DOS SEMAFOROS
# =====================================================

def atualizar_semaforos(estados):

    with _lock:

        via_aberta = "X"

        for via, cor in estados.items():

            via = via.upper()
            cor = cor.lower()

            if via not in _estado["vias"]:
                continue

            _estado["vias"][via]["semaforo"] = cor

            if cor == "verde":
                via_aberta = via

        _estado["via_aberta"] = via_aberta

        _atualizar_timestamp()


# =====================================================
# DADOS FUTUROS DO YOLO
# =====================================================

def atualizar_dados_via(
    via,
    veiculos=None,
    congestionamento=None,
    veiculo_prioritario=False,
    tipo_prioritario=None,
    tempo_espera=None,
    prioridade=None,
):

    via = via.upper()

    if via not in _estado["vias"]:
        return

    with _lock:

        dados = _estado["vias"][via]

        if veiculos is not None:
            dados["veiculos"] = veiculos

        if congestionamento is not None:
            dados["congestionamento"] = congestionamento

        dados["veiculo_prioritario"] = veiculo_prioritario
        dados["tipo_prioritario"] = tipo_prioritario
        dados["tempo_espera"] = tempo_espera
        dados["prioridade"] = prioridade

        _atualizar_timestamp()


# =====================================================
# COMANDOS RECEBIDOS PELO DASHBOARD
# =====================================================

def enfileirar_comando(comando):

    if comando is None:
        return

    comando = comando.strip().upper()

    if comando:
        _fila_comandos.put(comando)


def obter_comando_pendente():

    try:
        return _fila_comandos.get_nowait()

    except Empty:
        return None
