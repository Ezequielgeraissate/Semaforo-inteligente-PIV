import json
import os
import threading
import time

from datetime import datetime

import uvicorn


from camera.camera_rasp import capturar_imagem

from comunicacao.bluetooth_arduino import ArduinoBluetooth

from config import (
    COOLDOWN_CAPTURA,
    DASHBOARD_HOST,
    DASHBOARD_PORT,
    DECISAO_AUTOMATICA_HABILITADA,
    INTERVALO_MIN_DECISAO,
    INTERVALO_STATUS_ARDUINO,
    MANTER_IMAGENS_TESTE,
    PASTA_LOGS,
    YOLO_HABILITADO
)

from dashboard.api import app

from decisao.logica_decisao import decidir_via
from decisao.mapeamento_vias import mapear_deteccoes

from estado_sistema import (
    atualizar_resultado_yolo,
    atualizar_semaforos,
    atualizar_sensores,
    atualizar_status,
    atualizar_via_aberta,
    obter_comando_pendente,
    obter_estado,
    registrar_decisao,
    registrar_deteccao
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
# SEMAFOROS
# =====================================================

def processar_semaforos(mensagem):

    payload = mensagem.split(":", 1)[1]

    estados = {}

    for item in payload.split(","):

        if "=" not in item:
            continue

        via, cor = item.split("=", 1)

        estados[
            via.strip().upper()
        ] = cor.strip().lower()

    atualizar_semaforos(estados)


# =====================================================
# VIA ABERTA
# =====================================================

def processar_via_aberta(mensagem):

    via = (
        mensagem
        .split(":", 1)[1]
        .strip()
        .upper()
    )

    atualizar_via_aberta(via)


# =====================================================
# SENSORES
# =====================================================

def processar_sensores(mensagem):

    payload = mensagem.split(":", 1)[1]

    valores = [
        valor.strip()
        for valor in payload.split(",")
    ]

    if len(valores) < 4:
        return

    estados = {}

    for via, valor in zip(
        ("A", "B", "C", "D"),
        valores[:4]
    ):

        estados[via] = valor in (
            "1",
            "true",
            "True",
            "HIGH"
        )

    atualizar_sensores(estados)


# =====================================================
# LOG
# =====================================================

def salvar_log_analise(
    via_gatilho,
    resultado_yolo,
    mapeamento,
    decisao
):

    PASTA_LOGS.mkdir(
        parents=True,
        exist_ok=True
    )

    momento = datetime.now()

    caminho_log = (
        PASTA_LOGS
        / f"log_decisao_{momento.strftime('%Y-%m-%d')}.jsonl"
    )

    registro = {
        "hora": momento.strftime("%H:%M:%S"),
        "via_gatilho": via_gatilho,
        "yolo": resultado_yolo,
        "mapeamento": mapeamento,
        "decisao": decisao
    }

    with open(
        caminho_log,
        "a",
        encoding="utf-8"
    ) as arquivo:

        arquivo.write(
            json.dumps(
                registro,
                ensure_ascii=False
            )
            + "\n"
        )


# =====================================================
# MOSTRAR DECISAO
# =====================================================

def imprimir_decisao(
    mapeamento,
    decisao
):

    print()
    print("========== ANALISE DAS VIAS ==========")

    for via in ("A", "B", "C", "D"):

        dados = mapeamento["vias"][via]

        componentes = (
            decisao
            .get("pontuacoes", {})
            .get(via, {})
        )

        print(
            f"Via {via}: "
            f"veiculos={dados['veiculos']} | "
            f"congestionamento={dados['congestionamento']} | "
            f"prioritario={dados['veiculo_prioritario']} | "
            f"pontos={componentes.get('total', 0)}"
        )

    print()

    if decisao.get("via"):

        print(
            f"DECISAO: VIA {decisao['via']} | "
            f"motivo={decisao['motivo']} | "
            f"pontuacao={decisao['pontuacao']}"
        )

    else:

        print(
            "DECISAO: nenhuma via com demanda."
        )

    print("======================================")
    print()


# =====================================================
# MAIN
# =====================================================

def main():

    print("==============================")
    print(" SISTEMA SEMAFORO INTELIGENTE ")
    print("==============================")
    print()

    iniciar_dashboard()

    print(
        f"Dashboard iniciado na porta "
        f"{DASHBOARD_PORT}"
    )

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

        arduino.enviar("S")


        # ============================================
        # TEMPORIZADORES
        # ============================================

        ultima_captura = 0.0
        ultima_decisao_enviada = 0.0
        ultima_consulta_status = time.time()

        print()
        print("Aguardando eventos...")


        # ============================================
        # LOOP
        # ============================================

        while True:

            agora_loop = time.time()


            # ========================================
            # CONSULTAR ARDUINO
            # ========================================

            if (
                agora_loop
                - ultima_consulta_status
                >= INTERVALO_STATUS_ARDUINO
            ):

                arduino.enviar("S")

                ultima_consulta_status = (
                    agora_loop
                )


            # ========================================
            # COMANDO DO DASHBOARD
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
            # RECEBER MENSAGEM
            # ========================================

            mensagem = arduino.ler()

            if mensagem is None:

                time.sleep(0.03)

                continue

            print(
                f"Arduino -> Raspberry: "
                f"{mensagem}"
            )


            # ========================================
            # SENSORES
            # ========================================

            if mensagem.startswith(
                "SENSORES:"
            ):

                processar_sensores(
                    mensagem
                )

                continue


            # ========================================
            # VIA ABERTA
            # ========================================

            if mensagem.startswith(
                "VIA_ABERTA:"
            ):

                processar_via_aberta(
                    mensagem
                )

                continue


            # ========================================
            # SEMAFOROS
            # ========================================

            if mensagem.startswith(
                "SEMAFOROS:"
            ):

                processar_semaforos(
                    mensagem
                )

                continue


            # ========================================
            # DETECCAO
            # ========================================

            if not mensagem.startswith(
                "DETECCAO:"
            ):

                continue


            via_gatilho = (
                mensagem
                .split(":", 1)[1]
                .strip()
                .upper()
            )

            registrar_deteccao(
                via_gatilho
            )


            # ========================================
            # COOLDOWN DA CAMERA
            # ========================================

            agora_captura = time.time()

            if (
                agora_captura
                - ultima_captura
                < COOLDOWN_CAPTURA
            ):

                continue


            imagem = None

            try:

                # ====================================
                # CAMERA
                # ====================================

                imagem = capturar_imagem(
                    via_gatilho
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


                # ====================================
                # YOLO
                # ====================================

                if not YOLO_HABILITADO:

                    print(
                        "YOLO desabilitado."
                    )

                    continue


                from yolo.adapter import (
                    analisar_imagem
                )


                resultado_yolo = (
                    analisar_imagem(
                        imagem
                    )
                )


                atualizar_status(
                    "yolo",
                    True
                )


                print(
                    f"YOLO encontrou "
                    f"{len(resultado_yolo)} "
                    "deteccoes."
                )


                # ====================================
                # POSICAO -> VIA
                # ====================================

                mapeamento = (
                    mapear_deteccoes(
                        resultado_yolo
                    )
                )


                atualizar_resultado_yolo(
                    mapeamento
                )


                # ====================================
                # DECISAO
                # ====================================

                estado = obter_estado()


                decisao = decidir_via(

                    estado["vias"],

                    estado["via_aberta"]
                )


                registrar_decisao(
                    decisao
                )


                imprimir_decisao(
                    mapeamento,
                    decisao
                )


                # ====================================
                # ENVIAR PARA O ARDUINO
                # ====================================

                via_decidida = (
                    decisao.get("via")
                )

                via_aberta = (
                    estado.get(
                        "via_aberta",
                        "X"
                    )
                )

                momento_decisao = (
                    time.time()
                )


                if (
                    via_decidida
                    and
                    via_decidida != via_aberta
                    and
                    (
                        momento_decisao
                        - ultima_decisao_enviada
                        >= INTERVALO_MIN_DECISAO
                    )
                ):

                    if (
                        DECISAO_AUTOMATICA_HABILITADA
                    ):

                        print(
                            "Decisao automatica -> "
                            f"Arduino: Via "
                            f"{via_decidida}"
                        )

                        arduino.enviar(
                            via_decidida
                        )

                        ultima_decisao_enviada = (
                            momento_decisao
                        )

                    else:

                        print(
                            "MODO TESTE: "
                            "decisao calculada, "
                            "mas nao enviada -> "
                            f"VIA {via_decidida}"
                        )


                # ====================================
                # SALVAR LOG
                # ====================================

                salvar_log_analise(
                    via_gatilho,
                    resultado_yolo,
                    mapeamento,
                    decisao
                )


            except Exception as erro:

                texto = str(erro).lower()

                if (
                    "camera" in texto
                    or
                    "rpicam" in texto
                ):

                    atualizar_status(
                        "camera",
                        False
                    )

                else:

                    atualizar_status(
                        "yolo",
                        False
                    )

                print(
                    "Erro no pipeline:",
                    erro
                )


            finally:

                # ====================================
                # APAGAR OU MANTER FOTO
                # ====================================

                if (
                    imagem is not None
                    and
                    os.path.exists(imagem)
                    and
                    not MANTER_IMAGENS_TESTE
                ):

                    os.remove(imagem)

                    print(
                        f"Imagem {imagem} apagada."
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


if __name__ == "__main__":

    main()
