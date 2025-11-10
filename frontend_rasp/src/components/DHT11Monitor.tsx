import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Thermometer, Droplets, AlertCircle } from "lucide-react";
import { setHumidity } from "@/lib/ambientStore";

type DHT11State = {
  temperature: number | null;
  humidity: number | null;
  success: boolean;
  unit_temp?: string;
  unit_humid?: string;
  error?: string;
};

const API_BASE_URL = window.location.origin.replace(/:8080$/, ':5000') + '/api';

export const DHT11Monitor = () => {
  const [sensor, setSensor] = useState<DHT11State | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  useEffect(() => {
    const fetchSensor = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/sensor/dht11`, { 
          cache: "no-store",
          headers: {
            'Accept': 'application/json',
          }
        });
        
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        
        const data = await res.json();
        setSensor(data);
        setLastUpdate(new Date());
        setHumidity(data.humidity);
      } catch (error) {
        console.error("Erro ao buscar dados do DHT11:", error);
        setSensor({ 
          success: false, 
          temperature: null, 
          humidity: null, 
          error: "Falha na conexão com o sensor" 
        });
      } finally {
        setLoading(false);
      }
    };

    fetchSensor();
    const interval = setInterval(fetchSensor, 3000);
    return () => clearInterval(interval);
  }, []);

  const getTemperatureColor = (temp: number | null) => {
    if (temp === null) return "text-muted-foreground";
    if (temp < 15) return "text-blue-500";
    if (temp < 25) return "text-green-500";
    if (temp < 30) return "text-yellow-500";
    return "text-red-500";
  };

  const getHumidityColor = (humidity: number | null) => {
    if (humidity === null) return "text-muted-foreground";
    if (humidity < 30) return "text-orange-500";
    if (humidity < 60) return "text-green-500";
    return "text-blue-500";
  };

  return (
    <Card className="bg-muted p-6 mt-6">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-lg font-semibold">Sensor DHT11</h4>
        {lastUpdate && (
          <span className="text-xs text-muted-foreground">
            Atualizado: {lastUpdate.toLocaleTimeString()}
          </span>
        )}
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      ) : sensor?.success ? (
        <div className="grid grid-cols-2 gap-4">
          <div className="flex flex-col items-center p-4 bg-background rounded-lg">
            <Thermometer className={`h-8 w-8 mb-2 ${getTemperatureColor(sensor.temperature)}`} />
            <span className="text-sm text-muted-foreground mb-1">Temperatura</span>
            <span className={`text-3xl font-mono font-bold ${getTemperatureColor(sensor.temperature)}`}>
              {sensor.temperature}
            </span>
            <span className="text-sm text-muted-foreground mt-1">
              {sensor.unit_temp || "°C"}
            </span>
          </div>

          <div className="flex flex-col items-center p-4 bg-background rounded-lg">
            <Droplets className={`h-8 w-8 mb-2 ${getHumidityColor(sensor.humidity)}`} />
            <span className="text-sm text-muted-foreground mb-1">Umidade</span>
            <span className={`text-3xl font-mono font-bold ${getHumidityColor(sensor.humidity)}`}>
              {sensor.humidity}
            </span>
            <span className="text-sm text-muted-foreground mt-1">
              {sensor.unit_humid || "%"}
            </span>
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-center gap-2 py-8 text-red-600">
          <AlertCircle className="h-5 w-5" />
          <span>{sensor?.error || "Erro ao ler DHT11"}</span>
        </div>
      )}
    </Card>
  );
};
