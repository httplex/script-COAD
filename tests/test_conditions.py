from bs4 import BeautifulSoup

from coad_parser.extractors.conditions import extrai_condicoes_especificas


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def test_extrai_condicoes_junta_paragrafos_ate_condicoes_gerais():
    html = """
    <table><tr><td>
        <p>Condições Específicas: Primeira condição aqui.</p>
        <p>Segunda condição aqui.</p>
        <p>Condições Gerais:</p>
        <p>Isso não deve aparecer.</p>
    </td></tr></table>
    """
    soup = _soup(html)
    resultado = extrai_condicoes_especificas(soup)
    assert resultado == "Primeira condição aqui.\nSegunda condição aqui."


def test_extrai_condicoes_para_no_rodape_de_assinatura():
    html = """
    <table><tr><td>
        <p>Condições Específicas: Única condição.</p>
        <p>Documento assinado eletronicamente por Fulano.</p>
    </td></tr></table>
    """
    soup = _soup(html)
    assert extrai_condicoes_especificas(soup) == "Única condição."


def test_extrai_condicoes_retorna_none_quando_ausente():
    soup = _soup("<p>documento sem esse campo</p>")
    assert extrai_condicoes_especificas(soup) is None