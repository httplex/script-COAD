from bs4 import BeautifulSoup

from coad_parser.extractors.activity import extrai_atividade


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def test_extrai_atividade_rotulo_e_valor_na_mesma_linha():
    html = """
    <table><tr><td>
        <p class="Texto_Justificado">
            <strong>Atividade/Empreendimento</strong>: Retirada de material vegetal
        </p>
    </td></tr></table>
    """
    soup = _soup(html)
    assert extrai_atividade(soup) == "Retirada de material vegetal"


def test_extrai_atividade_rotulo_sozinho_valor_na_proxima_linha():
    html = """
    <table>
        <tr><td><p><strong>Atividade/Empreendimento</strong>:</p></td></tr>
        <tr><td><p>Pesquisa científica sobre fauna local.</p></td></tr>
    </table>
    """
    soup = _soup(html)
    assert extrai_atividade(soup) == "Pesquisa científica sobre fauna local."


def test_extrai_atividade_retorna_none_quando_ausente():
    soup = _soup("<p>documento sem esse campo</p>")
    assert extrai_atividade(soup) is None


def test_extrai_atividade_como_servico_a_ser_realizado():
    html = """
    <p class="Texto_Justificado">
        · <b>SERVIÇO A SER REALIZADO: </b>Substituição da antena VHF,
        substituição do transmissor e instalação de cabo.
    </p>
    """
    soup = _soup(html)
    assert extrai_atividade(soup) == (
        "Substituição da antena VHF, substituição do transmissor e instalação de cabo."
    )
