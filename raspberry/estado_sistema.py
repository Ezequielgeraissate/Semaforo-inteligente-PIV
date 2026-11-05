from copy import deepcopy
from datetime import datetime
from queue import Queue, Empty
from threading import Lock
import time


VIAS = (
    "A",
    "B",
    "C",
    "D"
)


# =====================================================
# ESTADO CENTRAL
# =====================================================

_estado = {

    "sistema": {

        "bluetooth": False,

        "camera": None,

        "yolo": None,

        "fpga": None,

        "api": True
    },


    "via_aberta":
        "X",


    "ultima_deteccao":
        None,


    "ultima_atualizacao":
        None,


    # Resultado mais recente da decisão.
    "decisao": {

        "via": None,

        "motivo": None,

        "pontuacao": 0.0,

        "pontuacoes": {}
    },


    "vias": {

        via: {

            "semaforo":
                "vermelho",

            "sensor":
                False,


            # IA
            "veiculos":
                0,

            "congestionamento":
                "livre",

            "deteccoes":
                [],


            # Prioridade
            "veiculo_prioritario":
                False,

            "tipo_prioritario":
                None,

            "tempo_espera":
                0.0,

            "prioridade":
                0.0,


            # Controle interno
            "inicio_espera":
                None
        }

        for via in VIAS
    }
}


_lock = Lock()

_fila_comandos = Queue()


# =====================================================
# DATA E HORA
# =====================================================

def agora():

    return datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )


def _atualizar_timestamp_sem_lock():

    _estado[
        "ultima_atualizacao"
    ] = agora()


# =====================================================
# TEMPO DE ESPERA
# =====================================================

def _atualizar_tempos_sem_lock():

    instante = time.time()


    for via in VIAS:

        dados = (
            _estado[
                "vias"
            ][via]
        )


        inicio = dados.get(
            "inicio_espera"
        )


        if inicio is None:

            dados[
                "tempo_espera"
            ] = 0.0

            continue


        dados[
            "tempo_espera"
        ] = round(

            max(
                0.0,
                instante
                - inicio
            ),

            1
        )


def _iniciar_espera_sem_lock(
    via
):

    dados = (
        _estado[
            "vias"
        ][via]
    )


    if (
        dados.get(
            "inicio_espera"
        )
        is None
    ):

        dados[
            "inicio_espera"
        ] = time.time()


        dados[
            "tempo_espera"
        ] = 0.0


def _encerrar_espera_sem_lock(
    via
):

    dados = (
        _estado[
            "vias"
        ][via]
    )


    dados[
        "inicio_espera"
    ] = None


    dados[
        "tempo_espera"
    ] = 0.0


# =====================================================
# CONSULTAR ESTADO
# =====================================================

def obter_estado():

    with _lock:

        _atualizar_tempos_sem_lock()

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

        _estado[
            "sistema"
        ][
            componente
        ] = valor


        _atualizar_timestamp_sem_lock()


# =====================================================
# SEMAFOROS
# =====================================================

def atualizar_semaforos(
    estados
):

    """
    Compatibilidade com versões do Arduino que enviam:

    SEMAFOROS:A=VERDE,B=VERMELHO,...
    """

    with _lock:

        via_verde = "X"


        for via in VIAS:

            if via not in estados:

                continue


            cor = str(
                estados[
                    via
                ]
            ).lower()


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


        if via_verde in VIAS:

            _encerrar_espera_sem_lock(
                via_verde
            )


        _atualizar_timestamp_sem_lock()


# =====================================================
# VIA ABERTA
# =====================================================

def atualizar_via_aberta(
    via
):

    """
    Protocolo usado pelo Arduino da branch:

    VIA_ABERTA:A
    VIA_ABERTA:B
    VIA_ABERTA:C
    VIA_ABERTA:D
    VIA_ABERTA:N
    """

    via = str(
        via
    ).upper().strip()


    if via == "N":

        via = "X"


    if via not in (
        *VIAS,
        "X"
    ):

        return


    with _lock:

        _estado[
            "via_aberta"
        ] = via


        for nome_via in VIAS:

            _estado[
                "vias"
            ][
                nome_via
            ][
                "semaforo"
            ] = (

                "verde"

                if nome_via == via

                else "vermelho"
            )


        if via in VIAS:

            _encerrar_espera_sem_lock(
                via
            )


        _atualizar_timestamp_sem_lock()


# =====================================================
# SENSOR
# =====================================================

def registrar_deteccao(
    via
):

    via = str(
        via
    ).upper().strip()


    if via not in VIAS:

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


        _iniciar_espera_sem_lock(
            via
        )


        _atualizar_timestamp_sem_lock()


# =====================================================
# ESTADO DOS QUATRO SENSORES
# =====================================================

def atualizar_sensores(
    estados
):

    with _lock:

        for via in VIAS:

            if via not in estados:

                continue


            ativo = bool(
                estados[
                    via
                ]
            )


            dados = (
                _estado[
                    "vias"
                ][via]
            )


            dados[
                "sensor"
            ] = ativo


            if ativo:

                _iniciar_espera_sem_lock(
                    via
                )


            elif (
                int(
                    dados.get(
                        "veiculos"
                    )
                    or 0
                )
                <= 0
            ):

                _encerrar_espera_sem_lock(
                    via
                )


        _atualizar_timestamp_sem_lock()


# =====================================================
# DADOS DE UMA VIA
# =====================================================

def atualizar_dados_via(
    via,
    veiculos=None,
    congestionamento=None,
    veiculo_prioritario=None,
    tipo_prioritario=None,
    deteccoes=None,
    prioridade=None
):

    via = str(
        via
    ).upper().strip()


    if via not in VIAS:

        return


    with _lock:

        dados = (
            _estado[
                "vias"
            ][via]
        )


        if veiculos is not None:

            dados[
                "veiculos"
            ] = int(
                veiculos
            )


        if congestionamento is not None:

            dados[
                "congestionamento"
            ] = congestionamento


        if veiculo_prioritario is not None:

            dados[
                "veiculo_prioritario"
            ] = bool(
                veiculo_prioritario
            )


        if (
            tipo_prioritario
            is not None
            or
            veiculo_prioritario
            is False
        ):

            dados[
                "tipo_prioritario"
            ] = tipo_prioritario


        if deteccoes is not None:

            dados[
                "deteccoes"
            ] = deepcopy(
                deteccoes
            )


        if prioridade is not None:

            dados[
                "prioridade"
            ] = round(
                float(
                    prioridade
                ),
                2
            )


        if (
            int(
                dados.get(
                    "veiculos"
                )
                or 0
            )
            > 0
        ):

            _iniciar_espera_sem_lock(
                via
            )


        elif not dados.get(
            "sensor",
            False
        ):

            _encerrar_espera_sem_lock(
                via
            )


        _atualizar_timestamp_sem_lock()


# =====================================================
# RESULTADO COMPLETO DO YOLO
# =====================================================

def atualizar_resultado_yolo(
    resumo
):

    if isinstance(
        resumo,
        dict
    ):

        vias_resultado = (
            resumo.get(
                "vias",
                {}
            )
        )

    else:

        vias_resultado = {}


    with _lock:

        for via in VIAS:

            novo = (
                vias_resultado.get(
                    via,
                    {}
                )
            )


            dados = (
                _estado[
                    "vias"
                ][via]
            )


            dados[
                "veiculos"
            ] = int(
                novo.get(
                    "veiculos",
                    0
                )
                or 0
            )


            dados[
                "congestionamento"
            ] = novo.get(
                "congestionamento",
                "livre"
            )


            dados[
                "veiculo_prioritario"
            ] = bool(
                novo.get(
                    "veiculo_prioritario",
                    False
                )
            )


            dados[
                "tipo_prioritario"
            ] = novo.get(
                "tipo_prioritario"
            )


            dados[
                "deteccoes"
            ] = deepcopy(
                novo.get(
                    "deteccoes",
                    []
                )
            )


            if (
                dados[
                    "veiculos"
                ]
                > 0
            ):

                _iniciar_espera_sem_lock(
                    via
                )


            elif not dados.get(
                "sensor",
                False
            ):

                _encerrar_espera_sem_lock(
                    via
                )


        _atualizar_timestamp_sem_lock()


# =====================================================
# DECISAO
# =====================================================

def registrar_decisao(
    decisao
):

    if not isinstance(
        decisao,
        dict
    ):

        return


    with _lock:

        _estado[
            "decisao"
        ] = deepcopy(
            decisao
        )


        pontuacoes = (
            decisao.get(
                "pontuacoes",
                {}
            )
        )


        for via in VIAS:

            componentes = (
                pontuacoes.get(
                    via,
                    {}
                )
            )


            _estado[
                "vias"
            ][via][
                "prioridade"
            ] = round(

                float(
                    componentes.get(
                        "total",
                        0.0
                    )
                    or 0.0
                ),

                2
            )


        _atualizar_timestamp_sem_lock()


# =====================================================
# COMANDOS DO DASHBOARD
# =====================================================

def enfileirar_comando(
    comando
):

    _fila_comandos.put(
        comando
    )


def obter_comando_pendente():

    try:

        return (
            _fila_comandos
            .get_nowait()
        )

    except Empty:

        return None
