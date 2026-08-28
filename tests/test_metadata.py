from bs4 import BeautifulSoup

from coad_parser.extractors.metadata import (
    extrai_data_assinatura,
    extrai_numero_autorizacao,
    extrai_numero_processo,
    extrai_numero_sei,
)


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def test_extrai_numero_autorizacao_encontra_valor():
    soup = _soup("<p>autorização direta Nº 12/2025</p>")
    assert extrai_numero_autorizacao(soup) == "12/2025"


def test_extrai_numero_autorizacao_retorna_none_quando_ausente():
    soup = _soup("<p>documento sem esse campo</p>")
    assert extrai_numero_autorizacao(soup) is None


def test_extrai_numero_processo_formato_padrao():
    soup = _soup("<p>Processo nº 02122.001396/2025-18</p>")
    assert extrai_numero_processo(soup) == "02122.001396/2025-18"


def test_extrai_numero_sei_do_titulo():
    soup = _soup("<html><title>Doc - 020968747 - Autorização</title></html>")
    assert extrai_numero_sei(soup) == "020968747"


def test_extrai_data_assinatura_do_rodape():
    html = "<p>Documento assinado eletronicamente por Fulano, em 22/07/2026, às 10:00</p>"
    soup = _soup(html)
    assert extrai_data_assinatura(soup) == "22/07/2026"
