from bs4 import BeautifulSoup

from coad_parser.extractors.uc import extrai_uc, reconciliar_ucs


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


def test_extrai_uc_reserva_extrativista_vira_resex():
    html = (
        "<p><strong>Unidade de Conservação afetada e ato de criação: </strong>"
        "Reserva Extrativista Marinha Fictícia - Decreto Federal nº 123/2000.</p>"
    )
    soup = _soup(html)
    assert extrai_uc(soup) == "RESEX Marinha Fictícia"


def test_extrai_uc_remove_ato_de_criacao_separado_por_barra():
    html = """
    <tr>
        <td colspan="5">
            <p class="Texto_Justificado"><strong>Unidade de Conservação afetada e ato de criação:&nbsp;Flona Cabedelo/</strong>Decreto Federal de 2 de junho de 2004</p>
        </td>
    </tr>
    """
    soup = _soup(html)
    assert extrai_uc(soup) == "FLONA da Restinga de Cabedelo"


def test_extrai_uc_floresta_nacional_com_atos_separados_por_barras():
    html = """
    <tr>
        <td colspan="2">
            <p class="Texto_Justificado"><strong>Unidade de Conservação afetada e ato de criação:&nbsp;&nbsp;</strong>FLORESTA NACIONAL DO TAPAJÓS/Decreto de Criação n°&nbsp;73.684, de 19 de fevereiro de 1974/Limites alterados pela Lei 12.678 de 25 de junho de 2012.&nbsp;&nbsp;</p>
        </td>
    </tr>
    """
    soup = _soup(html)
    assert extrai_uc(soup) == "FLONA do Tapajós"


def test_extrai_uc_prioriza_rotulo_explicito_e_ignora_condicionantes():
    html = """
    <table>
        <tr>
            <td>
                <p>Autoriza a atividade no que diz respeito aos impactos ambientais
                sobre as Unidades de Conservação federais afetadas.</p>
            </td>
        </tr>
    </table>
    <table>
        <tr>
            <td><strong>Unidades de Conservação afetadas: </strong>Parque Nacional de Aparados da Serra</td>
        </tr>
    </table>
    <table>
        <tr>
            <td>
                <div><strong>Condicionantes Gerais:</strong></div>
                <p>O ICMBio deverá ser comunicado em caso de acidentes que possam
                afetar a Unidade de Conservação.</p>
                <div><strong>Condicionantes Específicas:</strong></div>
                <p>1. Primeira condição específica.</p>
            </td>
        </tr>
    </table>
    """
    soup = _soup(html)
    assert extrai_uc(soup) == "PARNA de Aparados da Serra"


def test_extrai_uc_preserva_barra_do_nome_e_remove_decreto():
    html = """
    <p class="Texto_Justificado">
        <strong>Unidade de Conservação afetada e ato de criação:&nbsp;</strong>
        <span>APA da Bacia do Rio São João/Mico-Leão-Dourado, criada pelo Decreto s/nº de 27 de junho 2002.</span>
    </p>
    """
    soup = _soup(html)
    assert extrai_uc(soup) == "APA da Bacia do Rio São João - Mico-leão-dourado"


def test_extrai_uc_remove_uf_apos_barra_no_final():
    html = (
        "<p><strong>Unidade de Conservação afetada e ato de criação: "
        "Monumento Natural dos Pontões Capixabas/ES</strong></p>"
    )
    soup = _soup(html)
    assert extrai_uc(soup) == "MONA dos Pontões Capixabas"


def test_extrai_uc_remove_data_apos_barra():
    html = (
        "<p><strong>Unidade de Conservação afetada e ato de criação: "
        "Floresta Nacional do Tapajós / 19 de fevereiro de 1974.</strong></p>"
    )
    soup = _soup(html)
    assert extrai_uc(soup) == "FLONA do Tapajós"


def test_extrai_uc_nao_separa_ilhas_e_varzeas_e_remove_decreto_apos_ponto_e_virgula():
    html = """
    <p class="Texto_Justificado">
        <strong>Unidade de Conservação afetada e ato de criação:&nbsp;</strong>
        <span>APA Ilhas e Várzeas do Rio Paraná; </span>
        <span>Decreto de criação s/nº da APAIVRP, de 30/09/1997.</span>
    </p>
    """
    soup = _soup(html)
    assert extrai_uc(soup) == "APA Ilhas e Várzeas do Rio Paraná"


def test_extrai_uc_remove_decreto_apos_virgula_e_preserva_sigla_parna():
    html = (
        "<p><strong>Unidade de Conservação afetada e ato de criação:&nbsp;&nbsp;</strong>"
        "PARNA DO CATIMBAU, Decreto de Criação S/N de 13/12/2002.</p>"
    )
    soup = _soup(html)
    assert extrai_uc(soup) == "PARNA do Catimbau"


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
    assert extrai_uc(soup) == "Reserva Fictícia do Rio Verde"


def test_extrai_uc_retorna_none_quando_ausente():
    soup = _soup("<p>documento sem esse campo</p>")
    assert extrai_uc(soup) is None


def test_extrai_uc_sem_rotulo_pelo_cabecalho_e_texto_da_autoridade():
    html = """
    <p class="Texto_Centralizado"><strong>MINISTÉRIO DO MEIO AMBIENTE E MUDANÇA DO CLIMA</strong></p>
    <p class="Texto_Centralizado"><strong>INSTITUTO CHICO MENDES DE CONSERVAÇÃO DA BIODIVERSIDADE</strong></p>
    <p class="Texto_Centralizado"><strong>PARQUE NACIONAL DA TIJUCA</strong></p>
    <p class="Texto_Centralizado_Maiusculas">autorização direta Nº 22/2025</p>
    <p class="Texto_Justificado">A Chefe do Parque Nacional da Tijuca, no uso das competências atribuídas pela Portaria nº 854.</p>
    """
    soup = _soup(html)
    assert extrai_uc(soup) == "PARNA da Tijuca"


def test_extrai_uc_sem_rotulo_pelo_texto_da_autoridade():
    soup = _soup(
        "<p>A Chefe do Parque Nacional da Tijuca, no uso das competências "
        "atribuídas pela Portaria nº 854.</p>"
    )
    assert extrai_uc(soup) == "PARNA da Tijuca"


def test_extrai_uc_sem_rotulo_nao_depende_de_uma_uc_especifica():
    soup = _soup(
        "<p>A Chefe da Floresta Nacional do Tapajós, no uso das competências "
        "atribuídas pela Portaria nº 123.</p>"
    )
    assert extrai_uc(soup) == "FLONA do Tapajós"


def test_extrai_uc_sem_rotulo_ignora_mencao_generica_no_texto():
    soup = _soup("<p>Atividade realizada próximo ao Parque Nacional da Tijuca.</p>")
    assert extrai_uc(soup) is None


def test_extrai_uc_retorna_none_quando_valor_contem_apenas_decreto():
    soup = _soup(
        "<p><strong>Unidade de Conservação afetada e ato de criação: </strong>"
        "Decreto s/n de 05 de junho de 2008</p>"
    )
    assert extrai_uc(soup) is None


def test_extrai_uc_retorna_none_quando_valor_contem_categoria_sem_nome():
    soup = _soup(
        "<p><strong>Unidade de Conservação afetada e ato de criação: </strong>"
        "Refúgio da Vida Silvestre. Decreto s/n de 11 de junho de 2010</p>"
    )
    assert extrai_uc(soup) is None


def test_reconciliacao_final_remove_sobras_e_padroniza_nome():
    assert (
        reconciliar_ucs(
            "Refúgio da Vida Silvestre de Boa Nova. Decreto s/n de 11 de junho de 2010"
        )
        == "REVIS de Boa Nova"
    )


def test_reconciliacao_final_descarta_valor_sem_uc_identificavel():
    assert reconciliar_ucs("Decreto s/n de 05 de junho de 2008") is None


def test_reconciliacao_final_trata_multiplas_ucs():
    assert (
        reconciliar_ucs("APA de Cairuçu;PARNA da Serra da Bocaina")
        == "APA de Cairuçu;PARNA da Serra da Bocaina"
    )


def test_reconciliacao_final_padroniza_mona_revis_e_esec():
    assert reconciliar_ucs("Monumento Natural dos Pontões Capixabas") == "MONA dos Pontões Capixabas"
    assert reconciliar_ucs("Refúgio de Vida Silvestre de Una") == "REVIS de Una"
    assert reconciliar_ucs("Estação Ecológica do Taim") == "ESEC do Taim"


def test_reconciliacao_final_padroniza_rebio_arie_rppn_e_rds():
    assert reconciliar_ucs("Rebio da Contagem") == "REBIO da Contagem"
    assert reconciliar_ucs("Arie Matão de Cosmópolis") == "ARIE Matão de Cosmópolis"
    assert reconciliar_ucs("RPPN Sítio do Jacú") == "RPPN Sítio do Jacu"
    assert reconciliar_ucs("RDS Nascentes Geraizeiras") == "RDS Nascentes Geraizeiras"


def test_reconciliacao_final_usa_artigos_do_nome_oficial_cnuc():
    assert reconciliar_ucs("PARNA Aparados Serra") == "PARNA de Aparados da Serra"
    assert (
        reconciliar_ucs("APA Ilhas Várzeas do Rio Paraná")
        == "APA Ilhas e Várzeas do Rio Paraná"
    )


def test_reconciliacao_final_encurta_apa_de_fernando_de_noronha():
    assert (
        reconciliar_ucs(
            "Área de Proteção Ambiental de Fernando de Noronha - Rocas - São Pedro e São Paulo"
        )
        == "APA de Fernando de Noronha"
    )
