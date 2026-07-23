from bs4 import BeautifulSoup

from coad_parser.extractors.parties import extrai_cpf_cnpj, extrai_interessado


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def test_extrai_interessado_caixa_mista_nao_muda():
    soup = _soup("<p><strong>Interessado: </strong>Maria de Souza</p>")
    assert extrai_interessado(soup) == "Maria de Souza"


def test_extrai_interessado_caixa_alta_com_sa_vira_title_case():
    soup = _soup("<p><strong>Interessado: </strong>EMPRESA FICTICIA DE ENERGIA S.A</p>")
    assert extrai_interessado(soup) == "Empresa Ficticia de Energia S.A."


def test_extrai_interessado_caixa_alta_com_ltda_vira_title_case():
    soup = _soup("<p><strong>Interessado: </strong>COMERCIO FICTICIO LTDA</p>")
    assert extrai_interessado(soup) == "Comercio Ficticio Ltda."


def test_extrai_interessado_retorna_none_quando_ausente():
    soup = _soup("<p>documento sem esse campo</p>")
    assert extrai_interessado(soup) is None


def test_extrai_cpf_formato_pessoa_fisica():
    soup = _soup("<p><strong>CPF/CNPJ</strong>: 111.222.333-44</p>")
    assert extrai_cpf_cnpj(soup) == "111.222.333-44"


def test_extrai_cnpj_formato_pessoa_juridica():
    soup = _soup("<p><strong>CPF/CNPJ</strong>: 11.222.333/0001-44</p>")
    assert extrai_cpf_cnpj(soup) == "11.222.333/0001-44"


def test_extrai_cpf_cnpj_retorna_none_quando_ausente():
    soup = _soup("<p>documento sem esse campo</p>")
    assert extrai_cpf_cnpj(soup) is None