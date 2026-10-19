import threading
import time
from collections import deque

import uvicorn

from config import (
    DASHBOARD_HOST,
    DASHBOARD_PORT,
    TEMPO_VERDE_TESTE,
    LOOP_DELAY,
)

from comunicacao.bluetooth_arduino import ArduinoBluetooth

from dashboard.api import app

from estado_sistema import (
    atualizar_fila,
    atualizar_semaforos,
    atualizar_status,
    enfileirar_comando,
    obter_comando_pendente,
    registrar_deteccao,
)


# =====================================================
# FILA FIFO DAS VIAS
# =====================================================

fila_vias = deque()

via_em_atendimento = None

inicio_verde = None


# =====================================================
# DASHBOARD
# =====================================================

def iniciar_dashboard():

    print()
    print(
        f"Dashboard iniciado em "
        f"http://0.0.0.0:{DASHBOARD_PORT}"
    )
    print()

    uvicorn.run(
        app,
        host=DASHBOARD_HOST,
        port=DASHBOARD_PORT,
        log_level="warning",
    )


# =====================================================
# FILA
# =====================================================

def adicionar_via_na_fila(via):

    global fila_vias
    global via_em_atendimento

    via = via.strip().upper()

    if via not in ("A", "B", "C", "D"):
        return

    # Nao adiciona a via se ela ja estiver sendo atendida.
    if via == via_em_atendimento:

        print(
            f"Via {via} ja esta em atendimento."
        )

        return

    # Nao permite a mesma via duas vezes na fila.
    if via in fila_vias:

        print(
            f"Via {via} ja esta aguardando na fila."
        )

        return

    fila_vias.append(via)

    atualizar_fila(
        list(fila_vias)
    )

    print(
        f"Via {via} adicionada na fila."
    )

    print(
        "Fila atual:",
        list(fila_vias),
    )


# =====================================================
# INTERPRETACAO DO ESTADO DOS SEMAFOROS
# =====================================================

def processar_estado_semaforos(mensagem):

    global inicio_verde
    global via_em_atendimento

    # Exemplo:
    #
    # SEMAFOROS:A=VERDE,B=VERMELHO,C=VERMELHO,D=VERMELHO

    dados = mensagem.replace(
        "SEMAFOROS:",
        "",
        1,
    )

    estados = {}

    for item in dados.split(","):

        if "=" not in item:
            continue

        via, cor = item.split(
            "=",
            1,
        )

        via = via.strip().upper()
        cor = cor.strip().lower()

        estados[via] = cor

    atualizar_semaforos(
        estados
    )

    # Inicia a contagem dos 5 segundos somente
    # quando a via realmente ficar VERDE.
    if via_em_atendimento is not None:

        cor_atual = estados.get(
            via_em_atendimento
        )

        if (
            cor_atual == "verde"
            and inicio_verde is None
        ):

            inicio_verde = time.time()

            print(
                f"Via {via_em_atendimento} ficou VERDE."
            )

            print(
                f"Tempo de atendimento: "
                f"{TEMPO_VERDE_TESTE} segundos."
            )


# =====================================================
# PROCESSAMENTO DAS MENSAGENS DO ARDUINO
# =====================================================

def processar_mensagem_arduino(
    mensagem,
):

    if not mensagem:
        return

    mensagem = mensagem.strip()

    print(
        f"Arduino -> Raspberry: {mensagem}"
    )

    # -------------------------------------------------
    # SENSOR
    # -------------------------------------------------

    if mensagem.startswith(
        "DETECCAO:"
    ):

        partes = mensagem.split(
            ":",
            1,
        )

        if len(partes) != 2:
            return

        via = partes[1].strip().upper()

        registrar_deteccao(
            via
        )

        adicionar_via_na_fila(
            via
        )

        return

    # -------------------------------------------------
    # SEMAFOROS
    # -------------------------------------------------

    if mensagem.startswith(
        "SEMAFOROS:"
    ):

        processar_estado_semaforos(
            mensagem
        )

        return

    # -------------------------------------------------
    # PONG
    # -------------------------------------------------

    if mensagem == "PONG":

        atualizar_status(
            "bluetooth",
            True,
        )

        return


# =====================================================
# PROCESSAMENTO DA FILA
# =====================================================

def processar_fila(
    arduino,
):

    global via_em_atendimento
    global inicio_verde
    global fila_vias

    agora = time.time()

    # -------------------------------------------------
    # NAO HA VIA SENDO ATENDIDA
    # -------------------------------------------------

    if (
        via_em_atendimento is None
        and fila_vias
    ):

        via_em_atendimento = (
            fila_vias.popleft()
        )

        inicio_verde = None

        atualizar_fila(
            list(fila_vias)
        )

        print()
        print(
            "================================"
        )

        print(
            f"Iniciando Via "
            f"{via_em_atendimento}"
        )

        print(
            "================================"
        )

        arduino.enviar(
            via_em_atendimento
        )

        print(
            f"Raspberry -> Arduino: "
            f"{via_em_atendimento}"
        )

        return

    # -------------------------------------------------
    # ESPERANDO A VIA FICAR VERDE
    # -------------------------------------------------

    if via_em_atendimento is None:
        return

    if inicio_verde is None:
        return

    # -------------------------------------------------
    # VIA AINDA ESTA DENTRO DO TEMPO
    # -------------------------------------------------

    tempo_decorrido = (
        agora
        - inicio_verde
    )

    if (
        tempo_decorrido
        < TEMPO_VERDE_TESTE
    ):
        return

    # -------------------------------------------------
    # EXISTE OUTRA VIA NA FILA
    # -------------------------------------------------

    if fila_vias:

        proxima_via = (
            fila_vias.popleft()
        )

        atualizar_fila(
            list(fila_vias)
        )

        print()
        print(
            f"Tempo da Via "
            f"{via_em_atendimento} terminou."
        )

        print(
            f"Proxima via da fila: "
            f"{proxima_via}"
        )

        # O Arduino recebe a nova via.
        #
        # A maquina de estados do Arduino faz:
        #
        # verde atual
        # -> amarelo
        # -> todos vermelhos
        # -> proxima via verde

        via_em_atendimento = (
            proxima_via
        )

        inicio_verde = None

        arduino.enviar(
            proxima_via
        )

        print(
            f"Raspberry -> Arduino: "
            f"{proxima_via}"
        )

        return

    # -------------------------------------------------
    # FILA VAZIA
    # -------------------------------------------------

    print()
    print(
        f"Tempo da Via "
        f"{via_em_atendimento} terminou."
    )

    print(
        "Fila vazia."
    )

    print(
        "Fechando todas as vias."
    )

    arduino.enviar(
        "X"
    )

    print(
        "Raspberry -> Arduino: X"
    )

    via_em_atendimento = None
    inicio_verde = None

    atualizar_fila([])


# =====================================================
# COMANDOS DO DASHBOARD
# =====================================================

def processar_comando_dashboard(
    arduino,
):

    global fila_vias
    global via_em_atendimento
    global inicio_verde

    comando = (
        obter_comando_pendente()
    )

    if comando is None:
        return

    comando = comando.upper()

    # A, B, C e D entram na mesma fila.
    if comando in (
        "A",
        "B",
        "C",
        "D",
    ):

        adicionar_via_na_fila(
            comando
        )

        return

    # X limpa tudo.
    if comando == "X":

        fila_vias.clear()

        atualizar_fila([])

        via_em_atendimento = None
        inicio_verde = None

        arduino.enviar(
            "X"
        )

        print(
            "Dashboard -> X"
        )

        return

    # S solicita estado ao Arduino.
    if comando == "S":

        arduino.enviar(
            "S"
        )

        print(
            "Dashboard -> S"
        )


# =====================================================
# PROGRAMA PRINCIPAL
# =====================================================

def main():

    arduino = None

    print()
    print(
        "================================"
    )

    print(
        " SEMAFORO INTELIGENTE"
    )

    print(
        " TESTE DE FILA SEM CAMERA"
    )

    print(
        "================================"
    )

    print()

    # -------------------------------------------------
    # DASHBOARD
    # -------------------------------------------------

    thread_dashboard = threading.Thread(
        target=iniciar_dashboard,
        daemon=True,
    )

    thread_dashboard.start()

    time.sleep(
        1
    )

    # -------------------------------------------------
    # BLUETOOTH
    # -------------------------------------------------

    try:

        arduino = ArduinoBluetooth()

        atualizar_status(
            "bluetooth",
            True,
        )

        atualizar_status(
            "camera",
            False,
        )

        atualizar_status(
            "yolo",
            False,
        )

        print(
            "Arduino conectado por Bluetooth."
        )

        print()

        # Teste PING/PONG.
        print(
            "Testando Bluetooth..."
        )

        if arduino.testar_conexao():

            print(
                "Bluetooth Raspberry "
                "<-> Arduino: OK"
            )

        else:

            print(
                "Aviso: PONG nao recebido."
            )

        # Solicita estado inicial.
        arduino.enviar(
            "S"
        )

        print(
            "Raspberry -> Arduino: S"
        )

        print()
        print(
            "Sistema pronto."
        )

        print(
            "Aguardando sensores..."
        )

        print()

        # ---------------------------------------------
        # LOOP PRINCIPAL
        # ---------------------------------------------

        while True:

            # Recebe uma mensagem do Arduino.
            mensagem = arduino.ler()

            if mensagem:

                processar_mensagem_arduino(
                    mensagem
                )

            # Comandos vindos da API/dashboard.
            processar_comando_dashboard(
                arduino
            )

            # Processa a fila FIFO.
            processar_fila(
                arduino
            )

            time.sleep(
                LOOP_DELAY
            )

    except KeyboardInterrupt:

        print()
        print(
            "Sistema encerrado pelo usuario."
        )

    except Exception as erro:

        print()
        print(
            "ERRO:"
        )

        print(
            erro
        )

    finally:

        atualizar_status(
            "bluetooth",
            False,
        )

        if arduino is not None:

            try:
                arduino.fechar()

            except Exception:
                pass


# =====================================================
# EXECUCAO
# =====================================================

if __name__ == "__main__":
    main()
