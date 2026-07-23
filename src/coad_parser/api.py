import io
import pandas as pd

from fastapi import FastAPI, File, UploadFile
from .parser import parse_document
from .utils.path_utils import extrai_sei_do_caminho

from fastapi.responses import StreamingResponse

app = FastAPI(title="COAD Parser API")

TAMANHO_MAXIMO_BYTES = 5 * 1024 * 1024  # 5 MB


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

    if len(conteudo) > TAMANHO_MAXIMO_BYTES:
        return {
            "arquivo": arquivo.filename,
            "sucesso": False,
            "erro": "Arquivo excede o tamanho máximo permitido (5 MB)",
        }

    try:
        html = conteudo.decode("utf-8", errors="ignore")
        doc = parse_document(html)

        if not doc.numero_sei:
            doc.numero_sei = extrai_sei_do_caminho(arquivo.filename)

        return {"arquivo": arquivo.filename, "sucesso": True, "dados": doc.dict()}
    except Exception as e:
        return {"arquivo": arquivo.filename, "sucesso": False, "erro": str(e)}

@app.post("/documents/export")
async def exportar_documentos(arquivos: list[UploadFile] = File(...)) -> StreamingResponse:
    resultados = [await _processar_um_arquivo(arquivo) for arquivo in arquivos]

    linhas = [
        {**resultado["dados"], "arquivo_origem": resultado["arquivo"]}
        for resultado in resultados
        if resultado["sucesso"]
    ]

    df = pd.DataFrame(linhas)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=resultado.xlsx"},
    )