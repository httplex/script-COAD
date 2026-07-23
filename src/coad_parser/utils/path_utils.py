import os
import re


def extrai_sei_do_caminho(caminho_html: str) -> str | None:
    nome_arquivo = os.path.basename(caminho_html)
    match = re.search(r"sei[_-]?(\d+)", nome_arquivo, flags=re.IGNORECASE)
    return match.group(1) if match else None