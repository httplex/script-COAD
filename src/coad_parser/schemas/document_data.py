from pydantic import BaseModel


class DocumentData(BaseModel):
    numero_autorizacao: str | None = None
    numero_processo: str | None = None
    numero_sei: str | None = None
    ucs_envolvidas: str | None = None
    atividade: str | None = None
    interessado: str | None = None
    cpf_cnpj: str | None = None
    condicoes_especificas: str | None = None
    data_assinatura: str | None = None
    data_documento: str | None = None
    coordenadas_brutas: str | None = None