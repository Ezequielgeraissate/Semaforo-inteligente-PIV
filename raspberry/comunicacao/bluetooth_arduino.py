import time

from pathlib import Path

import serial

from config import (
    ARDUINO_PORTA,
    ARDUINO_BAUD
)


class ArduinoBluetooth:

    def __init__(self):

        # Verifica se RFCOMM existe
        if not Path(
            ARDUINO_PORTA
        ).exists():

            raise RuntimeError(
                f"{ARDUINO_PORTA} não existe. "
                "Conecte o HC-05 via RFCOMM."
            )


        self.serial = serial.Serial(
            ARDUINO_PORTA,
            ARDUINO_BAUD,
            timeout=0.2
        )


        time.sleep(0.5)


        # Remove mensagens antigas
        self.serial.reset_input_buffer()

        self.serial.reset_output_buffer()


        print(
            "Arduino conectado por Bluetooth "
            f"em {ARDUINO_PORTA}"
        )


    # =================================================
    # ENVIAR
    # =================================================

    def enviar(
        self,
        mensagem
    ):

        texto = str(
            mensagem
        ).strip()


        self.serial.write(
            (
                texto
                + "\n"
            ).encode("utf-8")
        )


        self.serial.flush()


        print(
            f"Raspberry -> Arduino: {texto}"
        )


    # =================================================
    # RECEBER
    # =================================================

    def ler(self):

        if (
            self.serial.in_waiting
            == 0
        ):

            return None


        linha = (
            self.serial
            .readline()
            .decode(
                errors="ignore"
            )
            .strip()
        )


        if linha:

            return linha


        return None


    # =================================================
    # TESTE P -> PONG
    # =================================================

    def testar_conexao(
        self,
        timeout=3.0
    ):

        # Descarta dados antigos
        self.serial.reset_input_buffer()


        self.enviar("P")


        limite = (
            time.time()
            + timeout
        )


        while (
            time.time()
            < limite
        ):

            mensagem = self.ler()


            if mensagem is None:

                time.sleep(0.05)

                continue


            print(
                "Arduino -> Raspberry: "
                f"{mensagem}"
            )


            if mensagem == "PONG":

                return True


        return False


    # =================================================
    # FECHAR
    # =================================================

    def fechar(self):

        if self.serial.is_open:

            self.serial.close()
