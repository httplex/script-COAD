from bs4 import BeautifulSoup

from coad_parser.extractors.uc import extrai_uc


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def test_extrai_uc_area_protecao_ambiental_vira_apa():
    html = (
        "<p><strong>Unidade de Conservação afetada e ato de criação: </strong>"
        "Área de Proteção Ambiental Serra Fictícia - Decreto Federal nº 12.345, "
        "de 01 de janeiro de 2000.</p>"
    )
    soup = _soup(html)
    assert extrai_uc(soup) == "APA Serra Fictícia"


def test_extrai_uc_duas_ucs_caixa_alta_separadas_por_ponto_e_virgula():
    html = (
        "<p><strong>Unidade de Conservação afetada e ato de criação: </strong>"
        "PARQUE NACIONAL FICTICIO DA MONTANHA (Decreto Federal nº 1.111/1980) e "
        "ÁREA DE PROTEÇÃO AMBIENTAL FICTICIA DO VALE (Decreto Federal nº 2.222/1990).</p>"
    )
    soup = _soup(html)
    assert extrai_uc(soup) == "PARNA Ficticio da Montanha;APA Ficticia do Vale"
    
def test_extrai_uc_rotulo_sozinho_valor_na_proxima_linha():
    html = """
    <table>
        <tr><td><p><strong>Unidade de Conservação afetada e ato de criação:</strong></p></td></tr>
        <tr><td><p>Reserva Fictícia do Rio Verde, criada conforme Decreto nº 999 de 1999.</p></td></tr>
    </table>
    """
    soup = _soup(html)
    assert extrai_uc(soup) == "Reserva Fictícia do Rio Verde, criada conforme Decreto nº 999 de 1999"


def test_extrai_uc_retorna_none_quando_ausente():
    soup = _soup("<p>documento sem esse campo</p>")
    assert extrai_uc(soup) is None