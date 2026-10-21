import threading
import time

import uvicorn

import os
import json
from datetime import datetime

from comunicacao.bluetooth_arduino import (
    ArduinoBluetooth
)

from camera.camera_rasp import (
    capturar_imagem
)

from dashboard.api import (
    app
)

from estado_sistema import (
    atualizar_status,
    atualizar_semaforos,
    registrar_deteccao,
    obter_comando_pendente
)

from config import (
    COOLDOWN_CAPTURA,
    DASHBOARD_HOST,
    DASHBOARD_PORT,
    YOLO_HABILITADO,
    PASTA_LOGS
)


# =====================================================
# DASHBOARD
# =====================================================

def iniciar_dashboard():

    def servidor():

        uvicorn.run(

            app,

            host=DASHBOARD_HOST,

            port=DASHBOARD_PORT,

            log_level="warning"
        )


    thread = threading.Thread(

        target=servidor,

        daemon=True
    )


    thread.start()


# =====================================================
# INTERPRETAR ESTADO DOS SEMÁFOROS
# =====================================================

def processar_semaforos(
    mensagem
):

    # Exemplo:
    #
    # SEMAFOROS:
    # A=VERDE,
    # B=VERMELHO,
    # C=VERMELHO,
    # D=VERMELHO


    payload = (
        mensagem
        .split(
            ":",
            1
        )[1]
    )


    estados = {}


    for item in payload.split(","):

        if "=" not in item:

            continue


        via, cor = (
            item.split(
                "=",
                1
            )
        )


        via = via.strip()

        cor = (
            cor
            .strip()
            .lower()
        )


        estados[via] = cor


    atualizar_semaforos(
        estados
    )


# =====================================================
# MAIN
# =====================================================

def main():

    print(
        "================================"
    )

    print(
        " SISTEMA SEMAFORO INTELIGENTE "
    )

    print(
        "================================"
    )

    print()


    # ================================================
    # INICIAR DASHBOARD
    # ================================================

    iniciar_dashboard()


    print(
        f"Dashboard iniciado na porta "
        f"{DASHBOARD_PORT}"
    )

    print()


    arduino = None


    try:

        # ============================================
        # BLUETOOTH
        # ============================================

        arduino = ArduinoBluetooth()


        atualizar_status(
            "bluetooth",
            True
        )


        print(
            "Testando comunicacao Bluetooth..."
        )


        if not arduino.testar_conexao():

            raise RuntimeError(
                "Arduino nao respondeu PONG."
            )


        print(
            "Bluetooth Raspberry <-> Arduino: OK"
        )


        # Solicita estado inicial

        arduino.enviar(
            "S"
        )


        # ============================================
        # LOOP
        # ============================================

        ultima_captura = 0


        print()

        print(
            "Aguardando eventos..."
        )


        while True:

            # ========================================
            # COMANDO DE TESTE VINDO DA API
            # ========================================

            comando = (
                obter_comando_pendente()
            )


            if comando:

                print(
                    f"Dashboard -> Arduino: "
                    f"{comando}"
                )

                arduino.enviar(
                    comando
                )


            # ========================================
            # BLUETOOTH
            # ========================================

            mensagem = (
                arduino.ler()
            )


            if mensagem is None:

                time.sleep(0.03)

                continue


            print(
                "Arduino -> Raspberry: "
                f"{mensagem}"
            )


            # ========================================
            # SEMÁFOROS
            # ========================================

            if mensagem.startswith(
                "SEMAFOROS:"
            ):

                processar_semaforos(
                    mensagem
                )

                continue


            # ========================================
            # SENSOR
            # ========================================

            if mensagem.startswith(
                "DETECCAO:"
            ):

                via = (

                    mensagem

                    .split(
                        ":",
                        1
                    )[1]

                    .strip()
                )


                registrar_deteccao(
                    via
                )


                agora = time.time()


                if (
                    agora
                    - ultima_captura
                    < COOLDOWN_CAPTURA
                ):

                    continue


                try:

                    # =================================
                    # CAPTURA
                    # =================================

                    imagem = (
                        capturar_imagem(
                            via
                        )
                    )


                    atualizar_status(
                        "camera",
                        True
                    )


                    ultima_captura = (
                        time.time()
                    )


                    print(
                        f"Imagem capturada: "
                        f"{imagem}"
                    )


                    # =================================
                    # YOLO
                    # =================================

                    if YOLO_HABILITADO:

                        from yolo.adapter import analisar_imagem

                        # 1. Roda o modelo na imagem recém tirada
                        resultado = analisar_imagem(imagem)

                        atualizar_status("yolo", True)

                        print("Resultado YOLO processado.")

                        # 2. Criar a pasta de logs caso ela não exista
                        PASTA_LOGS.mkdir(parents=True, exist_ok=True)
                        
                        # Nome do arquivo de log separado por dia
                        hoje = datetime.now()
                        caminho_log = PASTA_LOGS / f"log_posicoes_{hoje.strftime('%Y-%m-%d')}.txt"

                        # 3. Escrever as informações no Log
                        with open(caminho_log, "a", encoding="utf-8") as arquivo_log:
                            hora = hoje.strftime("%H:%M:%S")
                            # Salva a hora, a via detectada e o JSON com classe/bbox devolvido pelo C++
                            arquivo_log.write(f"[{hora}] Via: {via} | Veiculos: {json.dumps(resultado)}\n")

                        # 4. Apagar a imagem processada para liberar espaço no SD
                        if os.path.exists(imagem):
                            os.remove(imagem)
                            print(f"-> Imagem {imagem} apagada. SD salvo!")

                    else:

                        print("YOLO aguardando integracao do modelo.")


                except Exception as erro:

                    print(
                        "Erro no pipeline:",
                        erro
                    )


    except KeyboardInterrupt:

        print()

        print(
            "Sistema encerrado."
        )


    except Exception as erro:

        print(
            "Erro:",
            erro
        )


    finally:

        atualizar_status(
            "bluetooth",
            False
        )


        if arduino is not None:

            arduino.fechar()


# =====================================================
# EXECUÇÃO
# =====================================================

if __name__ == "__main__":

    main()
