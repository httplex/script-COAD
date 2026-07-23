import re
from bs4 import BeautifulSoup

from ..utils.html_helpers import encontra_tag_por_label
from ..utils.text_utils import titulo_com_artigos_minusculos

_SIGLAS_UC = {
    r"\bÁrea de Proteção Ambiental\b": "APA",
    r"\bParque Nacional\b": "PARNA",
}


def _aplica_sigla_uc(nome: str) -> str:
    for padrao, sigla in _SIGLAS_UC.items():
        nome = re.sub(padrao, sigla, nome, flags=re.IGNORECASE)
    return nome


def _limpar_segmento_uc(segmento: str) -> str:
    sem_parenteses = re.sub(r"\s*\([^)]*\)", "", segmento)
    sem_ato = re.split(r"\s+-\s+", sem_parenteses, maxsplit=1)[0]
    sem_ato = re.sub(r"\s{2,}", " ", sem_ato).strip()
    sem_ato = sem_ato.rstrip(".").strip()

    if sem_ato.isupper():
        sem_ato = titulo_com_artigos_minusculos(sem_ato)

    return _aplica_sigla_uc(sem_ato)


def _limpar_nome_uc(texto: str) -> str:
    segmentos = re.split(r"\s+e\s+", texto)
    limpos = [_limpar_segmento_uc(seg) for seg in segmentos if _limpar_segmento_uc(seg)]
    return ";".join(limpos)


def extrai_uc(soup: BeautifulSoup) -> str | None:
    """
    Extrai a(s) Unidade(s) de Conservação afetada(s) e o ato de criação.
    Não cobre layouts sem rótulo próprio (ex.: <p class="Texto_Centralizado">
    solto) — retorna None nesse caso, tratado como gap conhecido por ora.
    """
    label_tag = encontra_tag_por_label(soup, "Unidade de Conservação")
    if not label_tag:
        return None

    full = label_tag.get_text(" ", strip=True)
    match = re.search(r"Unidade de Conservação.*?:\s*(.+)$", full, flags=re.IGNORECASE)
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