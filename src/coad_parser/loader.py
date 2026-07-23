from .parser import parse_document
from .schemas.document_data import DocumentData
from .utils.path_utils import extrai_sei_do_caminho


def parse_html_document(caminho_html: str) -> DocumentData:
    with open(caminho_html, "r", encoding="utf-8", errors="ignore") as file:
        html = file.read()

    doc = parse_document(html)

    if not doc.numero_sei:
        doc.numero_sei = extrai_sei_do_caminho(caminho_html)

    return doc


def parse_html_document_as_dict(caminho_html: str) -> dict:
    return parse_html_document(caminho_html).dict()