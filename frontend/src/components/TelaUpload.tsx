import { useCallback, useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import type { ResultadoDocumento } from "@/components/TelaResultado"

const API_URL = "http://localhost:8000"

type Props = {
  onProcessado: (resultados: ResultadoDocumento[], arquivos: File[]) => void
}

export function TelaUpload({ onProcessado }: Props) {
  const [arquivos, setArquivos] = useState<File[]>([])
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

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

  const removerArquivo = (nome: string) => {
    setArquivos((atual) => atual.filter((f) => f.name !== nome))
  }

  const processar = async () => {
    setCarregando(true)
    setErro(null)
    try {
      const formData = new FormData()
      arquivos.forEach((arquivo) => formData.append("arquivos", arquivo))

      const resposta = await fetch(`${API_URL}/documents`, {
        method: "POST",
        body: formData,
      })

      if (!resposta.ok) {
        throw new Error(`Erro ${resposta.status} ao processar documentos`)
      }

      onProcessado(await resposta.json(), arquivos)
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
        <Button variant="secondary" onClick={() => inputRef.current?.click()}>
          Escolher arquivos
        </Button>
      </Card>

      {arquivos.length > 0 && (
        <ul className="mt-4 space-y-1 text-sm">
          {arquivos.map((arquivo) => (
            <li key={arquivo.name} className="flex items-center justify-between">
              <span>{arquivo.name}</span>
              <button
                className="text-muted-foreground hover:text-destructive"
                onClick={() => removerArquivo(arquivo.name)}
              >
                remover
              </button>
            </li>
          ))}
        </ul>
      )}

      {erro && <p className="mt-4 text-sm text-destructive">{erro}</p>}

      <Button
        className="mt-6 w-full"
        disabled={arquivos.length === 0 || carregando}
        onClick={processar}
      >
        {carregando ? "Processando..." : `Processar ${arquivos.length || ""} documento(s)`}
      </Button>
    </div>
  )
}