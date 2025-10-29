import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Thermometer, Droplets, GaugeCircle, Activity } from "lucide-react";
import { getCurrentSensorReading, type SensorReading } from "@/lib/api";

export const SensorMonitor = () => {
  const [sensorData, setSensorData] = useState<SensorReading | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchSensorData = async () => {
    try {
      const data = await getCurrentSensorReading();
      setSensorData(data);
      setError(null);
    } catch (err) {
      setError('Falha ao buscar dados do sensor');
      console.error('Error fetching sensor data:', err);
    }
  };

  useEffect(() => {
    fetchSensorData();
    const interval = setInterval(fetchSensorData, 5000);

    return () => clearInterval(interval);
  }, []);

  const sensors = [
    {
      icon: Thermometer,
      label: "Temperatura",
      value: sensorData ? `${sensorData.temperature.toFixed(1)}°C` : "Carregando...",
      color: "text-chart-1",
      bgColor: "bg-chart-1/10",
    },
    {
      icon: Droplets,
      label: "Umidade",
      value: sensorData ? `${sensorData.humidity.toFixed(1)}%` : "Carregando...",
      color: "text-chart-2",
      bgColor: "bg-chart-2/10",
    },
    {
      icon: GaugeCircle,
      label: "Pressão",
      value: sensorData ? `${sensorData.pressure.toFixed(1)} hPa` : "Carregando...",
      color: "text-chart-3",
      bgColor: "bg-chart-3/10",
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Monitoramento de Sensores
        </CardTitle>
        <CardDescription>
          Última atualização: {sensorData ? new Date(sensorData.timestamp).toLocaleTimeString() : "Carregando..."}
        </CardDescription>
      </CardHeader>
      <CardContent className="grid gap-4 md:grid-cols-3">
        {sensors.map((sensor) => (
          <div
            key={sensor.label}
            className={`rounded-lg p-4 ${sensor.bgColor} border border-border/50`}
          >
            <div className="flex items-center gap-3">
              <sensor.icon className={`h-8 w-8 ${sensor.color}`} />
              <div>
                <p className="text-sm text-muted-foreground">{sensor.label}</p>
                <p className={`text-2xl font-bold ${sensor.color}`}>
                  {sensor.value}
                </p>
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
};
