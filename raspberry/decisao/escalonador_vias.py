"""
Escalonador das vias do semáforo inteligente.

Ordem de prioridade:

1. Veículo prioritário.
2. Via que atingiu tempo máximo de espera.
3. Pontuação:
   - quantidade de veículos;
   - tempo de espera;
   - sensor.
4. Desempate circular para evitar favorecer sempre A.
"""

VIAS = (
    "A",
    "B",
    "C",
    "D",
)


# =====================================================
# CONFIGURAÇÕES DO ESCALONADOR
# =====================================================

# Para demonstração.
# Depois podemos aumentar para 30 ou 45 segundos.
TEMPO_MAX_ESPERA = 20.0

PESO_VEICULO = 10.0

PESO_ESPERA = 0.50

PESO_SENSOR = 1.0

PONTOS_PRIORITARIO = 1000.0


# =====================================================
# ORDEM CIRCULAR
# =====================================================

def ordem_circular(
    via_atual
):

    if via_atual not in VIAS:

        return list(
            VIAS
        )


    indice = (
        VIAS.index(
            via_atual
        )
        + 1
    )


    return [

        VIAS[
            (
                indice
                + deslocamento
            )
            % len(VIAS)
        ]

        for deslocamento
        in range(
            len(VIAS)
        )
    ]


# =====================================================
# DESEMPATE
# =====================================================

def desempatar(
    candidatas,
    via_atual
):

    ordem = (
        ordem_circular(
            via_atual
        )
    )


    for via in ordem:

        if via in candidatas:

            return via


    return candidatas[0]


# =====================================================
# ESCOLHER VIA
# =====================================================

def escolher_via(
    estado
):

    vias = (
        estado.get(
            "vias",
            {}
        )
    )


    via_atual = (
        estado.get(
            "via_aberta",
            "X"
        )
    )


    # =================================================
    # VIAS QUE REALMENTE POSSUEM VEÍCULOS
    # =================================================

    ativas = [

        via

        for via in VIAS

        if int(
            vias.get(
                via,
                {}
            ).get(
                "veiculos",
                0
            )
            or 0
        )
        > 0
    ]


    # =================================================
    # NENHUM VEÍCULO
    # =================================================

    if not ativas:

        return {

            "via":
                "X",

            "motivo":
                "sem_veiculos",

            "pontuacao":
                0.0,

            "pontuacoes": {

                via: {
                    "total": 0.0
                }

                for via in VIAS
            }
        }


    # =================================================
    # 1. VEÍCULO PRIORITÁRIO
    # =================================================

    prioritarias = [

        via

        for via in ativas

        if bool(
            vias[
                via
            ].get(
                "veiculo_prioritario",
                False
            )
        )
    ]


    if prioritarias:

        # Prioritário que está esperando há mais tempo.
        maior_espera = max(

            float(
                vias[
                    via
                ].get(
                    "tempo_espera",
                    0.0
                )
                or 0.0
            )

            for via in prioritarias
        )


        candidatas = [

            via

            for via in prioritarias

            if float(
                vias[
                    via
                ].get(
                    "tempo_espera",
                    0.0
                )
                or 0.0
            )
            == maior_espera
        ]


        escolhida = (
            desempatar(
                candidatas,
                via_atual
            )
        )


        pontuacoes = {

            via: {

                "prioritario":
                    PONTOS_PRIORITARIO
                    if via == escolhida
                    else 0.0,

                "total":
                    PONTOS_PRIORITARIO
                    if via == escolhida
                    else 0.0
            }

            for via in VIAS
        }


        return {

            "via":
                escolhida,

            "motivo":
                "veiculo_prioritario",

            "pontuacao":
                PONTOS_PRIORITARIO,

            "pontuacoes":
                pontuacoes
        }


    # =================================================
    # 2. TEMPO MÁXIMO DE ESPERA
    # =================================================

    vencidas = [

        via

        for via in ativas

        if (
            via != via_atual

            and

            float(
                vias[
                    via
                ].get(
                    "tempo_espera",
                    0.0
                )
                or 0.0
            )
            >= TEMPO_MAX_ESPERA
        )
    ]


    if vencidas:

        maior_espera = max(

            float(
                vias[
                    via
                ].get(
                    "tempo_espera",
                    0.0
                )
                or 0.0
            )

            for via in vencidas
        )


        candidatas = [

            via

            for via in vencidas

            if float(
                vias[
                    via
                ].get(
                    "tempo_espera",
                    0.0
                )
                or 0.0
            )
            == maior_espera
        ]


        escolhida = (
            desempatar(
                candidatas,
                via_atual
            )
        )


        pontuacoes = {}


        for via in VIAS:

            espera = float(
                vias.get(
                    via,
                    {}
                ).get(
                    "tempo_espera",
                    0.0
                )
                or 0.0
            )


            pontuacoes[
                via
            ] = {

                "espera":
                    round(
                        espera,
                        2
                    ),

                "total":
                    round(
                        espera,
                        2
                    )
            }


        return {

            "via":
                escolhida,

            "motivo":
                "tempo_maximo_espera",

            "pontuacao":
                round(
                    maior_espera,
                    2
                ),

            "pontuacoes":
                pontuacoes
        }


    # =================================================
    # 3. PONTUAÇÃO NORMAL
    # =================================================

    pontuacoes = {}


    for via in VIAS:

        dados = (
            vias.get(
                via,
                {}
            )
        )


        veiculos = int(
            dados.get(
                "veiculos",
                0
            )
            or 0
        )


        espera = float(
            dados.get(
                "tempo_espera",
                0.0
            )
            or 0.0
        )


        # A via atualmente aberta não está esperando.
        if via == via_atual:

            espera = 0.0


        sensor = bool(
            dados.get(
                "sensor",
                False
            )
        )


        pontos_fluxo = (
            veiculos
            * PESO_VEICULO
        )


        pontos_espera = (
            espera
            * PESO_ESPERA
        )


        pontos_sensor = (

            PESO_SENSOR

            if sensor

            else 0.0
        )


        total = (

            pontos_fluxo
            + pontos_espera
            + pontos_sensor
        )


        pontuacoes[
            via
        ] = {

            "fluxo":
                round(
                    pontos_fluxo,
                    2
                ),

            "espera":
                round(
                    pontos_espera,
                    2
                ),

            "sensor":
                round(
                    pontos_sensor,
                    2
                ),

            "total":
                round(
                    total,
                    2
                )
        }


    maior = max(

        pontuacoes[
            via
        ][
            "total"
        ]

        for via in ativas
    )


    candidatas = [

        via

        for via in ativas

        if pontuacoes[
            via
        ][
            "total"
        ]
        == maior
    ]


    # =================================================
    # DESEMPATE CIRCULAR
    # =================================================

    escolhida = (
        desempatar(
            candidatas,
            via_atual
        )
    )


    return {

        "via":
            escolhida,

        "motivo":
            (
                "maior_prioridade"
                if len(
                    candidatas
                )
                == 1

                else
                "desempate_fila"
            ),

        "pontuacao":
            round(
                maior,
                2
            ),

        "pontuacoes":
            pontuacoes
    }
