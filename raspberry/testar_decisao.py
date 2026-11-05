"""
Teste offline:

YOLO
 -> posições
 -> vias
 -> lógica de decisão

Não usa câmera, Arduino ou Bluetooth.
"""

from decisao.logica_decisao import (
    decidir_via
)

from decisao.mapeamento_vias import (
    mapear_deteccoes
)


# =====================================================
# SAIDA SIMULADA DO YOLO
# =====================================================

deteccoes_teste = [

    # VIA A
    {
        "classe": 0,
        "score": 0.92,
        "x1": 850,
        "y1": 100,
        "x2": 980,
        "y2": 350
    },

    # VIA A
    {
        "classe": 0,
        "score": 0.87,
        "x1": 1050,
        "y1": 120,
        "x2": 1180,
        "y2": 390
    },

    # VIA B
    {
        "classe": 0,
        "score": 0.90,
        "x1": 1580,
        "y1": 600,
        "x2": 1780,
        "y2": 790
    },

    # VIA C - ESPECIAL
    {
        "classe": 1,
        "score": 0.95,
        "x1": 930,
        "y1": 1120,
        "x2": 1110,
        "y2": 1420
    },

    # VIA D
    {
        "classe": 0,
        "score": 0.81,
        "x1": 190,
        "y1": 610,
        "x2": 390,
        "y2": 790
    }
]


# =====================================================
# MAPEAR
# =====================================================

mapeamento = (
    mapear_deteccoes(
        deteccoes_teste
    )
)


vias_para_decisao = {}


for via, dados in (
    mapeamento[
        "vias"
    ].items()
):

    vias_para_decisao[
        via
    ] = {

        **dados,

        "sensor":
            dados[
                "veiculos"
            ] > 0,

        "tempo_espera": {

            "A": 4,

            "B": 8,

            "C": 2,

            "D": 15

        }[via]
    }


# =====================================================
# DECIDIR
# =====================================================

decisao = decidir_via(

    vias_para_decisao,

    via_aberta="A"
)


# =====================================================
# RESULTADO
# =====================================================

print()

print(
    "=== MAPEAMENTO ==="
)


for via in (
    "A",
    "B",
    "C",
    "D"
):

    dados = (
        mapeamento[
            "vias"
        ][via]
    )


    print(

        f"Via {via}: "

        f"veiculos="
        f"{dados['veiculos']} | "

        f"prioritario="
        f"{dados['veiculo_prioritario']} | "

        f"congestionamento="
        f"{dados['congestionamento']}"
    )


print()

print(
    "=== DECISAO ==="
)

print(
    decisao
)

print()

print(
    "Esperado: VIA C, "
    "por veiculo prioritario."
)

print()
