from coad_parser.utils.uc_catalog import encontrar_nome_canonico


def test_catalogo_encontra_uc_por_nome_oficial():
    assert encontrar_nome_canonico("FLONA do Tapajós") == "Floresta Nacional do Tapajós"


def test_catalogo_corrige_nome_incompleto_unico_na_categoria():
    assert (
        encontrar_nome_canonico("FLONA Cabedelo")
        == "Floresta Nacional da Restinga de Cabedelo"
    )


def test_catalogo_tolera_artigos_e_conjuncoes_ausentes():
    assert (
        encontrar_nome_canonico("APA Ilhas Várzeas do Rio Paraná")
        == "Área de Proteção Ambiental Ilhas e Várzeas do Rio Paraná"
    )


def test_catalogo_descarta_decreto_residual_apos_nome():
    assert (
        encontrar_nome_canonico(
            "PARNA do Catimbau, Decreto de Criação S/N de 13/12/2002"
        )
        == "Parque Nacional do Catimbau"
    )


def test_catalogo_descarta_observacao_residual_apos_nome():
    assert (
        encontrar_nome_canonico(
            "FLONA do Tapajós limites alterados pela Lei 12.678 de 2012"
        )
        == "Floresta Nacional do Tapajós"
    )


def test_catalogo_reconhece_categoria_alternativa_com_decreto():
    assert (
        encontrar_nome_canonico(
            "Refúgio da Vida Silvestre de Boa Nova. Decreto s/n de 11 de junho de 2010"
        )
        == "Refúgio de Vida Silvestre de Boa Nova"
    )


def test_catalogo_reconhece_sigla_revis_com_decreto():
    assert (
        encontrar_nome_canonico("REVIS de Boa Nova. Decreto s/n de 11 de junho de 2010")
        == "Refúgio de Vida Silvestre de Boa Nova"
    )


def test_catalogo_reconhece_sigla_mona():
    assert (
        encontrar_nome_canonico("MONA dos Pontões Capixabas")
        == "Monumento Natural dos Pontões Capixabas"
    )


def test_catalogo_encontra_categoria_dentro_de_frase():
    assert (
        encontrar_nome_canonico("Trata-se da RESEX do Rio Ouro Preto")
        == "Reserva Extrativista do Rio Ouro Preto"
    )


def test_catalogo_completa_nome_oficial_antes_do_decreto():
    assert (
        encontrar_nome_canonico(
            "APA de Fernando de Noronha/PE. Decreto de criação nº 92.755 de 05 de junho de 1986"
        )
        == "Área de Proteção Ambiental de Fernando de Noronha - Rocas - São Pedro e São Paulo"
    )


def test_catalogo_remove_texto_introdutorio_apos_nome():
    assert (
        encontrar_nome_canonico(
            "O PARNA Serra do Teixeira, Unidade de Conservação do grupo de Proteção Integral"
        )
        == "Parque Nacional da Serra do Teixeira"
    )


def test_catalogo_nao_forca_correspondencia_insegura():
    assert encontrar_nome_canonico("PARNA Nome Totalmente Desconhecido") is None
