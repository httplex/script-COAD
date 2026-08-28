import io
import re

import pandas as pd
from bs4 import BeautifulSoup
from pydantic import BaseModel

from fastapi import FastAPI, File, UploadFile
from .extractors.uc import reconciliar_ucs
from .parser import parse_document
from .schemas.document_data import DocumentData
from .utils.path_utils import extrai_sei_do_caminho
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import StreamingResponse

app = FastAPI(title="COAD Parser API")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)

TAMANHO_MAXIMO_BYTES = 5 * 1024 * 1024  # 5 MB


class ResultadoParaExportar(BaseModel):
    arquivo: str
    sucesso: bool
    dados: DocumentData | None = None
    erro: str | None = None


PADRAO_PAGINA_ERRO = re.compile(
    r"\b(404\s+not\s+found|403\s+forbidden|500\s+internal\s+server\s+error|"
    r"página\s+não\s+encontrada|acesso\s+negado|erro\s+interno\s+do\s+servidor)\b",
    flags=re.IGNORECASE,
)


@app.post("/documents")
async def processar_documentos(arquivos: list[UploadFile] = File(...)) -> list[dict]:
    return [await _processar_um_arquivo(arquivo) for arquivo in arquivos]


async def _processar_um_arquivo(arquivo: UploadFile) -> dict:
    if not arquivo.filename or not arquivo.filename.lower().endswith(".html"):
        return {
            "arquivo": arquivo.filename,
            "sucesso": False,
            "erro": "Extensão inválida, esperado .html",
        }

    conteudo = await arquivo.read()

    if not conteudo.strip():
        return {
            "arquivo": arquivo.filename,
            "sucesso": False,
            "erro": "Arquivo HTML vazio",
        }

    if len(conteudo) > TAMANHO_MAXIMO_BYTES:
        return {
            "arquivo": arquivo.filename,
            "sucesso": False,
            "erro": "Arquivo excede o tamanho máximo permitido (5 MB)",
        }

    try:
        html = conteudo.decode("utf-8", errors="ignore")

        motivo_invalido = _identificar_pagina_invalida(html)
        if motivo_invalido:
            return {
                "arquivo": arquivo.filename,
                "sucesso": False,
                "erro": motivo_invalido,
            }

        doc = parse_document(html)

        if not _possui_campos_esperados(doc):
            return {
                "arquivo": arquivo.filename,
                "sucesso": False,
                "erro": "HTML sem os campos esperados de um documento COAD",
            }

        if not doc.numero_sei:
            doc.numero_sei = extrai_sei_do_caminho(arquivo.filename)

        return {"arquivo": arquivo.filename, "sucesso": True, "dados": doc.dict()}
    except Exception as e:
        return {"arquivo": arquivo.filename, "sucesso": False, "erro": str(e)}


def _identificar_pagina_invalida(html: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    titulo = soup.title.get_text(" ", strip=True) if soup.title else ""
    texto_inicial = soup.get_text(" ", strip=True)[:5000]

    if PADRAO_PAGINA_ERRO.search(f"{titulo} {texto_inicial}"):
        return "O HTML contém uma página de erro"

    possui_senha = soup.find("input", attrs={"type": re.compile(r"^password$", re.I)})
    formulario_login = soup.find(
        "form",
        attrs={"action": re.compile(r"(login|autentica|signin)", re.I)},
    )
    titulo_login = re.search(r"\b(login|autenticação|entrar)\b", titulo, re.I)

    if possui_senha or formulario_login or titulo_login:
        return "O HTML contém uma página de login/autenticação"

    return None


def _possui_campos_esperados(doc: DocumentData) -> bool:
    campos_caracteristicos = (
        doc.numero_autorizacao,
        doc.numero_processo,
        doc.numero_sei,
        doc.ucs_envolvidas,
        doc.atividade,
        doc.interessado,
        doc.cpf_cnpj,
        doc.condicoes_especificas,
    )
    return any(valor for valor in campos_caracteristicos)

@app.post("/documents/export")
async def exportar_documentos(arquivos: list[UploadFile] = File(...)) -> StreamingResponse:
    resultados = [await _processar_um_arquivo(arquivo) for arquivo in arquivos]

    return _criar_planilha(resultados)


@app.post("/documents/export-results")
async def exportar_resultados(resultados: list[ResultadoParaExportar]) -> StreamingResponse:
    return _criar_planilha([resultado.model_dump() for resultado in resultados])


def _criar_planilha(resultados: list[dict]) -> StreamingResponse:
    campos_documento = list(DocumentData.model_fields)
    campos_obrigatorios = [
        campo for campo in campos_documento if campo != "coordenadas_brutas"
    ]
    colunas_documento = campos_documento
    registros_completos = []
    dados_faltantes = []
    htmls_quebrados = []

    for resultado in resultados:
        dados = resultado.get("dados")

        if not resultado["sucesso"] or not dados:
            htmls_quebrados.append(
                {
                    "arquivo": resultado["arquivo"],
                    "motivo": resultado.get("erro") or "Resultado sem dados extraídos",
                }
            )
            continue

        dados = {
            **dados,
            "ucs_envolvidas": reconciliar_ucs(dados.get("ucs_envolvidas")),
        }
        campos_faltantes = [
            campo
            for campo in campos_obrigatorios
            if _valor_vazio(dados.get(campo))
        ]
        if campos_faltantes:
            dados_faltantes.append(dados)
        else:
            registros_completos.append(dados)

    registros_completos.sort(key=_chave_numero_autorizacao)
    dados_faltantes.sort(key=_chave_numero_autorizacao)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame(
            registros_completos,
            columns=colunas_documento,
        ).to_excel(writer, sheet_name="Registros completos", index=False)
        pd.DataFrame(
            dados_faltantes,
            columns=colunas_documento,
        ).to_excel(writer, sheet_name="Dados faltantes", index=False)
        pd.DataFrame(
            htmls_quebrados,
            columns=["arquivo", "motivo"],
        ).to_excel(writer, sheet_name="HTMLs quebrados", index=False)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=resultado.xlsx"},
    )


def _valor_vazio(valor: object) -> bool:
    return valor is None or (isinstance(valor, str) and not valor.strip())


def _chave_numero_autorizacao(registro: dict) -> tuple:
    valor = registro.get("numero_autorizacao")
    if not isinstance(valor, str) or not valor.strip():
        return (2, 0, 0, "")

    valor = valor.strip()
    match = re.fullmatch(r"(\d+(?:\.\d+)*)\s*/\s*(\d{4})", valor)
    if match:
        numero = int(match.group(1).replace(".", ""))
        ano = int(match.group(2))
        return (0, ano, numero, valor)

    return (1, 0, 0, valor.casefold())

