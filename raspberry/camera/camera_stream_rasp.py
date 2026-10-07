import io
import logging
import socketserver

from http import server
from threading import Condition

from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput


# =========================================================
# PÁGINA HTML
# =========================================================

PAGE = """
<html>

<head>
    <title>Camera Raspberry Pi - Semaforo Inteligente</title>
</head>

<body style="
    text-align:center;
    font-family:Arial;
    background-color:#111;
    color:white;
">

    <h2>Camera Raspberry Pi</h2>

    <p>
        Visualizacao em tempo real
        com enquadramento equivalente ao dataset
    </p>

    <img
        src="/stream.mjpg"
        style="
            width:95%;
            max-width:1200px;
            height:auto;
            border:2px solid white;
        "
    >

</body>

</html>
"""


# =========================================================
# BUFFER DO STREAM
# =========================================================

class StreamingOutput(io.BufferedIOBase):

    def __init__(self):

        self.frame = None
        self.condition = Condition()


    def write(self, buf):

        with self.condition:

            self.frame = buf

            self.condition.notify_all()


# =========================================================
# SERVIDOR HTTP
# =========================================================

class StreamingHandler(server.BaseHTTPRequestHandler):

    def do_GET(self):

        # -------------------------------------------------
        # Página principal
        # -------------------------------------------------

        if self.path == "/":

            content = PAGE.encode("utf-8")

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "text/html"
            )

            self.send_header(
                "Content-Length",
                len(content)
            )

            self.end_headers()

            self.wfile.write(content)


        # -------------------------------------------------
        # Stream MJPEG
        # -------------------------------------------------

        elif self.path == "/stream.mjpg":

            self.send_response(200)

            self.send_header(
                "Age",
                0
            )

            self.send_header(
                "Cache-Control",
                "no-cache, private"
            )

            self.send_header(
                "Pragma",
                "no-cache"
            )

            self.send_header(
                "Content-Type",
                "multipart/x-mixed-replace; boundary=FRAME"
            )

            self.end_headers()


            try:

                while True:

                    with output.condition:

                        output.condition.wait()

                        frame = output.frame


                    self.wfile.write(
                        b"--FRAME\r\n"
                    )

                    self.send_header(
                        "Content-Type",
                        "image/jpeg"
                    )

                    self.send_header(
                        "Content-Length",
                        len(frame)
                    )

                    self.end_headers()

                    self.wfile.write(frame)

                    self.wfile.write(
                        b"\r\n"
                    )


            except Exception as erro:

                logging.warning(
                    "Cliente desconectado: %s",
                    erro
                )


        # -------------------------------------------------
        # Página não encontrada
        # -------------------------------------------------

        else:

            self.send_error(404)

            self.end_headers()


# =========================================================
# SERVIDOR COM MÚLTIPLAS THREADS
# =========================================================

class StreamingServer(
    socketserver.ThreadingMixIn,
    server.HTTPServer
):

    allow_reuse_address = True

    daemon_threads = True


# =========================================================
# CONFIGURAÇÃO DA CÂMERA
# =========================================================

picam2 = Picamera2()


# Resolução usada no stream:
# 2048 x 1536 = formato 4:3
#
# O raw utiliza o sensor inteiro da OV5647:
# 2592 x 1944 = formato 4:3

config = picam2.create_video_configuration(

    main={
        "size": (2048, 1536)
    },

    raw={
        "size": (2592, 1944)
    }
)


picam2.configure(config)


# =========================================================
# INICIA STREAM
# =========================================================

output = StreamingOutput()


picam2.start_recording(

    MJPEGEncoder(),

    FileOutput(output)
)


# =========================================================
# INICIA SERVIDOR WEB
# =========================================================

try:

    endereco = (
        "",
        8000
    )


    servidor = StreamingServer(

        endereco,

        StreamingHandler
    )


    print()
    print("========================================")
    print(" CAMERA RASPBERRY PI")
    print("========================================")
    print()

    print("Resolucao do stream:")
    print("2048 x 1536")

    print()

    print("Resolucao do sensor:")
    print("2592 x 1944")

    print()

    print("Acesse no navegador:")
    print()

    print("http://192.168.0.109:8000")

    print()

    print("Pressione Ctrl+C para encerrar.")

    print()


    servidor.serve_forever()


except KeyboardInterrupt:

    print()
    print("Servidor encerrado.")


finally:

    picam2.stop_recording()
