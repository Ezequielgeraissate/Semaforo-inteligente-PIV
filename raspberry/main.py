import time

from comunicacao.serial_arduino import ArduinoSerial
from comunicacao.camera_esp import capturar_imagem

from yolo.adapter import analisar_imagem

from config import COOLDOWN_CAPTURA


def main():

    print("==============================")
    print(" SISTEMA SEMÁFORO INTELIGENTE ")
    print("==============================")
    print()

    arduino = ArduinoSerial()

    ultima_captura = 0

    print()
    print("Aguardando detecção dos sensores...")
    print()


    while True:

        mensagem = arduino.ler()

        if mensagem is None:
            time.sleep(0.05)
            continue


        print(
            f"Arduino -> {mensagem}"
        )


        # Só interessa mensagem de detecção
        if not mensagem.startswith("DETECCAO:"):
            continue


        agora = time.time()

        # Evita várias fotos quase simultâneas
        if (
            agora - ultima_captura
            < COOLDOWN_CAPTURA
        ):

            print(
                "Detecção ignorada "
                "(intervalo entre capturas)."
            )

            continue


        via_sensor = (
            mensagem
            .split(":")[1]
            .strip()
        )


        print()
        print(
            f"Sensor da Via {via_sensor} "
            "detectou um veículo."
        )


        try:

            # ==========================
            # 1. CAPTURA
            # ==========================

            imagem = capturar_imagem(
                via_sensor
            )

            ultima_captura = time.time()


            # ==========================
            # 2. ENTREGA AO YOLO
            # ==========================

            print(
                "Enviando imagem para "
                "o módulo YOLO-FastestV2..."
            )

            resultado = analisar_imagem(
                imagem
            )


            # ==========================
            # 3. RESULTADO
            # ==========================

            print()
            print("Resultado recebido:")

            print(resultado)


        except Exception as erro:

            print()
            print(
                f"Erro no pipeline: {erro}"
            )


        print()
        print(
            "Aguardando nova detecção..."
        )


if __name__ == "__main__":
    main()
