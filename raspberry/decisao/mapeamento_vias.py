"""
Mapeamento das detecções do YOLO para as vias A/B/C/D.

O YOLO retorna bounding boxes:

x1, y1, x2, y2

Para determinar onde o veículo está na pista,
utilizamos o centro inferior da bounding box.

Exemplo:

       ┌───────────────┐
       │    veículo    │
       │               │
       └───────●───────┘
               ↑
          ponto usado

As regiões das vias são polígonos definidos
em config.py utilizando coordenadas normalizadas.
"""

from copy import deepcopy

from config import (
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    CLASSES_PRIORITARIAS,
    LIMIARES_CONGESTIONAMENTO,
    REGIOES_VIAS,
    YOLO_CLASSES,
    YOLO_SCORE_MIN
)


VIAS = (
    "A",
    "B",
    "C",
    "D"
)


# =====================================================
# PONTO DENTRO DE POLIGONO
# =====================================================

def _ponto_no_poligono(
    x,
    y,
    poligono
):

    dentro = False

    j = (
        len(poligono)
        - 1
    )


    for i in range(
        len(poligono)
    ):

        xi, yi = poligono[i]

        xj, yj = poligono[j]


        cruza = (
            (yi > y)
            !=
            (yj > y)
        )


        if cruza:

            denominador = (
                yj
                - yi
            )


            if denominador == 0:

                j = i

                continue


            x_intersecao = (
                (xj - xi)
                * (y - yi)
                / denominador
                + xi
            )


            if x < x_intersecao:

                dentro = (
                    not dentro
                )


        j = i


    return dentro


# =====================================================
# PONTO REPRESENTATIVO DO VEICULO
# =====================================================

def ponto_representativo(
    deteccao
):

    x1 = float(
        deteccao.get(
            "x1",
            0
        )
    )

    y1 = float(
        deteccao.get(
            "y1",
            0
        )
    )

    x2 = float(
        deteccao.get(
            "x2",
            0
        )
    )

    y2 = float(
        deteccao.get(
            "y2",
            0
        )
    )


    # Centro horizontal
    x = (
        x1
        + x2
    ) / 2.0


    # Parte inferior da bounding box
    y = max(
        y1,
        y2
    )


    return (
        x,
        y
    )


# =====================================================
# DESCOBRIR VIA
# =====================================================

def localizar_via(
    deteccao,
    largura=CAMERA_WIDTH,
    altura=CAMERA_HEIGHT
):

    if (
        largura <= 0
        or
        altura <= 0
    ):

        return None


    px, py = (
        ponto_representativo(
            deteccao
        )
    )


    # Coordenadas normalizadas
    xn = (
        px
        / float(largura)
    )

    yn = (
        py
        / float(altura)
    )


    for via in VIAS:

        poligono = (
            REGIOES_VIAS.get(
                via,
                []
            )
        )


        if len(poligono) < 3:

            continue


        if _ponto_no_poligono(
            xn,
            yn,
            poligono
        ):

            return via


    return None


# =====================================================
# NIVEL DE CONGESTIONAMENTO
# =====================================================

def _nivel_congestionamento(
    quantidade
):

    baixo = (
        LIMIARES_CONGESTIONAMENTO
        .get(
            "baixo",
            2
        )
    )


    moderado = (
        LIMIARES_CONGESTIONAMENTO
        .get(
            "moderado",
            4
        )
    )


    if quantidade <= 0:

        return "livre"


    if quantidade <= baixo:

        return "baixo"


    if quantidade <= moderado:

        return "moderado"


    return "alto"


# =====================================================
# MAPEAR TODAS AS DETECCOES
# =====================================================

def mapear_deteccoes(
    deteccoes,
    largura=CAMERA_WIDTH,
    altura=CAMERA_HEIGHT
):

    resultado = {

        "vias": {

            via: {

                "veiculos": 0,

                "congestionamento":
                    "livre",

                "veiculo_prioritario":
                    False,

                "tipo_prioritario":
                    None,

                "deteccoes": []

            }

            for via in VIAS
        },

        "fora_das_vias": [],

        "total_deteccoes": 0
    }


    if not isinstance(
        deteccoes,
        list
    ):

        return resultado


    for det_original in deteccoes:

        if not isinstance(
            det_original,
            dict
        ):

            continue


        det = deepcopy(
            det_original
        )


        # ============================================
        # SCORE
        # ============================================

        try:

            score = float(
                det.get(
                    "score",
                    0.0
                )
            )

        except (
            TypeError,
            ValueError
        ):

            score = 0.0


        if score < YOLO_SCORE_MIN:

            continue


        # ============================================
        # CLASSE
        # ============================================

        try:

            classe_id = int(
                det.get(
                    "classe",
                    -1
                )
            )

        except (
            TypeError,
            ValueError
        ):

            classe_id = -1


        classe_nome = (
            YOLO_CLASSES.get(
                classe_id,
                f"classe_{classe_id}"
            )
        )


        # ============================================
        # POSICAO
        # ============================================

        px, py = (
            ponto_representativo(
                det
            )
        )


        via = localizar_via(
            det,
            largura,
            altura
        )


        det_enriquecida = {

            **det,

            "classe_nome":
                classe_nome,

            "ponto": {

                "x":
                    round(
                        px,
                        1
                    ),

                "y":
                    round(
                        py,
                        1
                    ),

                "x_normalizado":
                    round(
                        px
                        / float(largura),
                        4
                    ),

                "y_normalizado":
                    round(
                        py
                        / float(altura),
                        4
                    )
            },

            "via":
                via
        }


        resultado[
            "total_deteccoes"
        ] += 1


        # ============================================
        # FORA DAS REGIOES
        # ============================================

        if via is None:

            resultado[
                "fora_das_vias"
            ].append(
                det_enriquecida
            )

            continue


        # ============================================
        # DADOS DA VIA
        # ============================================

        dados_via = (
            resultado[
                "vias"
            ][via]
        )


        dados_via[
            "veiculos"
        ] += 1


        dados_via[
            "deteccoes"
        ].append(
            det_enriquecida
        )


        # ============================================
        # PRIORITARIO
        # ============================================

        if (
            classe_nome
            in
            CLASSES_PRIORITARIAS
        ):

            dados_via[
                "veiculo_prioritario"
            ] = True


            dados_via[
                "tipo_prioritario"
            ] = classe_nome


    # ================================================
    # CONGESTIONAMENTO
    # ================================================

    for via in VIAS:

        dados_via = (
            resultado[
                "vias"
            ][via]
        )


        dados_via[
            "congestionamento"
        ] = (
            _nivel_congestionamento(
                dados_via[
                    "veiculos"
                ]
            )
        )


    return resultado
