# script_COADv1

Ferramenta que extrai dados específicos de documentos `.html` exportados do SEI, mirando na base de dados da COAD/ICMBio. O objetivo é fazer o trabalho de cadastro de informações ser feito automaticamente, mais rápido e com menos erro manual.

## Estrutura

- `src/coad_parser/` — pacote Python com a lógica de extração (`parser.py`), a API HTTP (`api.py`, FastAPI) e o runner de lote por pasta (`loader.py` + `processar.py`)
- `frontend/` — interface web (Vite + React + shadcn/ui) para upload de documentos e download do resultado consolidado
- `tests/` — suíte pytest cobrindo os extractors, com fixtures sintéticas (sem dado pessoal real)

## Como funciona

Cada extractor busca um campo pré-definido (rótulo específico, formato de data, etc.) dentro da estrutura HTML do documento. Se não encontra, retorna `None` em vez de arriscar um valor errado — precisão acima de cobertura total.

## Rodando localmente (sem Docker)

**Backend:**
```bash
pip install -e ".[dev]"
uvicorn coad_parser.api:app --reload
```
API disponível em `http://localhost:8000` (documentação interativa em `/docs`).

**Frontend** (em outro terminal):
```bash
cd frontend
npm install
npm run dev
```
Interface disponível em `http://localhost:5173` (ou próxima porta livre).

**Processamento em lote sem interface** (coloca os `.html` em `data/raw/`):
```bash
python processar.py
```
Gera `data/output/resultado.xlsx`.

## Rodando com Docker

```bash
docker compose up --build
```
Backend em `http://localhost:8000`, frontend em `http://localhost:5173`.

## API

- `POST /documents` — recebe 1+ arquivos `.html` (multipart/form-data, campo `arquivos`), devolve JSON por documento: `{"arquivo": str, "sucesso": bool, "dados": {...} | "erro": str}`
- `POST /documents/export` — mesma entrada, devolve um `.xlsx` consolidado (só com os documentos processados com sucesso)

Campos extraídos por documento (`dados`): `numero_autorizacao`, `numero_processo`, `numero_sei`, `ucs_envolvidas`, `atividade`, `interessado`, `cpf_cnpj`, `condicoes_especificas`, `data_assinatura`, `data_documento`, `coordenadas_brutas`.

## Testes

```bash
pytest
```

## Futuras melhorias

- Categorização/rótulo mais sucinto para o campo `atividade`
- Suporte ao layout de UC sem rótulo próprio (`<p class="Texto_Centralizado">` solto)
- Persistência de histórico dos documentos processados (hoje não há banco de dados)
