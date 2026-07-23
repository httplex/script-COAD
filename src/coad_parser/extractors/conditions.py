import re
from bs4 import BeautifulSoup


def extrai_condicoes_especificas(soup: BeautifulSoup) -> str | None:
    header = soup.find(
        lambda tag: tag.name in ("p", "div")
        and (
            "Condições Específicas" in tag.get_text(" ", strip=True)
            or "Condicionantes Específicas" in tag.get_text(" ", strip=True)
        )
    )
    if not header:
        return None

    condicoes = []

    header_texto = header.get_text(" ", strip=True)
    resto = re.sub(
        r"^.*?(Condições Específicas|Condicionantes Específicas)\s*:\s*",
        "",
        header_texto,
        flags=re.IGNORECASE,
    ).strip()

    if resto:
        condicoes.append(resto)

    container = header.find_parent(["td", "tr"])
    ps_iter = container.find_all("p") if container else header.find_all_next("p")

    started = False
    for p in ps_iter:
        if p == header:
            started = True
            continue
        if not started:
            continue

        texto = p.get_text(" ", strip=True)
        if not texto:
            continue

        if re.search(
            r"\b(Condições|Condicionantes)\s+(Gerais|Específicas)\b\s*:?",
            texto,
            re.IGNORECASE,
        ):
            break

        if re.search(
            r"\bDocumento assinado eletronicamente\b|\bAnalista Ambiental\b|\bChefe\b|\bMatr\b",
            texto,
            re.IGNORECASE,
        ):
            break

        if texto.isupper() and len(texto.split()) >= 2 and len(texto) < 120:
            break

        if re.search(r"\b(ICMBio|NGI|Coordenação|Portaria|Assinado)\b", texto, re.IGNORECASE):
            if len(texto) < 90 and not re.search(r"\b\d+[\.\)]\s*", texto):
                break

        if re.search(
            r"Condições Específicas|Condicionantes Específicas",
            texto,
            re.IGNORECASE,
        ):
            continue

        condicoes.append(texto)

    return "\n".join(condicoes) if condicoes else None