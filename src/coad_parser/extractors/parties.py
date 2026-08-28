import re
from bs4 import BeautifulSoup

from ..utils.html_helpers import encontra_tag_por_label
from ..utils.text_utils import normaliza_nome

def extrai_interessado(soup: BeautifulSoup) -> str | None:
    label_tag = None
    label_usado = None
    for label in ("Interessado", "Autorizada", "Autorizado"):
        label_tag = encontra_tag_por_label(soup, label)
        if label_tag:
            label_usado = label
            break

    if not label_tag or not label_usado:
        return None

    full = label_tag.get_text(" ", strip=True)
    match = re.search(
        rf"{re.escape(label_usado)}\s*:?\s*(.+)$",
        full,
        flags=re.IGNORECASE,
    )
    if not match:
        return None

    resto = match.group(1).strip()
    return normaliza_nome(resto) if resto else None


def extrai_cpf_cnpj(soup: BeautifulSoup) -> str | None:
    label_tag = encontra_tag_por_label(soup, "CPF")
    if not label_tag:
        label_tag = encontra_tag_por_label(soup, "CNPJ")
    if not label_tag:
        return None

    full = label_tag.get_text(" ", strip=True)
    padrao = r"\d{3}\.\d{3}\.\d{3}-\d{2}|\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}"
    match = re.search(padrao, full)
    return match.group(0) if match else None
