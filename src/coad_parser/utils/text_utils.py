from datetime import datetime
import re

def parse_data(data_str: str) -> str | None:
    try:
        data = datetime.strptime(data_str, "%d/%m/%Y")
    except ValueError:
        return None

    return data.strftime("%Y-%m-%d")

_ARTIGOS_MINUSCULOS = {"de", "da", "do", "das", "dos", "e"}


def titulo_com_artigos_minusculos(texto: str) -> str:
    palavras = texto.split(" ")
    resultado = [
        palavra.lower() if palavra.lower() in _ARTIGOS_MINUSCULOS else palavra.capitalize()
        for palavra in palavras
    ]
    return " ".join(resultado)


def _normaliza_forma_societaria(nome: str) -> str:
    nome = re.sub(r"\bS\.?\s*/?\s*A\.?\b", "S.A.", nome, flags=re.IGNORECASE)
    nome = re.sub(r"\bLTDA\.?\b", "Ltda.", nome, flags=re.IGNORECASE)
    return nome


def normaliza_nome(nome: str) -> str:
    nome = nome.strip()
    if not nome:
        return nome

    if nome.isupper():
        nome = titulo_com_artigos_minusculos(nome)

    return _normaliza_forma_societaria(nome)