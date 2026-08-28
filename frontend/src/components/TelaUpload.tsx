import { useCallback, useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import type { ResultadoDocumento } from "@/components/TelaResultado"

const API_URL = "http://localhost:8000"
const TAMANHO_LOTE = 250

type Props = {
  onProcessado: (resultados: ResultadoDocumento[]) => void
}

export function TelaUpload({ onProcessado }: Props) {
  const [arquivos, setArquivos] = useState<File[]>([])
  const [carregando, setCarregando] = useState(false)
  const [processados, setProcessados] = useState(0)
  const [erro, setErro] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const pastaInputRef = useRef<HTMLInputElement>(null)

  const adicionarArquivos = useCallback((novos: FileList | null) => {
    if (!novos) return
    const html = Array.from(novos).filter((f) => f.name.toLowerCase().endsWith(".html"))
    setArquivos((atual) => [...atual, ...html])
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      adicionarArquivos(e.dataTransfer.files)
    },
    [adicionarArquivos]
  )

  const removerArquivo = (indice: number) => {
    setArquivos((atual) => atual.filter((_, i) => i !== indice))
  }

  const processar = async () => {
    setCarregando(true)
    setProcessados(0)
    setErro(null)
    try {
      const resultados: ResultadoDocumento[] = []
      let totalProcessados = 0

      const processarLote = async (lote: File[]): Promise<void> => {
        const formData = new FormData()
        lote.forEach((arquivo) => formData.append("arquivos", arquivo))

        const resposta = await fetch(`${API_URL}/documents`, {
          method: "POST",
          body: formData,
        })

        if (!resposta.ok) {
          if ((resposta.status === 400 || resposta.status === 413) && lote.length > 1) {
            const metade = Math.ceil(lote.length / 2)
            await processarLote(lote.slice(0, metade))
            await processarLote(lote.slice(metade))
            return
          }

          const corpo = await resposta.text()
          let detalhe = corpo

          try {
            const json = JSON.parse(corpo)
            detalhe = typeof json.detail === "string" ? json.detail : corpo
          } catch {
            // Mantém o corpo original quando a resposta não é JSON.
          }

          const arquivo = lote.length === 1 ? ` (${lote[0].name})` : ""
          throw new Error(
            `Erro ${resposta.status} ao processar${arquivo}${detalhe ? `: ${detalhe}` : ""}`
          )
        }

        const resultadosLote: ResultadoDocumento[] = await resposta.json()
        resultados.push(...resultadosLote)
        totalProcessados += lote.length
        setProcessados(totalProcessados)
      }

      for (let inicio = 0; inicio < arquivos.length; inicio += TAMANHO_LOTE) {
        const lote = arquivos.slice(inicio, inicio + TAMANHO_LOTE)
        await processarLote(lote)
      }

      onProcessado(resultados)
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Erro desconhecido")
    } finally {
      setCarregando(false)
    }
  }

  return (
    <div className="mx-auto max-w-2xl p-8">
      <h1 className="mb-6 text-2xl font-semibold">Processar documentos COAD</h1>

      <Card
        className="flex flex-col items-center justify-center gap-3 border-2 border-dashed p-10 text-center"
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
      >
        <p className="text-sm text-muted-foreground">Arraste arquivos .html aqui, ou</p>
        <input
          ref={inputRef}
          type="file"
          accept=".html"
          multiple
          className="hidden"
          onChange={(e) => adicionarArquivos(e.target.files)}
        />
        <input
          ref={pastaInputRef}
          type="file"
          // @ts-expect-error webkitdirectory não está nos tipos padrão do React/DOM
          webkitdirectory=""
          multiple
          className="hidden"
          onChange={(e) => adicionarArquivos(e.target.files)}
        />
        <Button variant="secondary" onClick={() => pastaInputRef.current?.click()}>
          Escolher pasta
        </Button>
        <Button variant="secondary" onClick={() => inputRef.current?.click()}>
          Escolher arquivos
        </Button>
      </Card>

      {arquivos.length > 0 && (
        <details className="mt-4 rounded-md border px-4 py-3 text-sm">
          <summary className="cursor-pointer select-none font-medium">
            {arquivos.length} arquivo(s) selecionado(s) — ver lista
          </summary>
          <ul className="mt-3 max-h-64 space-y-1 overflow-y-auto pr-2">
            {arquivos.map((arquivo, indice) => (
              <li
                key={`${arquivo.name}-${arquivo.size}-${arquivo.lastModified}-${indice}`}
                className="flex items-center justify-between gap-4"
              >
                <span className="truncate" title={arquivo.name}>
                  {arquivo.name}
                </span>
                <button
                  type="button"
                  className="shrink-0 text-muted-foreground hover:text-destructive"
                  onClick={() => removerArquivo(indice)}
                >
                  remover
                </button>
              </li>
            ))}
          </ul>
        </details>
      )}

      {erro && <p className="mt-4 text-sm text-destructive">{erro}</p>}

      <Button
        className="mt-6 w-full"
        disabled={arquivos.length === 0 || carregando}
        onClick={processar}
      >
        {carregando
          ? `Processando ${processados} de ${arquivos.length}...`
          : `Processar ${arquivos.length || ""} documento(s)`}
      </Button>
    </div>
  )
}
