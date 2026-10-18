from copy import deepcopy
from datetime import datetime
from queue import Queue, Empty
from threading import Lock


# =====================================================
# ESTADO CENTRAL DO SISTEMA
# =====================================================

_estado = {

    "sistema": {
        "bluetooth": False,
        "camera": None,
        "yolo": None,
        "fpga": None,
        "api": True
    },

    "via_aberta": "X",

    "ultima_deteccao": None,

    "ultima_atualizacao": None,

    "vias": {

        "A": {
            "semaforo": "vermelho",
            "sensor": False,

            # Dados futuros do YOLO
            "veiculos": None,
            "congestionamento": None,

            # Dados futuros de prioridade
            "veiculo_prioritario": False,
            "tipo_prioritario": None,
            "tempo_espera": None,
            "prioridade": None
        },

        "B": {
            "semaforo": "vermelho",
            "sensor": False,
            "veiculos": None,
            "congestionamento": None,
            "veiculo_prioritario": False,
            "tipo_prioritario": None,
            "tempo_espera": None,
            "prioridade": None
        },

        "C": {
            "semaforo": "vermelho",
            "sensor": False,
            "veiculos": None,
            "congestionamento": None,
            "veiculo_prioritario": False,
            "tipo_prioritario": None,
            "tempo_espera": None,
            "prioridade": None
        },

        "D": {
            "semaforo": "vermelho",
            "sensor": False,
            "veiculos": None,
            "congestionamento": None,
            "veiculo_prioritario": False,
            "tipo_prioritario": None,
            "tempo_espera": None,
            "prioridade": None
        }
    }
}


_lock = Lock()

_fila_comandos = Queue()


# =====================================================
# DATA/HORA
# =====================================================

def agora():

    return datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )


# =====================================================
# CONSULTAR ESTADO
# =====================================================

def obter_estado():

    with _lock:

        return deepcopy(
            _estado
        )


# =====================================================
# STATUS DOS COMPONENTES
# =====================================================

def atualizar_status(
    componente,
    valor
):

    with _lock:

        _estado["sistema"][
            componente
        ] = valor

        _estado[
            "ultima_atualizacao"
        ] = agora()


# =====================================================
# ESTADO DOS SEMÁFOROS
# =====================================================

def atualizar_semaforos(
    estados
):

    with _lock:

        via_verde = "X"

        for via in [
            "A",
            "B",
            "C",
            "D"
        ]:

            if via not in estados:
                continue

            cor = (
                estados[via]
                .lower()
            )

            _estado[
                "vias"
            ][via][
                "semaforo"
            ] = cor


            if cor == "verde":

                via_verde = via


        _estado[
            "via_aberta"
        ] = via_verde


        _estado[
            "ultima_atualizacao"
        ] = agora()


# =====================================================
# DETECÇÃO DE SENSOR
# =====================================================

def registrar_deteccao(
    via
):

    if via not in [
        "A",
        "B",
        "C",
        "D"
    ]:

        return


    with _lock:

        _estado[
            "ultima_deteccao"
        ] = via

        _estado[
            "vias"
        ][via][
            "sensor"
        ] = True

        _estado[
            "ultima_atualizacao"
        ] = agora()


# =====================================================
# FUTURO: RESULTADO DO YOLO
# =====================================================

def atualizar_dados_via(
    via,
    veiculos=None,
    congestionamento=None,
    veiculo_prioritario=None,
    tipo_prioritario=None
):

    if via not in _estado["vias"]:

        return


    with _lock:

        dados = _estado[
            "vias"
        ][via]


        if veiculos is not None:

            dados[
                "veiculos"
            ] = veiculos


        if congestionamento is not None:

            dados[
                "congestionamento"
            ] = congestionamento


        if veiculo_prioritario is not None:

            dados[
                "veiculo_prioritario"
            ] = veiculo_prioritario


        if tipo_prioritario is not None:

            dados[
                "tipo_prioritario"
            ] = tipo_prioritario


        _estado[
            "ultima_atualizacao"
        ] = agora()


# =====================================================
# COMANDOS DE TESTE
# =====================================================

def enfileirar_comando(
    comando
):

    _fila_comandos.put(
        comando
    )


def obter_comando_pendente():

    try:

        return _fila_comandos.get_nowait()

    except Empty:

        return None
