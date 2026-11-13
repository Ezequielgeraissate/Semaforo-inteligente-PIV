"""
Teste sequencial completo do Semáforo Inteligente.

REGRAS:

1. Uma imagem é processada pelo YOLO uma única vez.
2. As vias ocupadas dessa imagem formam uma fila.
3. Veículo prioritário é atendido primeiro.
4. Cada via da fila recebe:
       VERDE    = 5 segundos
       AMARELO  = 2 segundos
       TODOS VERMELHOS = 1 segundo
5. A próxima imagem só é processada depois que TODAS
   as vias ocupadas da imagem atual forem atendidas.
6. Arduino/Bluetooth não são acionados neste teste.
"""

import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

import cv2
import uvicorn

from dashboard.api import app

from estado_sistema import (
    atualizar_resultado_yolo,
    registrar_decisao,
    atualizar_semaforos,
    atualizar_status,
    obter_estado,
)


# =====================================================
# CONFIGURAÇÃO
# =====================================================

BASE = Path(__file__).resolve().parent

VIAS = (
    "A",
    "B",
    "C",
    "D",
)


TEMPO_VERDE = 5.0
TEMPO_AMARELO = 2.0
TEMPO_TODOS_VERMELHOS = 1.0


# Resolução usada atualmente pelo sistema.
LARGURA_PIPELINE = 2048
ALTURA_PIPELINE = 1536


# Imagem leve enviada ao navegador.
LARGURA_DASHBOARD = 1000


# =====================================================
# IMAGENS DO TESTE
# =====================================================

PREFIXOS = [

    "imagem_0090",

    "imagem_0087",

    "imagem_0088",

    "imagem_0089",

    "imagem_0080_ambulancia_carros6",

    "imagem_0081_ambulancia_carros7",
]


# =====================================================
# PASTAS
# =====================================================

PASTAS_ORIGEM = [

    BASE
    / "capturas"
    / "testes_dataset",

    BASE
    / "capturas"
    / "sequencia_teste",

    BASE
    / "capturas"
    / "testes",
]


PASTA_PREPARADAS = (
    BASE
    / "capturas"
    / "sequencia_fsm"
)


PASTA_DASHBOARD = (
    BASE
    / "capturas"
    / "sequencia_dashboard"
)


IMAGEM_DASHBOARD = (
    PASTA_DASHBOARD
    / "imagem_atual.jpg"
)


IMAGEM_DASHBOARD_TEMP = (
    PASTA_DASHBOARD
    / "imagem_atual.tmp.jpg"
)


# =====================================================
# DASHBOARD
# =====================================================

def iniciar_dashboard():

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="warning",
        access_log=False
    )


# =====================================================
# LOCALIZAR IMAGEM
# =====================================================

def localizar_imagem(
    prefixo
):

    for pasta in PASTAS_ORIGEM:

        if not pasta.exists():

            continue


        candidatos = sorted(
            pasta.glob(
                prefixo
                + "*.jpg"
            )
        )


        # Evita pegar arquivos gerados de visualização.
        candidatos = [

            arquivo

            for arquivo in candidatos

            if (
                "_yolo"
                not in arquivo.stem

                and

                "_regioes"
                not in arquivo.stem

                and

                "_mapeamento"
                not in arquivo.stem
            )
        ]


        if candidatos:

            return candidatos[0]


    return None


# =====================================================
# PREPARAR IMAGEM PARA O PIPELINE
# =====================================================

def preparar_imagem(
    prefixo
):

    origem = (
        localizar_imagem(
            prefixo
        )
    )


    if origem is None:

        raise FileNotFoundError(
            f"Imagem não encontrada: {prefixo}"
        )


    imagem = cv2.imread(
        str(
            origem
        )
    )


    if imagem is None:

        raise RuntimeError(
            f"Não foi possível abrir: {origem}"
        )


    # Todas as imagens entram no pipeline
    # exatamente com a mesma resolução.
    imagem = cv2.resize(

        imagem,

        (
            LARGURA_PIPELINE,
            ALTURA_PIPELINE
        ),

        interpolation=
            cv2.INTER_AREA
    )


    PASTA_PREPARADAS.mkdir(
        parents=True,
        exist_ok=True
    )


    destino = (
        PASTA_PREPARADAS
        /
        f"{prefixo}.jpg"
    )


    cv2.imwrite(
        str(
            destino
        ),
        imagem,
        [
            cv2.IMWRITE_JPEG_QUALITY,
            92
        ]
    )


    return destino


# =====================================================
# IMAGEM LEVE DO DASHBOARD
# =====================================================

def atualizar_imagem_dashboard(
    caminho
):

    imagem = cv2.imread(
        str(
            caminho
        )
    )


    if imagem is None:

        print(
            "[ERRO] Imagem do dashboard não abriu."
        )

        return


    altura, largura = (
        imagem.shape[:2]
    )


    escala = (
        LARGURA_DASHBOARD
        / float(
            largura
        )
    )


    nova_altura = int(
        altura
        * escala
    )


    imagem = cv2.resize(

        imagem,

        (
            LARGURA_DASHBOARD,
            nova_altura
        ),

        interpolation=
            cv2.INTER_AREA
    )


    PASTA_DASHBOARD.mkdir(
        parents=True,
        exist_ok=True
    )


    # Escreve primeiro no temporário.
    cv2.imwrite(

        str(
            IMAGEM_DASHBOARD_TEMP
        ),

        imagem,

        [
            cv2.IMWRITE_JPEG_QUALITY,
            76
        ]
    )


    # Troca atômica.
    os.replace(

        IMAGEM_DASHBOARD_TEMP,

        IMAGEM_DASHBOARD
    )


# =====================================================
# PIPELINE REAL
# =====================================================

def executar_pipeline(
    imagem
):

    processo = subprocess.run(

        [
            sys.executable,

            str(
                BASE
                / "testar_pipeline_imagem.py"
            ),

            str(
                imagem
            )
        ],

        cwd=str(
            BASE
        ),

        capture_output=True,
        text=True
    )


    return (

        processo.stdout
        +
        processo.stderr
    )


# =====================================================
# INTERPRETAR O RESULTADO
# =====================================================

def interpretar_pipeline(
    texto
):

    vias = {}


    for via in VIAS:

        padrao = (

            rf"Via {via}:"
            rf"\s*(\d+)"
            rf"\s*veiculos"

            rf"\s*\|\s*"
            rf"prioritario="
            rf"(True|False)"

            rf"\s*\|\s*"
            rf"congestionamento="
            rf"([^\s]+)"
        )


        resultado = re.search(
            padrao,
            texto
        )


        if resultado:

            veiculos = int(
                resultado.group(1)
            )


            prioritario = (
                resultado.group(2)
                ==
                "True"
            )


            congestionamento = (
                resultado.group(3)
            )

        else:

            veiculos = 0
            prioritario = False
            congestionamento = "livre"


        vias[
            via
        ] = {

            "veiculos":
                veiculos,

            "veiculo_prioritario":
                prioritario,

            "tipo_prioritario":
                (
                    "especial"

                    if prioritario

                    else None
                ),

            "congestionamento":
                congestionamento,

            "deteccoes":
                []
        }


    resultado_fora = re.search(

        r"Fora das vias:"
        r"\s*(\d+)",

        texto
    )


    fora = (

        int(
            resultado_fora.group(1)
        )

        if resultado_fora

        else 0
    )


    return {

        "vias":
            vias,

        "fora":
            fora
    }


# =====================================================
# MONTAR FILA DA IMAGEM
# =====================================================

def montar_fila(
    resumo
):

    vias = (
        resumo.get(
            "vias",
            {}
        )
    )


    prioritarias = []

    normais = []


    for indice, via in enumerate(
        VIAS
    ):

        dados = (
            vias.get(
                via,
                {}
            )
        )


        quantidade = int(
            dados.get(
                "veiculos",
                0
            )
            or 0
        )


        if quantidade <= 0:

            continue


        registro = {

            "via":
                via,

            "veiculos":
                quantidade,

            "indice":
                indice,

            "prioritario":
                bool(
                    dados.get(
                        "veiculo_prioritario",
                        False
                    )
                )
        }


        if registro[
            "prioritario"
        ]:

            prioritarias.append(
                registro
            )

        else:

            normais.append(
                registro
            )


    # Dentro de cada grupo:
    #
    # 1. mais veículos primeiro;
    # 2. em empate mantém A/B/C/D.
    prioritarias.sort(

        key=lambda item: (
            -item[
                "veiculos"
            ],
            item[
                "indice"
            ]
        )
    )


    normais.sort(

        key=lambda item: (
            -item[
                "veiculos"
            ],
            item[
                "indice"
            ]
        )
    )


    return (
        prioritarias
        +
        normais
    )


# =====================================================
# ESTADOS DOS SEMÁFOROS
# =====================================================

def todos_vermelhos():

    atualizar_semaforos({

        "A":
            "vermelho",

        "B":
            "vermelho",

        "C":
            "vermelho",

        "D":
            "vermelho",
    })


def abrir_via(
    via
):

    estados = {

        "A":
            "vermelho",

        "B":
            "vermelho",

        "C":
            "vermelho",

        "D":
            "vermelho",
    }


    estados[
        via
    ] = "verde"


    atualizar_semaforos(
        estados
    )


def amarelar_via(
    via
):

    estados = {

        "A":
            "vermelho",

        "B":
            "vermelho",

        "C":
            "vermelho",

        "D":
            "vermelho",
    }


    estados[
        via
    ] = "amarelo"


    atualizar_semaforos(
        estados
    )


# =====================================================
# REGISTRAR A DECISÃO ATUAL
# =====================================================

def registrar_atendimento(
    item,
    posicao,
    total
):

    via = (
        item[
            "via"
        ]
    )


    motivo = (

        "veiculo_prioritario"

        if item[
            "prioritario"
        ]

        else
        "fila_da_imagem"
    )


    pontuacoes = {

        v: {

            "total":
                float(
                    item[
                        "veiculos"
                    ]
                )

                if v == via

                else 0.0
        }

        for v in VIAS
    }


    registrar_decisao({

        "via":
            via,

        "motivo":
            motivo,

        "pontuacao":
            float(
                item[
                    "veiculos"
                ]
            ),

        "pontuacoes":
            pontuacoes,

        "posicao_fila":
            posicao,

        "tamanho_fila":
            total
    })


# =====================================================
# CRONÔMETRO VISUAL
# =====================================================

def esperar(
    segundos,
    descricao
):

    inicio = time.monotonic()


    while True:

        decorrido = (
            time.monotonic()
            -
            inicio
        )


        restante = (
            segundos
            -
            decorrido
        )


        if restante <= 0:

            break


        print(
            f"\r{descricao}: "
            f"{restante:4.1f}s ",
            end="",
            flush=True
        )


        time.sleep(
            0.1
        )


    print(
        f"\r{descricao}: concluído      "
    )


# =====================================================
# ATENDER UMA VIA
# =====================================================

def atender_via(
    item,
    posicao,
    total
):

    via = (
        item[
            "via"
        ]
    )


    quantidade = (
        item[
            "veiculos"
        ]
    )


    print()
    print(
        "-" * 65
    )

    print(
        f"ATENDENDO VIA {via}"
    )

    print(
        f"Veículos detectados: "
        f"{quantidade}"
    )


    if item[
        "prioritario"
    ]:

        print(
            ">>> VEÍCULO PRIORITÁRIO"
        )


    print(
        f"Posição na fila: "
        f"{posicao}/{total}"
    )

    print(
        "-" * 65
    )


    registrar_atendimento(
        item,
        posicao,
        total
    )


    # =================================================
    # VERDE
    # =================================================

    print(
        f">>> VIA {via}: VERDE"
    )


    abrir_via(
        via
    )


    esperar(
        TEMPO_VERDE,
        f"Via {via} VERDE"
    )


    # =================================================
    # AMARELO
    # =================================================

    print(
        f">>> VIA {via}: AMARELO"
    )


    amarelar_via(
        via
    )


    esperar(
        TEMPO_AMARELO,
        f"Via {via} AMARELO"
    )


    # =================================================
    # INTERVALO DE SEGURANÇA
    # =================================================

    print(
        ">>> TODAS AS VIAS: VERMELHO"
    )


    todos_vermelhos()


    esperar(

        TEMPO_TODOS_VERMELHOS,

        "Intervalo de segurança"
    )


# =====================================================
# PROCESSAR UMA IMAGEM COMPLETA
# =====================================================

def processar_imagem(
    numero,
    total,
    prefixo
):

    print()
    print()
    print(
        "=" * 75
    )

    print(
        f"IMAGEM "
        f"{numero}/{total}: "
        f"{prefixo}"
    )

    print(
        "=" * 75
    )


    # =================================================
    # PREPARAR RESOLUÇÃO
    # =================================================

    imagem = (
        preparar_imagem(
            prefixo
        )
    )


    print(
        "Imagem preparada:",
        imagem.name
    )


    # =================================================
    # IMAGEM NO DASHBOARD PRIMEIRO
    #
    # Isso remove o atraso visual.
    # =================================================

    atualizar_imagem_dashboard(
        imagem
    )


    # Altera timestamp imediatamente para o navegador
    # perceber que um novo frame começou.
    atualizar_status(
        "camera",
        True
    )


    atualizar_status(
        "yolo",
        None
    )


    # Pequeno tempo apenas para o navegador trocar
    # visualmente o frame.
    time.sleep(
        0.25
    )


    # =================================================
    # YOLO - SOMENTE UMA VEZ
    # =================================================

    print()
    print(
        ">>> Executando YOLO..."
    )


    inicio = (
        time.perf_counter()
    )


    saida = (
        executar_pipeline(
            imagem
        )
    )


    duracao = (

        time.perf_counter()
        -
        inicio
    )


    print(
        saida
    )


    print(
        f"Tempo do pipeline: "
        f"{duracao:.2f}s"
    )


    atualizar_status(
        "yolo",
        True
    )


    # =================================================
    # RESULTADO DA IMAGEM
    # =================================================

    resumo = (
        interpretar_pipeline(
            saida
        )
    )


    atualizar_resultado_yolo(
        resumo
    )


    # =================================================
    # CONGELA A FILA DA IMAGEM
    # =================================================

    fila = (
        montar_fila(
            resumo
        )
    )


    print()
    print(
        "FILA GERADA PARA ESTA IMAGEM:"
    )


    if not fila:

        print(
            "Nenhuma via com veículos."
        )


        todos_vermelhos()


        esperar(
            TEMPO_TODOS_VERMELHOS,
            "Todos vermelhos"
        )


        return


    for posicao, item in enumerate(
        fila,
        start=1
    ):

        marca = (

            " [PRIORITÁRIO]"

            if item[
                "prioritario"
            ]

            else ""
        )


        print(

            f"{posicao}. "
            f"Via "
            f"{item['via']}"

            f" - "
            f"{item['veiculos']} "
            f"veículo(s)"

            f"{marca}"
        )


    print()
    print(
        "IMPORTANTE:"
    )

    print(
        "O YOLO NÃO SERÁ EXECUTADO NOVAMENTE "
        "ATÉ ESTA FILA TERMINAR."
    )


    # =================================================
    # ATENDER TODA A FILA
    # =================================================

    total_fila = len(
        fila
    )


    for posicao, item in enumerate(
        fila,
        start=1
    ):

        atender_via(

            item,

            posicao,

            total_fila
        )


    # =================================================
    # IMAGEM COMPLETAMENTE ATENDIDA
    # =================================================

    print()
    print(
        "=" * 75
    )

    print(
        f"IMAGEM {prefixo} "
        "TOTALMENTE ATENDIDA."
    )

    print(
        "Todas as vias detectadas com carros "
        "receberam seu ciclo."
    )

    print(
        "Liberado processamento "
        "da próxima imagem."
    )

    print(
        "=" * 75
    )


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    print()
    print(
        "=" * 75
    )

    print(
        "TESTE SEQUENCIAL POR IMAGEM"
    )

    print(
        "=" * 75
    )


    print(
        "VERDE:",
        TEMPO_VERDE,
        "s"
    )

    print(
        "AMARELO:",
        TEMPO_AMARELO,
        "s"
    )

    print(
        "TODOS VERMELHOS:",
        TEMPO_TODOS_VERMELHOS,
        "s"
    )


    print()
    print(
        "Arduino/Bluetooth: DESABILITADOS"
    )

    print(
        "Dashboard: HABILITADO"
    )

    print()


    PASTA_DASHBOARD.mkdir(
        parents=True,
        exist_ok=True
    )


    todos_vermelhos()


    atualizar_status(
        "camera",
        True
    )


    atualizar_status(
        "yolo",
        True
    )


    # =================================================
    # DASHBOARD
    # =================================================

    servidor = threading.Thread(

        target=iniciar_dashboard,

        daemon=True
    )


    servidor.start()


    time.sleep(
        1.0
    )


    print(
        "Dashboard disponível em:"
    )

    print(
        "http://IP_DA_RASPBERRY:8000"
    )


    print()


    # =================================================
    # PROCESSAR IMAGENS
    # =================================================

    total = len(
        PREFIXOS
    )


    try:

        while True:

            for numero, prefixo in enumerate(
                PREFIXOS,
                start=1
            ):

                processar_imagem(

                    numero,

                    total,

                    prefixo
                )


            print()
            print(
                "#" * 75
            )

            print(
                "FIM DE TODA A SEQUÊNCIA."
            )

            print(
                "Reiniciando desde a primeira imagem..."
            )

            print(
                "#" * 75
            )


            todos_vermelhos()


            time.sleep(
                2.0
            )


    except KeyboardInterrupt:

        print()
        print(
            "Teste interrompido."
        )


        todos_vermelhos()


        sys.exit(
            0
        )
