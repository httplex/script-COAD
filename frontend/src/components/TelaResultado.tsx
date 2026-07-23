import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

const API_URL = "http://localhost:8000"

type DocumentoExtraido = {
  numero_autorizacao: string | null
  numero_processo: string | null
  numero_sei: string | null
  ucs_envolvidas: string | null
  atividade: string | null
  interessado: string | null
  cpf_cnpj: string | null
  condicoes_especificas: string | null
  data_assinatura: string | null
  data_documento: string | null
  coordenadas_brutas: string | null
}

export type ResultadoDocumento =
  | { arquivo: string; sucesso: true; dados: DocumentoExtraido }
  | { arquivo: string; sucesso: false; erro: string }

const CAMPOS: { chave: keyof DocumentoExtraido; rotulo: string }[] = [
  { chave: "numero_sei", rotulo: "Número SEI" },
  { chave: "numero_autorizacao", rotulo: "Autorização" },
  { chave: "numero_processo", rotulo: "Processo" },
  { chave: "ucs_envolvidas", rotulo: "UC(s)" },
  { chave: "interessado", rotulo: "Interessado" },
  { chave: "cpf_cnpj", rotulo: "CPF/CNPJ" },
  { chave: "data_assinatura", rotulo: "Assinatura" },
  { chave: "data_documento", rotulo: "Documento" },
  { chave: "atividade", rotulo: "Atividade" },
  { chave: "condicoes_especificas", rotulo: "Condições específicas" },
  { chave: "coordenadas_brutas", rotulo: "Coordenadas" },
]

type Props = {
  resultados: ResultadoDocumento[]
  arquivos: File[]
  onVoltar: () => void
}

export function TelaResultado({ resultados, arquivos, onVoltar }: Props) {
  const [baixando, setBaixando] = useState(false)
  const [erroDownload, setErroDownload] = useState<string | null>(null)
  const sucessos = resultados.filter((r) => r.sucesso).length

  const baixarPlanilha = async () => {
    setBaixando(true)
    setErroDownload(null)
    try {
      const formData = new FormData()
      arquivos.forEach((arquivo) => formData.append("arquivos", arquivo))

      const resposta = await fetch(`${API_URL}/documents/export`, {
        method: "POST",
        body: formData,
      })

      if (!resposta.ok) {
        throw new Error(`Erro ${resposta.status} ao exportar planilha`)
      }

      const blob = await resposta.blob()
      const url = URL.createObjectURL(blob)
      const link = document.createElement("a")
      link.href = url
      link.download = "resultado.xlsx"
      link.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      setErroDownload(e instanceof Error ? e.message : "Erro desconhecido")
    } finally {
      setBaixando(false)
    }
  }

  return (
    <div className="mx-auto max-w-4xl p-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">
          Resultado ({sucessos}/{resultados.length} processado(s))
        </h1>
        <div className="flex gap-2">
          <Button onClick={baixarPlanilha} disabled={baixando}>
            {baixando ? "Gerando..." : "Baixar planilha"}
          </Button>
          <Button variant="secondary" onClick={onVoltar}>
            Voltar
          </Button>
        </div>
      </div>

      {erroDownload && <p className="mb-4 text-sm text-destructive">{erroDownload}</p>}

      <div className="space-y-4">
        {resultados.map((resultado) => (
          <Card key={resultado.arquivo} className="p-4">
            <div className="mb-2 flex items-center justify-between">
              <span className="font-medium">{resultado.arquivo}</span>
              <span className={resultado.sucesso ? "text-xs text-green-600" : "text-xs text-destructive"}>
                {resultado.sucesso ? "processado" : "erro"}
              </span>
            </div>

            {!resultado.sucesso && <p className="text-sm text-destructive">{resultado.erro}</p>}

            {resultado.sucesso && (
              <dl className="grid grid-cols-1 gap-2 text-sm sm:grid-cols-2">
                {CAMPOS.map(({ chave, rotulo }) => (
                  <div key={chave}>
                    <dt className="text-xs text-muted-foreground">{rotulo}</dt>
                    <dd className="whitespace-pre-wrap">{resultado.dados[chave] ?? "—"}</dd>
                  </div>
                ))}
              </dl>
            )}
          </Card>
        ))}
      </div>
    </div>
  )
}
