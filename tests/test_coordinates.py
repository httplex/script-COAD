from bs4 import BeautifulSoup

from coad_parser.extractors.coordinates import extrai_coordenadas


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def test_extrai_coordenadas_um_par():
    soup = _soup("<p>Ponto de referência: -19.301115, -43.652507</p>")
    assert extrai_coordenadas(soup) == "-19.301115, -43.652507"


def test_extrai_coordenadas_dois_pares_juntos_com_ponto_e_virgula():
    html = "<p>Pontos: -19.301115, -43.652507 e -20.123456, -44.654321</p>"
    soup = _soup(html)
    assert extrai_coordenadas(soup) == "-19.301115, -43.652507; -20.123456, -44.654321"


def test_extrai_coordenadas_retorna_none_quando_ausente():
    soup = _soup("<p>documento sem coordenadas</p>")
    assert extrai_coordenadas(soup) is None