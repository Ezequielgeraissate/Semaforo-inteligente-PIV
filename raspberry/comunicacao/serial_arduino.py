import serial
import time

from config import ARDUINO_PORTA, ARDUINO_BAUD


class ArduinoSerial:

    def __init__(self):

        self.serial = serial.Serial(
            ARDUINO_PORTA,
            ARDUINO_BAUD,
            timeout=1
        )

        # Arduino pode reiniciar ao abrir a serial
        time.sleep(2)

        self.serial.reset_input_buffer()

        print(
            f"Arduino conectado em {ARDUINO_PORTA}"
        )


    def ler(self):

        if self.serial.in_waiting == 0:
            return None

        linha = (
            self.serial
            .readline()
            .decode(errors="ignore")
            .strip()
        )

        return linha if linha else None
