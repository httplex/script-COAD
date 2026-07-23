import { useState } from "react"
import { TelaUpload } from "@/components/TelaUpload"
import { TelaResultado, type ResultadoDocumento } from "@/components/TelaResultado"

function App() {
  const [resultados, setResultados] = useState<ResultadoDocumento[] | null>(null)
  const [arquivos, setArquivos] = useState<File[]>([])

  if (!resultados) {
    return (
      <TelaUpload
        onProcessado={(resultados, arquivos) => {
          setResultados(resultados)
          setArquivos(arquivos)
        }}
      />
    )
  }

  return (
    <TelaResultado
      resultados={resultados}
      arquivos={arquivos}
      onVoltar={() => setResultados(null)}
    />
  )
}

export default App