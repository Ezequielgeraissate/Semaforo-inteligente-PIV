import sys

from decisao.logica_decisao import decidir_via
from decisao.mapeamento_vias import mapear_deteccoes
from yolo.adapter import analisar_imagem


def main():

    if len(sys.argv) < 2:

        print(
            "Uso:"
        )

        print(
            "python3 testar_pipeline_imagem.py "
            "imagem.jpg"
        )

        return


    imagem = sys.argv[1]


    print()
    print("==============================")
    print(" TESTE DO PIPELINE COMPLETO ")
    print("==============================")


    # =================================================
    # YOLO
    # =================================================

    print()
    print("[1] Executando YOLO...")


    deteccoes = analisar_imagem(
        imagem
    )


    print(
        f"Deteccoes: {len(deteccoes)}"
    )


    for numero, det in enumerate(
        deteccoes,
        start=1
    ):

        print(
            f"{numero}: "
            f"classe={det.get('classe')} | "
            f"score={det.get('score')} | "
            f"x1={det.get('x1')} | "
            f"y1={det.get('y1')} | "
            f"x2={det.get('x2')} | "
            f"y2={det.get('y2')}"
        )


    # =================================================
    # MAPEAR PARA VIAS
    # =================================================

    print()
    print(
        "[2] Associando veiculos as vias..."
    )


    mapeamento = mapear_deteccoes(
        deteccoes
    )


    for via in ("A", "B", "C", "D"):

        dados = (
            mapeamento["vias"][via]
        )

        print(
            f"Via {via}: "
            f"{dados['veiculos']} veiculos | "
            f"prioritario="
            f"{dados['veiculo_prioritario']} | "
            f"congestionamento="
            f"{dados['congestionamento']}"
        )


    print(
        "Fora das vias:",
        len(
            mapeamento[
                "fora_das_vias"
            ]
        )
    )


    # =================================================
    # DECISAO
    # =================================================

    print()
    print(
        "[3] Calculando decisao..."
    )


    vias = {}


    for via in ("A", "B", "C", "D"):

        dados = (
            mapeamento["vias"][via]
        )

        vias[via] = {
            **dados,

            "sensor":
                dados["veiculos"] > 0,

            "tempo_espera":
                0
        }


    decisao = decidir_via(
        vias,
        via_aberta="X"
    )


    print()
    print("==============================")
    print(" DECISAO FINAL ")
    print("==============================")

    print(
        f"Via: {decisao['via']}"
    )

    print(
        f"Motivo: {decisao['motivo']}"
    )

    print(
        f"Pontuacao: "
        f"{decisao['pontuacao']}"
    )


    print()
    print("Pontuacao por via:")


    for via, dados in (
        decisao[
            "pontuacoes"
        ].items()
    ):

        print(
            f"Via {via}: "
            f"{dados['total']}"
        )


if __name__ == "__main__":

    main()
