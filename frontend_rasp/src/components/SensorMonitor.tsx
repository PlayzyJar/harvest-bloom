import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Lightbulb, AlertCircle } from "lucide-react";

const API_BASE_URL = window.location.origin.replace(/:8080$/, ':5000') + '/api';

interface LDRStatus {
  color: string;
  text: string;
  intensity: "forte" | "media" | "fraca" | "escura";
}

function getLDRStatus(valor: number): LDRStatus {
  if (valor < 50000) {
    return { 
      color: "#FFD700", 
      text: "Iluminação Forte", 
      intensity: "forte" 
    };
  }
  if (valor < 90000) {
    return { 
      color: "#FFA500", 
      text: "Iluminação Média", 
      intensity: "media" 
    };
  }
  if (valor < 120000) {
    return { 
      color: "#B197FC", 
      text: "Iluminação Fraca", 
      intensity: "fraca" 
    };
  }
  return { 
    color: "#808080", 
    text: "Pouca Luz", 
    intensity: "escura" 
  };
}

export const SensorMonitor = () => {
  const [ldrValue, setLdrValue] = useState<number | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLDR = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/ldr`, {
          headers: {
            'Accept': 'application/json',
          }
        });
        
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        
        const data = await res.json();
        
        if (data.ldr !== null && data.ldr !== undefined) {
          setLdrValue(data.ldr);
          setLastUpdate(new Date());
          setError(null);
        } else if (data.status === 'aguardando leitura') {
          setError("Aguardando primeira leitura...");
        }
      } catch (err) {
        console.error("Erro ao buscar dados do LDR:", err);
        setError("Falha na conexão com o sensor");
      }
    };

    fetchLDR();
    const interval = setInterval(fetchLDR, 1000);
    return () => clearInterval(interval);
  }, []);

  const status = ldrValue !== null 
    ? getLDRStatus(ldrValue) 
    : { color: "#808080", text: "Sem leitura", intensity: "escura" as const };

  // Calcula a porcentagem da barra (invertida: menos luz = mais à direita)
  const barFill = ldrValue !== null 
    ? Math.min(Math.max((ldrValue / 150000) * 100, 1), 100) 
    : 0;

  return (
    <Card className="bg-muted p-6 mt-6">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-lg font-semibold">Sensor LDR</h4>
        {lastUpdate && (
          <span className="text-xs text-muted-foreground">
            {lastUpdate.toLocaleTimeString()}
          </span>
        )}
      </div>

      {error ? (
        <div className="flex items-center justify-center gap-2 py-4 text-yellow-600">
          <AlertCircle className="h-5 w-5" />
          <span className="text-sm">{error}</span>
        </div>
      ) : (
        <>
          <div className="flex items-center gap-4 mb-4">
            <div className="relative">
              <Lightbulb 
                className="h-12 w-12 transition-all duration-300" 
                style={{ color: status.color }}
                fill={status.intensity === "forte" ? status.color : "none"}
              />
              {status.intensity === "forte" && (
                <div 
                  className="absolute inset-0 rounded-full blur-xl opacity-50"
                  style={{ backgroundColor: status.color }}
                />
              )}
            </div>
            
            <div className="flex-1">
              <h5 className="text-xl font-semibold">Iluminação Ambiente</h5>
              <span 
                className="text-sm font-medium"
                style={{ color: status.color }}
              >
                {status.text}
              </span>
            </div>
          </div>

          {/* Barra de intensidade */}
          <div className="space-y-2">
            <div className="relative w-full h-6 bg-gray-300 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500 ease-out"
                style={{
                  width: `${barFill}%`,
                  background: `linear-gradient(90deg, ${status.color}, ${status.color}dd)`,
                  boxShadow: `0 0 10px ${status.color}88`
                }}
              />
            </div>
            
            <div className="flex justify-between text-xs text-muted-foreground px-1">
              <span className="font-medium">🔆 Forte</span>
              <span className="font-medium">🌙 Escuro</span>
            </div>
          </div>

          {/* Valor numérico */}
          <div className="mt-4 p-3 bg-background rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Valor do sensor:</span>
              <span className="text-xl font-mono font-bold" style={{ color: status.color }}>
                {ldrValue !== null ? ldrValue.toLocaleString() : "--"}
              </span>
            </div>
          </div>
        </>
      )}
    </Card>
  );
};
