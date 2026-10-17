import time

from comunicacao.bluetooth_arduino import (
    ArduinoBluetooth
)

from camera.camera_rasp import (
    capturar_imagem
)

from yolo.adapter import (
    analisar_imagem
)

from config import (
    COOLDOWN_CAPTURA
)


def main():

    print(
        "=============================="
    )

    print(
        " SISTEMA SEMAFORO INTELIGENTE "
    )

    print(
        "=============================="
    )

    print()


    arduino = None


    try:

        # ============================================
        # BLUETOOTH
        # ============================================

        arduino = ArduinoBluetooth()


        print()

        print(
            "Testando comunicacao Bluetooth..."
        )


        if not arduino.testar_conexao():

            raise RuntimeError(
                "Arduino nao respondeu PONG "
                "pelo Bluetooth."
            )


        print(
            "Bluetooth Raspberry <-> Arduino: OK"
        )

        print()


        # ============================================
        # CAPTURA
        # ============================================

        ultima_captura = 0


        print(
            "Aguardando deteccao "
            "dos sensores..."
        )

        print()


        # ============================================
        # LOOP PRINCIPAL
        # ============================================

        while True:

            mensagem = (
                arduino.ler()
            )


            if mensagem is None:

                time.sleep(0.05)

                continue


            print(
                "Arduino -> Raspberry: "
                f"{mensagem}"
            )


            # Só processa eventos dos sensores

            if not mensagem.startswith(
                "DETECCAO:"
            ):

                continue


            agora = time.time()


            # Evita várias fotos
            # quase simultâneas

            if (
                agora
                - ultima_captura
                < COOLDOWN_CAPTURA
            ):

                print(
                    "Deteccao ignorada "
                    "(intervalo entre capturas)."
                )

                continue


            # ========================================
            # VIA
            # ========================================

            via_sensor = (

                mensagem

                .split(
                    ":",
                    1
                )[1]

                .strip()
            )


            print()

            print(
                f"Sensor da Via {via_sensor} "
                "detectou um veiculo."
            )


            try:

                # ====================================
                # 1. CAPTURA OV5647
                # ====================================

                imagem = capturar_imagem(
                    via_sensor
                )


                ultima_captura = (
                    time.time()
                )


                # ====================================
                # 2. YOLO
                # ====================================

                print(
                    "Enviando imagem para "
                    "o YOLO-FastestV2..."
                )


                resultado = analisar_imagem(
                    imagem
                )


                # ====================================
                # 3. RESULTADO
                # ====================================

                print()

                print(
                    "Resultado recebido:"
                )

                print(
                    resultado
                )


            except Exception as erro:

                print()

                print(
                    f"Erro no pipeline: {erro}"
                )


            print()

            print(
                "Aguardando nova deteccao..."
            )


    except KeyboardInterrupt:

        print()

        print(
            "Sistema encerrado."
        )


    finally:

        if arduino is not None:

            arduino.fechar()


if __name__ == "__main__":

    main()
