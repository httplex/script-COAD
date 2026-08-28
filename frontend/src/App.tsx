import { useState } from "react"
import { TelaUpload } from "@/components/TelaUpload"
import { TelaResultado, type ResultadoDocumento } from "@/components/TelaResultado"

function App() {
  const [resultados, setResultados] = useState<ResultadoDocumento[] | null>(null)

  if (!resultados) {
    return (
      <TelaUpload
        onProcessado={(resultados) => {
          setResultados(resultados)
        }}
      />
    )
  }

  return (
    <TelaResultado
      resultados={resultados}
      onVoltar={() => setResultados(null)}
    />
  )
}

export default App
