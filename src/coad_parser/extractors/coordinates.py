import re
from bs4 import BeautifulSoup


def extrai_coordenadas(soup: BeautifulSoup) -> str | None:
    texto = soup.get_text(" ", strip=True)
    padrao = r"-?\d{1,3}\.\d{4,},\s*-?\d{1,3}\.\d{4,}"
    coordenadas = re.findall(padrao, texto)
    return "; ".join(coordenadas) if coordenadas else None