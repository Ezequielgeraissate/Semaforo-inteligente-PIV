import json
import subprocess

from pathlib import Path


RASPBERRY_DIR = (
    Path(
        __file__
    )
    .resolve()
    .parents[1]
)


YOLO_DIR = (
    Path(
        __file__
    )
    .resolve()
    .parent
)


# =====================================================
# EXECUTAVEIS POSSIVEIS
# =====================================================

EXECUTAVEIS_CANDIDATOS = [

    YOLO_DIR
    / "modelo"
    / "yolo_fastest",

    YOLO_DIR
    / "teste"
    / "modelo"
    / "yolo_fastest"
]


# =====================================================
# LOCALIZAR EXECUTAVEL
# =====================================================

def _encontrar_executavel():

    for caminho in (
        EXECUTAVEIS_CANDIDATOS
    ):

        if caminho.exists():

            return caminho


    candidatos = "\n".join(

        f"- {caminho}"

        for caminho
        in EXECUTAVEIS_CANDIDATOS
    )


    raise RuntimeError(

        "Executavel YOLO nao encontrado.\n"
        "Caminhos verificados:\n"
        + candidatos
    )


# =====================================================
# EXTRAIR JSON
# =====================================================

def _extrair_json(
    stdout
):

    """
    O C++ pode imprimir mensagens de debug
    antes do JSON.

    Procuramos de baixo para cima a última
    linha que seja um JSON válido.
    """

    linhas = [

        linha.strip()

        for linha
        in stdout.splitlines()

        if linha.strip()
    ]


    for linha in reversed(
        linhas
    ):

        try:

            resultado = (
                json.loads(
                    linha
                )
            )

        except json.JSONDecodeError:

            continue


        if isinstance(
            resultado,
            list
        ):

            return resultado


    raise RuntimeError(

        "O YOLO executou, mas nao devolveu "
        "uma lista JSON valida.\n\n"
        f"Saida recebida:\n{stdout}"
    )


# =====================================================
# ANALISAR IMAGEM
# =====================================================

def analisar_imagem(
    caminho_imagem
):

    executavel = (
        _encontrar_executavel()
    )


    caminho_imagem = (
        Path(
            caminho_imagem
        )
        .resolve()
    )


    processo = subprocess.run(

        [
            str(
                executavel
            ),

            str(
                caminho_imagem
            )
        ],

        cwd=RASPBERRY_DIR,

        capture_output=True,

        text=True
    )


    if processo.returncode != 0:

        raise RuntimeError(

            processo.stderr.strip()

            or

            processo.stdout.strip()

            or

            "Erro desconhecido ao executar YOLO."
        )


    return _extrair_json(
        processo.stdout
    )
