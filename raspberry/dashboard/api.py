from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import HTTPException

from estado_sistema import (
    obter_estado,
    enfileirar_comando
)


# =====================================================
# CAMINHOS
# =====================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
)

STATIC_DIR = (
    BASE_DIR
    / "static"
)


# =====================================================
# FASTAPI
# =====================================================

app = FastAPI(
    title="Semáforo Inteligente",
    version="1.0"
)


# =====================================================
# ARQUIVOS DO FRONT-END
# =====================================================

app.mount(
    "/static",
    StaticFiles(
        directory=STATIC_DIR
    ),
    name="static"
)


# =====================================================
# DASHBOARD
# =====================================================

@app.get("/")
def dashboard():

    return FileResponse(
        STATIC_DIR
        / "index.html"
    )


# =====================================================
# ESTADO DO SISTEMA
# =====================================================

@app.get("/api/status")
def status():

    return obter_estado()


# =====================================================
# COMANDO DE TESTE
# =====================================================

@app.post(
    "/api/comando/{comando}"
)
def enviar_comando(
    comando: str
):

    comando = (
        comando
        .upper()
        .strip()
    )


    permitidos = [
        "A",
        "B",
        "C",
        "D",
        "X",
        "S"
    ]


    if comando not in permitidos:

        raise HTTPException(
            status_code=400,
            detail="Comando inválido"
        )


    enfileirar_comando(
        comando
    )


    return {
        "enviado": comando
    }
