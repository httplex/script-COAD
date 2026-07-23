import re
from bs4 import BeautifulSoup

from ..utils.text_utils import parse_data


def extrai_numero_autorizacao(soup: BeautifulSoup) -> str | None:
    """
    Exemplos:
      "autorização direta Nº 12/2025"
      "Autorização Direta nº 12/2025"
    Queremos só "12/2025".
    """
    texto = soup.get_text(" ", strip=True)
    padrao = r"Autorização\s+Direta\s*N[ºo]?\s*([0-9./-]+)"
    match = re.search(padrao, texto, flags=re.IGNORECASE)
    return match.group(1) if match else None


def extrai_numero_processo(soup: BeautifulSoup) -> str | None:
    """
    Extrai o número do processo de duas formas:
    1) Pelo texto padrão: "Processo nº 02122.001396/2025-18"
    2) Pela linha do topo do HTML com classe Tabela_Texto_Alinhado_Direita
    """
    texto = soup.get_text(" ", strip=True)

    padrao1 = r"Processo\s*n[ºo]?\s*:?\s*([0-9]{5}\.[0-9]{6}/[0-9]{4}-[0-9]{2})"
    match = re.search(padrao1, texto, flags=re.IGNORECASE)
    if match:
        return match.group(1)

    candidatos = soup.find_all("p", class_="Tabela_Texto_Alinhado_Direita")
    for p in candidatos:
        t = p.get_text(strip=True)

        if re.search(r"sei", t, flags=re.IGNORECASE):
            continue

        match2 = re.search(r"([0-9]{5}\.[0-9]{6}/[0-9]{4}-[0-9]{2})", t)
        if match2:
            return match2.group(1)

    return None


def extrai_numero_sei(soup: BeautifulSoup) -> str | None:
    """
    Tenta extrair o Número SEI preferencialmente do <title>.
    Se não encontrar no título, procura 'Número SEI:xxxxx' nos <p>.
    """
    titulo = soup.title.string if soup.title and soup.title.string else ""
    if titulo:
        match = re.search(r"-\s*([0-9]{6,})\s*-", titulo)
        if match:
            return match.group(1)

    for p in soup.find_all("p"):
        texto = p.get_text(" ", strip=True)
        if not texto:
            continue

        match = re.search(r"Número\s+SEI:?\s*([0-9]+)", texto, flags=re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def extrai_data_assinatura(soup: BeautifulSoup) -> str | None:
    """
    Tenta pegar a data de assinatura no rodapé do SEI.
    """
    ps_footer = soup.find_all(
        "p",
        string=lambda t: t and "Documento assinado eletronicamente por" in t,
    )

    if ps_footer:
        texto = ps_footer[-1].get_text(" ", strip=True)
        match = re.search(r"em\s+(\d{2}/\d{2}/\d{4}),\s*às", texto)
        if match:
            return parse_data(match.group(1))

    texto_total = soup.get_text(" ", strip=True)
    datas = re.findall(r"em\s+(\d{2}/\d{2}/\d{4}),\s*às", texto_total)

    if not datas:
        return None

    return parse_data(datas[-1])


def extrai_data_documento(soup: BeautifulSoup) -> str | None:
    """
    Data do documento = data do rodapé
    'Criado por ..., versão X por ..., em dd/mm/aaaa hh:mm:ss.'
    """
    divs_unselectable = soup.find_all("div", attrs={"unselectable": "on"})

    if divs_unselectable:
        texto_rodape = divs_unselectable[-1].get_text(" ", strip=True)
    else:
        texto_rodape = soup.get_text(" ", strip=True)

    match = re.search(
        r"Criado por .*? em\s+(\d{2}/\d{2}/\d{4})\s+\d{2}:\d{2}:\d{2}",
        texto_rodape,
        flags=re.IGNORECASE,
    )

    if not match:
        match = re.search(
            r"em\s+(\d{2}/\d{2}/\d{4})",
            texto_rodape,
            flags=re.IGNORECASE,
        )

    if not match:
        return None

    return parse_data(match.group(1))