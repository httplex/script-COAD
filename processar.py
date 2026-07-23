from pathlib import Path

import pandas as pd

from coad_parser.loader import parse_html_document_as_dict

PASTA_ENTRADA = Path("data/raw")
PASTA_SAIDA = Path("data/output")


def main():
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)
    arquivos = sorted(PASTA_ENTRADA.glob("*.html"))

    if not arquivos:
        print(f"Nenhum arquivo .html encontrado em {PASTA_ENTRADA}")
        return

    resultados = []
    for arquivo in arquivos:
        try:
            dados = parse_html_document_as_dict(str(arquivo))
            dados["arquivo_origem"] = arquivo.name
            resultados.append(dados)
        except Exception as e:
            print(f"ERRO ao processar {arquivo.name}: {e}")

    if not resultados:
        print("Nenhum documento processado com sucesso.")
        return

    df = pd.DataFrame(resultados)
    caminho_saida = PASTA_SAIDA / "resultado.xlsx"
    df.to_excel(caminho_saida, index=False)
    print(f"{len(resultados)} documento(s) processado(s). Resultado em {caminho_saida}")


if __name__ == "__main__":
    main()