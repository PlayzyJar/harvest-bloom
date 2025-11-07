import { useEffect, useState } from "react";

type DHT11State = {
  temperature: number | null;
  humidity: number | null;
  success: boolean;
  unit_temp?: string;
  unit_humid?: string;
  error?: string;
};

export const DHT11Monitor = () => {
  const [sensor, setSensor] = useState<DHT11State | null>(null);
  const [loading, setLoading] = useState(false);

  // Faz fetch a cada 3 segundos
  useEffect(() => {
    const fetchSensor = async () => {
      setLoading(true);
      try {
        const res = await fetch("/api/sensor/dht11", { cache: "no-store" });
        const data = await res.json();
        setSensor(data);
      } catch {
        setSensor({ success: false, temperature: null, humidity: null, error: "Falha ao buscar dados" });
      }
      setLoading(false);
    };
    fetchSensor();
    const interval = setInterval(fetchSensor, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="card bg-muted p-4 flex flex-col items-center gap-3">
      <h4 className="text-lg font-semibold">Monitor DHT11</h4>
      {loading ? (
        <span className="text-muted-foreground">Carregando...</span>
      ) : sensor?.success ? (
        <>
          <div className="flex gap-5">
            <div>
              <span className="block text-sm">Temperatura</span>
              <span className="text-2xl font-mono font-bold">{sensor.temperature} {sensor.unit_temp || "°C"}</span>
            </div>
            <div>
              <span className="block text-sm">Umidade</span>
              <span className="text-2xl font-mono font-bold">{sensor.humidity} {sensor.unit_humid || "%"}</span>
            </div>
          </div>
        </>
      ) : (
        <span className="text-red-600">{sensor?.error || "Erro ao ler DHT11"}</span>
      )}
    </div>
  );
};
