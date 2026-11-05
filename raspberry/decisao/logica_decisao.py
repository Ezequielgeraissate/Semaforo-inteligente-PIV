"""
Lógica de decisão das vias.

Cada via recebe uma pontuação levando em conta:

- quantidade de veículos;
- tempo de espera;
- sensor ativo;
- veículo prioritário;
- pequeno bônus para manter a via atual.

Os pesos ficam em config.py.
"""

from config import (
    BONUS_MANTER_VIA,
    PESO_ESPERA,
    PESO_SENSOR,
    PESO_VEICULO,
    PESO_VEICULO_PRIORITARIO,
    TEMPO_ESPERA_MAX_PONTUACAO
)


VIAS = (
    "A",
    "B",
    "C",
    "D"
)


# =====================================================
# CONVERSAO SEGURA PARA NUMERO
# =====================================================

def _numero(
    valor,
    padrao=0.0
):

    try:

        return float(
            valor
        )

    except (
        TypeError,
        ValueError
    ):

        return padrao


# =====================================================
# CALCULAR PONTOS DE UMA VIA
# =====================================================

def calcular_pontuacao(
    via,
    dados,
    via_aberta="X"
):

    veiculos = int(
        _numero(
            dados.get(
                "veiculos"
            ),
            0
        )
    )


    espera = max(

        0.0,

        _numero(
            dados.get(
                "tempo_espera"
            ),
            0.0
        )
    )


    sensor = bool(
        dados.get(
            "sensor",
            False
        )
    )


    prioritario = bool(
        dados.get(
            "veiculo_prioritario",
            False
        )
    )


    # Só entra na disputa se houver demanda.
    tem_demanda = (
        veiculos > 0
        or
        sensor
        or
        prioritario
    )


    if not tem_demanda:

        return {

            "total": 0.0,

            "fluxo": 0.0,

            "espera": 0.0,

            "sensor": 0.0,

            "prioritario": 0.0,

            "manter_via": 0.0,

            "tem_demanda": False
        }


    componentes = {

        "fluxo":
            veiculos
            * PESO_VEICULO,

        "espera":
            min(
                espera,
                TEMPO_ESPERA_MAX_PONTUACAO
            )
            * PESO_ESPERA,

        "sensor":
            PESO_SENSOR
            if sensor
            else 0.0,

        "prioritario":
            PESO_VEICULO_PRIORITARIO
            if prioritario
            else 0.0,

        "manter_via":
            BONUS_MANTER_VIA
            if via == via_aberta
            else 0.0
    }


    componentes[
        "total"
    ] = round(
        sum(
            componentes.values()
        ),
        2
    )


    componentes[
        "tem_demanda"
    ] = True


    return componentes


# =====================================================
# MOTIVO PRINCIPAL
# =====================================================

def _motivo_principal(
    componentes
):

    nomes = {

        "prioritario":
            "veiculo_prioritario",

        "fluxo":
            "maior_fluxo",

        "espera":
            "tempo_espera",

        "sensor":
            "sensor_ativo",

        "manter_via":
            "manter_via_atual"
    }


    chaves = [

        "prioritario",

        "fluxo",

        "espera",

        "sensor",

        "manter_via"
    ]


    principal = max(

        chaves,

        key=lambda chave:
            componentes.get(
                chave,
                0.0
            )
    )


    if (
        componentes.get(
            principal,
            0.0
        )
        <= 0
    ):

        return "sem_demanda"


    return nomes[
        principal
    ]


# =====================================================
# DECIDIR MELHOR VIA
# =====================================================

def decidir_via(
    vias,
    via_aberta="X"
):

    pontuacoes = {}


    # Calcula os pontos das quatro vias.
    for via in VIAS:

        dados = vias.get(
            via,
            {}
        )


        pontuacoes[
            via
        ] = calcular_pontuacao(

            via,

            dados,

            via_aberta
        )


    # Somente vias com demanda.
    candidatas = [

        via

        for via in VIAS

        if pontuacoes[
            via
        ][
            "tem_demanda"
        ]
    ]


    # Nenhum veículo / sensor ativo.
    if not candidatas:

        return {

            "via": None,

            "motivo":
                "sem_demanda",

            "pontuacao":
                0.0,

            "pontuacoes":
                pontuacoes
        }


    # Via com maior pontuação.
    melhor_via = max(

        candidatas,

        key=lambda via:
            pontuacoes[
                via
            ][
                "total"
            ]
    )


    componentes = (
        pontuacoes[
            melhor_via
        ]
    )


    return {

        "via":
            melhor_via,

        "motivo":
            _motivo_principal(
                componentes
            ),

        "pontuacao":
            componentes[
                "total"
            ],

        "pontuacoes":
            pontuacoes
    }
