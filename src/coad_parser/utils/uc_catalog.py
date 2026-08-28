import csv
import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from functools import lru_cache
from importlib.resources import files

from .text_utils import titulo_com_artigos_minusculos

_ARQUIVO_CNUC = "cnuc_2026_03.csv"
_LIMITE_SIMILARIDADE = 0.84
_MARGEM_AMBIGUIDADE = 0.05
_PALAVRAS_IGNORADAS = {"A", "AS", "O", "OS", "DE", "DA", "DO", "DAS", "DOS", "E"}
_SUFIXOS_DESCARTADOS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS",
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
    "SP", "SE", "TO", "ICMBIO",
}

_PREFIXOS_CATEGORIA = (
    ("AREA DE PROTECAO AMBIENTAL", "APA"),
    ("PARQUE NACIONAL", "PARNA"),
    ("FLORESTA NACIONAL", "FLONA"),
    ("RESERVA EXTRATIVISTA", "RESEX"),
    ("ESERVA EXTRATIVISTA", "RESEX"),
    ("R ESERVA EXTRATIVISTA", "RESEX"),
    ("MONUMENTO NATURAL", "MONUMENTO NATURAL"),
    ("ESTACAO ECOLOGICA", "ESTACAO ECOLOGICA"),
    ("RESERVA BIOLOGICA", "RESERVA BIOLOGICA"),
    ("REFUGIO DE VIDA SILVESTRE", "REFUGIO DE VIDA SILVESTRE"),
    ("REFUGIO DA VIDA SILVESTRE", "REFUGIO DE VIDA SILVESTRE"),
    ("AREA DE RELEVANTE INTERESSE ECOLOGICO", "AREA DE RELEVANTE INTERESSE ECOLOGICO"),
    ("RESERVA DE FAUNA", "RESERVA DE FAUNA"),
    ("RESERVA DE DESENVOLVIMENTO SUSTENTAVEL", "RESERVA DE DESENVOLVIMENTO SUSTENTAVEL"),
    ("RESERVA PARTICULAR DO PATRIMONIO NATURAL", "RESERVA PARTICULAR DO PATRIMONIO NATURAL"),
    ("APA", "APA"),
    ("PARNA", "PARNA"),
    ("FLONA", "FLONA"),
    ("RESEX", "RESEX"),
    ("REVIS", "REFUGIO DE VIDA SILVESTRE"),
    ("ESEC", "ESTACAO ECOLOGICA"),
    ("MONA", "MONUMENTO NATURAL"),
    ("REBIO", "RESERVA BIOLOGICA"),
    ("RPPN", "RESERVA PARTICULAR DO PATRIMONIO NATURAL"),
    ("RDS", "RESERVA DE DESENVOLVIMENTO SUSTENTAVEL"),
    ("ARIE", "AREA DE RELEVANTE INTERESSE ECOLOGICO"),
    ("AREA DE PROTECAO", "APA"),
    ("PARQUE", "PARNA"),
)

_PADRAO_INICIO_RUIDO = re.compile(
    r"(?:[.;]|\s+-\s+|\s*/\s*)?\b(?:"
    r"Decreto|Dec\.?|Lei|Portaria|Resolução|Medida\s+Provisória|"
    r"Limites?\s+alterados?|Unidade\s+de\s+Conservação\s+do\s+grupo"
    r")\b.*$",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True)
class UnidadeCanonica:
    nome: str
    categoria: str | None
    tokens_nome: tuple[str, ...]


def _normalizar(texto: str) -> str:
    sem_acentos = "".join(
        caractere
        for caractere in unicodedata.normalize("NFKD", texto.upper())
        if not unicodedata.combining(caractere)
    )
    return re.sub(r"[^A-Z0-9]+", " ", sem_acentos).strip()


def _separar_categoria(texto: str) -> tuple[str | None, str]:
    normalizado = _normalizar(texto)

    for prefixo, categoria in _PREFIXOS_CATEGORIA:
        encontrado = re.search(rf"(?:^|\s){re.escape(prefixo)}(?:\s|$)", normalizado)
        if not encontrado:
            continue
        if encontrado.end() == len(normalizado):
            return categoria, ""
        return categoria, normalizado[encontrado.end() :].strip()

    return None, normalizado


def _tokens_significativos(texto: str) -> tuple[str, ...]:
    tokens = [token for token in texto.split() if token not in _PALAVRAS_IGNORADAS]
    while tokens and tokens[-1] in _SUFIXOS_DESCARTADOS:
        tokens.pop()
    return tuple(tokens)


@lru_cache(maxsize=1)
def _carregar_catalogo() -> tuple[UnidadeCanonica, ...]:
    caminho = files("coad_parser").joinpath("data", _ARQUIVO_CNUC)
    unidades = []

    with caminho.open("r", encoding="utf-8", newline="") as arquivo:
        for linha in csv.DictReader(arquivo, delimiter=";"):
            if linha["Esfera Administrativa"].strip().casefold() != "federal":
                continue

            nome_oficial = linha["Nome da UC"].strip()
            if not nome_oficial:
                continue

            categoria, nome_base = _separar_categoria(nome_oficial)
            tokens_nome = _tokens_significativos(nome_base)
            unidades.append(
                UnidadeCanonica(
                    nome=titulo_com_artigos_minusculos(nome_oficial),
                    categoria=categoria,
                    tokens_nome=tokens_nome,
                )
            )

    return tuple(unidades)


def encontrar_nome_canonico(nome_extraido: str) -> str | None:
    texto_sem_ruido = _PADRAO_INICIO_RUIDO.sub("", nome_extraido).strip()
    categoria, nome_base = _separar_categoria(texto_sem_ruido)
    tokens_extraidos = _tokens_significativos(nome_base)
    if not tokens_extraidos:
        return None

    candidatos = [
        unidade
        for unidade in _carregar_catalogo()
        if categoria is None or unidade.categoria == categoria
    ]

    exatos = [
        unidade for unidade in candidatos if unidade.tokens_nome == tokens_extraidos
    ]
    if len(exatos) == 1:
        return exatos[0].nome

    conjunto_extraido = set(tokens_extraidos)
    por_conteudo = [
        unidade
        for unidade in candidatos
        if conjunto_extraido.issubset(set(unidade.tokens_nome))
    ]
    if len(por_conteudo) == 1:
        return por_conteudo[0].nome

    if categoria is not None:
        por_prefixo = [
            unidade
            for unidade in candidatos
            if len(tokens_extraidos) >= len(unidade.tokens_nome)
            and tokens_extraidos[: len(unidade.tokens_nome)] == unidade.tokens_nome
        ]
        if len(por_prefixo) == 1:
            return por_prefixo[0].nome

        nomes_contidos = [
            unidade
            for unidade in candidatos
            if set(unidade.tokens_nome).issubset(conjunto_extraido)
        ]
        if len(nomes_contidos) == 1:
            return nomes_contidos[0].nome

    texto_extraido = " ".join(tokens_extraidos)
    pontuados = sorted(
        [
            (
                _calcular_similaridade(
                    texto_extraido,
                    tokens_extraidos,
                    unidade.tokens_nome,
                    permitir_janelas=categoria is not None,
                ),
                unidade,
            )
            for unidade in candidatos
        ],
        key=lambda item: item[0],
    )
    if not pontuados:
        return None

    melhor_pontuacao, melhor_unidade = pontuados[-1]
    segunda_pontuacao = pontuados[-2][0] if len(pontuados) > 1 else 0.0

    if (
        melhor_pontuacao >= _LIMITE_SIMILARIDADE
        and melhor_pontuacao - segunda_pontuacao >= _MARGEM_AMBIGUIDADE
    ):
        return melhor_unidade.nome

    return None


def _calcular_similaridade(
    texto_extraido: str,
    tokens_extraidos: tuple[str, ...],
    tokens_oficiais: tuple[str, ...],
    *,
    permitir_janelas: bool,
) -> float:
    texto_oficial = " ".join(tokens_oficiais)
    pontuacoes = [SequenceMatcher(None, texto_extraido, texto_oficial).ratio()]

    if permitir_janelas and len(tokens_extraidos) >= len(tokens_oficiais):
        tamanho = len(tokens_oficiais)
        pontuacoes.extend(
            SequenceMatcher(
                None,
                " ".join(tokens_extraidos[inicio : inicio + tamanho]),
                texto_oficial,
            ).ratio()
            for inicio in range(len(tokens_extraidos) - tamanho + 1)
        )

    return max(pontuacoes)
