import re
from bs4 import BeautifulSoup

from ..utils.text_utils import titulo_com_artigos_minusculos
from ..utils.uc_catalog import encontrar_nome_canonico

_SIGLAS_UC = {
    r"\bÁrea de Proteção Ambiental\b": "APA",
    r"\bApa\b": "APA",
    r"\bParque Nacional\b": "PARNA",
    r"\bParna\b": "PARNA",
    r"\bFloresta Nacional\b": "FLONA",
    r"\bFlona\b": "FLONA",
    r"\bReserva Extrativista\b": "RESEX",
    r"\bResex\b": "RESEX",
    r"\bMonumento Natural\b": "MONA",
    r"\bMona\b": "MONA",
    r"\bRefúgio (?:de|da) Vida Silvestre\b": "REVIS",
    r"\bRevis\b": "REVIS",
    r"\bEstação Ecológica\b": "ESEC",
    r"\bEsec\b": "ESEC",
    r"\bReserva Biológica\b": "REBIO",
    r"\bRebio\b": "REBIO",
    r"\bÁrea de Relevante Interesse Ecológico\b": "ARIE",
    r"\bArie\b": "ARIE",
    r"\bReserva Particular do Patrimônio Natural\b": "RPPN",
    r"\bReserva de Desenvolvimento Sustentável\b": "RDS",
}

_INICIO_CATEGORIA_UC = (
    r"(?:Área\s+de\s+Proteção\s+Ambiental|Parque\s+Nacional|"
    r"Floresta\s+Nacional|Reserva\s+Extrativista|Monumento\s+Natural|"
    r"Estação\s+Ecológica|Reserva\s+Biológica|Refúgio\s+de\s+Vida\s+Silvestre|"
    r"Área\s+de\s+Relevante\s+Interesse\s+Ecológico|Reserva\s+de\s+Fauna|"
    r"Reserva\s+de\s+Desenvolvimento\s+Sustentável|"
    r"Reserva\s+Particular\s+do\s+Patrimônio\s+Natural|"
    r"APA|PARNA|FLONA|RESEX|MONA|REVIS|ESEC|REBIO|ARIE|RPPN|RDS)"
)

_PADRAO_ROTULO_UC = re.compile(
    r"^\s*Unidades?\s+de\s+Conservação"
    r"(?:\s+afetadas?)?"
    r"(?:\s+e\s+ato\s+de\s+criação)?"
    r"\s*:\s*(.*)$",
    flags=re.IGNORECASE,
)

_PADRAO_APENAS_ATO = re.compile(
    r"^(?:Decreto|Lei|Portaria|Resolução|Medida\s+Provisória)\b",
    flags=re.IGNORECASE,
)

_PADRAO_APENAS_CATEGORIA = re.compile(
    r"^(?:APA|PARNA|FLONA|RESEX|MONA|REVIS|ESEC|REBIO|ARIE|RPPN|RDS|Parque(?:\s+Nacional)?|"
    r"Floresta(?:\s+Nacional)?|Reserva\s+Extrativista|Monumento\s+Natural|"
    r"Estação\s+Ecológica|Reserva\s+Biológica|"
    r"Refúgio\s+d[ae]\s+Vida\s+Silvestre)\s*$",
    flags=re.IGNORECASE,
)

_PADRAO_CABECALHO_UC = re.compile(
    rf"^\s*{_INICIO_CATEGORIA_UC}\b",
    flags=re.IGNORECASE,
)

_PADRAO_AUTORIDADE_UC = re.compile(
    rf"\b(?:Chefe|Chefia|Gestor(?:a)?|Diretor(?:a)?)\s+d[oa]\s+"
    rf"{_INICIO_CATEGORIA_UC}\b",
    flags=re.IGNORECASE,
)


def _aplica_sigla_uc(nome: str) -> str:
    nome = re.sub(
        r"\s+-\s+Rocas\s+-\s+São\s+Pedro\s+e\s+São\s+Paulo$",
        "",
        nome,
        flags=re.IGNORECASE,
    )
    for padrao, sigla in _SIGLAS_UC.items():
        nome = re.sub(padrao, sigla, nome, flags=re.IGNORECASE)
    return nome


def _limpar_segmento_uc(segmento: str) -> str:
    sem_parenteses = re.sub(r"\s*\([^)]*\)", "", segmento)
    sem_ato = re.split(r"\s+-\s+", sem_parenteses, maxsplit=1)[0]
    sem_ato = re.split(
        r"\s*/\s*(?=(?:(?:Decreto|Lei|Portaria|Medida\s+Provisória|Resolução)\b|\d{1,2}\s+de\s+))",
        sem_ato,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]
    sem_ato = re.split(
        r"\s*,\s*(?:criad[oa]|instituíd[oa])\s+"
        r"(?:(?:pel[oa]|por|conforme)\s+)?"
        r"(?=(?:Decreto|Lei|Portaria|Medida\s+Provisória|Resolução)\b)",
        sem_ato,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]
    sem_ato = re.split(
        r"\s*[,;]\s*(?=(?:Decreto|Lei|Portaria|Medida\s+Provisória|Resolução)\b)",
        sem_ato,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]
    sem_ato = re.sub(r"\s*/\s*[A-Z]{2}\s*$", "", sem_ato)
    sem_ato = re.sub(r"\s{2,}", " ", sem_ato).strip()
    sem_ato = sem_ato.rstrip(".").strip()

    if _PADRAO_APENAS_ATO.match(sem_ato) or _PADRAO_APENAS_CATEGORIA.match(sem_ato):
        return ""

    nome_canonico = encontrar_nome_canonico(sem_ato)
    if nome_canonico:
        sem_ato = nome_canonico
    elif sem_ato.isupper():
        sem_ato = titulo_com_artigos_minusculos(sem_ato)

    return _aplica_sigla_uc(sem_ato)


def _limpar_nome_uc(texto: str) -> str | None:
    segmentos = re.split(
        rf"\s+e\s+(?={_INICIO_CATEGORIA_UC}\b)",
        texto,
        flags=re.IGNORECASE,
    )
    limpos = []
    for segmento in segmentos:
        segmento_limpo = _limpar_segmento_uc(segmento)
        if segmento_limpo:
            limpos.append(segmento_limpo)
    return ";".join(limpos) or None


def reconciliar_ucs(valor_extraido: str | None) -> str | None:
    if not valor_extraido:
        return None

    nomes_canonicos = []
    for segmento in re.split(r"\s*;\s*", valor_extraido):
        nome_canonico = encontrar_nome_canonico(segmento)
        if not nome_canonico:
            continue

        nome_formatado = _aplica_sigla_uc(nome_canonico)
        if nome_formatado not in nomes_canonicos:
            nomes_canonicos.append(nome_formatado)

    return ";".join(nomes_canonicos) or None


def extrai_uc(soup: BeautifulSoup) -> str | None:
    """
    Extrai a(s) Unidade(s) de Conservação afetada(s) e o ato de criação.
    Se não houver rótulo próprio, procura a UC no cabeçalho ou na apresentação
    da autoridade responsável pelo documento.
    """
    label_tag = soup.find(
        lambda tag: tag.name in ("p", "div", "td")
        and _PADRAO_ROTULO_UC.match(tag.get_text(" ", strip=True))
    )
    if not label_tag:
        return _extrair_uc_sem_rotulo(soup)

    full = label_tag.get_text(" ", strip=True)
    match = _PADRAO_ROTULO_UC.match(full)
    if match:
        resto = match.group(1).strip()
        if resto:
            return _limpar_nome_uc(resto)

    tr = label_tag.find_parent("tr")
    if tr:
        next_tr = tr.find_next_sibling("tr")
        if next_tr:
            p = next_tr.find("p")
            if p:
                texto = p.get_text(" ", strip=True)
                return _limpar_nome_uc(texto) if texto else None

    return None


def _extrair_uc_sem_rotulo(soup: BeautifulSoup) -> str | None:
    paragrafos = soup.find_all(("p", "div"))

    # Cabeçalhos como "PARQUE NACIONAL DA TIJUCA" são a indicação mais direta.
    for tag in paragrafos:
        texto = tag.get_text(" ", strip=True)
        if texto and _PADRAO_CABECALHO_UC.match(texto):
            nome = _limpar_nome_uc(texto)
            if nome:
                return nome

    # Alguns modelos informam a UC apenas em frases como
    # "A Chefe do Parque Nacional da Tijuca, no uso das competências...".
    for tag in paragrafos:
        texto = tag.get_text(" ", strip=True)
        if texto and _PADRAO_AUTORIDADE_UC.search(texto):
            nome = _limpar_nome_uc(texto)
            if nome:
                return nome

    return None
