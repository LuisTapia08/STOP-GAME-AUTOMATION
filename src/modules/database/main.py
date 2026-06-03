import csv
import unicodedata

from src.shared.constant import CSV_PATH


APELIDOS_TEMAS = {
    "cidade estado ou pais": "cep",
    "cidade, estado ou pais": "cep",
    "cidade, estado ou país": "cep",
    "cep": "cep",

    "minha sogra e": "mse",
    "minha sogra é": "mse",
    "mse": "mse",

    "filme desenho serie": "fds",
    "filme, desenho, serie": "fds",
    "filme, desenho, série": "fds",
    "fds": "fds",

    "jornal livro revista": "jlr",
    "jornal, livro, revista": "jlr",
    "jlr": "jlr",

    "parte do corpo humano": "phc",
    "phc": "phc",

    "app marca": "app/marca",
    "app/marca": "app/marca",

    "personagem ficticio": "personagem ficticio",
    "personagem fictício": "personagem ficticio",

    "tem na fazenda": "tem na fazenda",

    "palavra em ingles": "palavra em ingles",
    "palavra em inglês": "palavra em ingles",

    "sabor de sorvete": "sabor de sorvete",
    "sabor de pizza": "sabor de pizza"
}


def normalizar_texto(texto):
    texto = texto.strip().lower()

    texto = "".join(
        caractere for caractere in unicodedata.normalize("NFD", texto)
        if unicodedata.category(caractere) != "Mn"
    )

    texto = texto.replace("(", "")
    texto = texto.replace(")", "")
    texto = texto.replace("-", " ")
    texto = texto.replace("_", " ")

    while "  " in texto:
        texto = texto.replace("  ", " ")

    return texto.strip()


def normalizar_tema(tema):
    tema_normalizado = normalizar_texto(tema)

    if tema_normalizado in APELIDOS_TEMAS:
        return APELIDOS_TEMAS[tema_normalizado]

    return tema_normalizado


def carregar_linhas():
    if not CSV_PATH.exists():
        return []

    with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def salvar_linhas(linhas):
    campos = ["letra", "tema", "tema_normalizado", "palavra"]

    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=campos)
        writer.writeheader()
        writer.writerows(linhas)


def buscar_palavra(letra, tema):
    letra = letra.strip().upper()
    tema_busca = normalizar_tema(tema)

    linhas = carregar_linhas()

    for linha in linhas:
        letra_linha = linha.get("letra", "").strip().upper()

        tema_linha = linha.get("tema_normalizado", "").strip()

        if not tema_linha:
            tema_linha = linha.get("tema", "")

        tema_linha = normalizar_tema(tema_linha)

        palavra = linha.get("palavra", "").strip()

        if letra_linha == letra and tema_linha == tema_busca:
            return palavra

    return ""


def adicionar_ou_atualizar_palavra(letra, tema, palavra):
    letra = letra.strip().upper()
    tema_original = tema.strip()
    tema_normalizado = normalizar_tema(tema)
    palavra = palavra.strip()

    linhas = carregar_linhas()
    encontrado = False

    for linha in linhas:
        letra_linha = linha.get("letra", "").strip().upper()

        tema_linha = linha.get("tema_normalizado", "").strip()

        if not tema_linha:
            tema_linha = linha.get("tema", "")

        tema_linha = normalizar_tema(tema_linha)

        if letra_linha == letra and tema_linha == tema_normalizado:
            linha["palavra"] = palavra
            encontrado = True
            break

    if not encontrado:
        linhas.append({
            "letra": letra,
            "tema": tema_original,
            "tema_normalizado": tema_normalizado,
            "palavra": palavra
        })

    salvar_linhas(linhas)