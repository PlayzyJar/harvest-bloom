
import { useEffect, useState } from "react";

const fetchLDR = async () => {
  try {
    const res = await fetch("/api/ldr");
    const data = await res.json();
    return data.ldr;
  } catch {
    return null;
  }
};

function getLDRStatus(valor: number): { color: string; text: string } {
  if (valor < 50000) return { color: "#FFD700", text: "Iluminação Forte" };      // Amarelo brilhante
  if (valor < 90000) return { color: "#FFA500", text: "Iluminação Média" };      // Laranja
  if (valor < 120000) return { color: "#B197FC", text: "Iluminação Fraca" };     // Azul claro
  return { color: "#808080", text: "Pouca Luz" };                                // Cinza escuro
}

export const SensorMonitor = () => {
  const [ldrValue, setLdrValue] = useState<number | null>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      fetchLDR().then(setLdrValue);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const status = ldrValue !== null ? getLDRStatus(ldrValue) : { color: "#808080", text: "Sem leitura" };
  const barFill = ldrValue !== null ? Math.max(100 - ldrValue / 1500, 1) : 0; // Proporção visual invertida

  return (
    <div className="card bg-muted p-4 flex flex-col items-center gap-4">
      <div className="flex items-center gap-3">
        {/* SVG lâmpada com cor variável */}
        <svg width="42" height="42" viewBox="0 0 42 42" fill={status.color} xmlns="http://www.w3.org/2000/svg">
          <circle cx="21" cy="18" r="13" fill={status.color} stroke="#DDD" strokeWidth={2} />
          <rect x="17" y="31" width="8" height="7" rx="4" fill="#BBB" />
        </svg>
        <div>
          <h4 className="text-xl font-semibold">Iluminação Incidente</h4>
          <span className="text-sm" style={{ color: status.color }}>{status.text}</span>
        </div>
      </div>
      {/* Barra horizontal de intensidade */}
      <div className="w-full flex flex-col gap-1">
        <div className="w-full h-4 bg-gray-300 rounded">
          <div
            className="h-4 rounded transition-all"
            style={{
              width: `${barFill}%`,
              background: status.color,
              minWidth: "2%",
            }}
          />
        </div>
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>Forte</span>
          <span>Fraca</span>
        </div>
      </div>
      {/* Valor lido */}
      <div className="text-sm text-muted-foreground mt-2">
        Valor do LDR: <span className="font-mono font-bold">{ldrValue !== null ? ldrValue : "--"}</span>
      </div>
    </div>
  );
};
