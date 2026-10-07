import subprocess
from pathlib import Path


# ==========================================
# PASTA DO DATASET
# ==========================================

PASTA = (
    Path.home()
    / "semaforo_dataset_rasp"
    / "images"
)

PASTA.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================
# DESCOBRIR PRÓXIMO NÚMERO
# ==========================================

imagens_existentes = list(
    PASTA.glob("imagem_*.jpg")
)

contador = len(imagens_existentes)


# ==========================================
# FUNÇÃO DE CAPTURA
# ==========================================

def tirar_foto():

    global contador

    proximo_numero = contador + 1

    nome_base = f"imagem_{proximo_numero:04d}"

    print()
    print(f"Próxima imagem: {nome_base}")

    complemento = input(
        f"Nome da imagem [{nome_base}]: "
    ).strip()

    # Remove espaços e evita caracteres ruins no nome
    complemento = complemento.replace(" ", "_")

    if complemento:
        nome = f"{nome_base}_{complemento}.jpg"
    else:
        nome = f"{nome_base}.jpg"

    caminho = PASTA / nome

    print()
    print("Capturando imagem...")

    try:

        subprocess.run(
            [
                "rpicam-still",
                "--nopreview",
                "--timeout", "1000",
                "--output", str(caminho)
            ],
            check=True
        )

        contador += 1

        print()
        print(f"Imagem salva: {nome}")
        print(f"Total de imagens: {contador}")

    except subprocess.CalledProcessError:

        print("Erro ao capturar imagem.")


# ==========================================
# PROGRAMA PRINCIPAL
# ==========================================

print()
print("==============================")
print(" DATASET - CÂMERA RASPBERRY PI")
print("==============================")
print()

print("ENTER -> capturar nova imagem")
print("q     -> sair")
print()


while True:

    comando = input("Comando: ").strip().lower()

    if comando == "q":

        print()
        print("Programa encerrado.")
        break

    tirar_foto()
