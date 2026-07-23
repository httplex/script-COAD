import re
from bs4 import BeautifulSoup

from ..utils.html_helpers import encontra_tag_por_label


def extrai_atividade(soup: BeautifulSoup) -> str | None:
    """
    Extrai a descrição da atividade/empreendimento.
    """
    labels = ["Atividade/Empreendimento", "Atividade"]

    label_tag = None
    label_usado = None

    for lab in labels:
        label_tag = encontra_tag_por_label(soup, lab)
        if label_tag:
            label_usado = lab
            break

    if not label_tag:
        return None

    full = label_tag.get_text(" ", strip=True)

    match = re.search(
        rf"{re.escape(label_usado)}\s*:?\s*(.+)$",
        full,
        flags=re.IGNORECASE,
    )
    if match:
        resto = match.group(1).strip()
        if resto and not resto.endswith(":"):
            return resto

    tr = label_tag.find_parent("tr")
    if tr:
        next_tr = tr.find_next_sibling("tr")
        while next_tr and next_tr.name != "tr":
            next_tr = next_tr.next_sibling

        if next_tr:
            p = next_tr.find("p")
            if p:
                texto = p.get_text(" ", strip=True)
                return (
                    re.sub(
                        r"^(Atividade/Empreendimento|Atividade)\s*:\s*",
                        "",
                        texto,
                        flags=re.IGNORECASE,
                    ).strip()
                    or None
                )

    prox_p = label_tag.find_next("p")
    if prox_p:
        texto = prox_p.get_text(" ", strip=True)
        return (
            re.sub(
                r"^(Atividade/Empreendimento|Atividade)\s*:\s*",
                "",
                texto,
                flags=re.IGNORECASE,
            ).strip()
            or None
        )

    return None