import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { TrendingUp } from "lucide-react";
import { getSensorHistory, type SensorReading } from "@/lib/api";

const formatChartData = (data: SensorReading[]) => {
  return data.map(reading => ({
    time: new Date(reading.timestamp).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
    temperatura: reading.temperature.toFixed(1),
    umidade: reading.humidity.toFixed(1),
    pressao: reading.pressure.toFixed(1),
  }));
};

export const HistoricalChart = () => {
  const [data, setData] = useState<ReturnType<typeof formatChartData>>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const history = await getSensorHistory(12); // Last 12 readings
        setData(formatChartData(history));
        setError(null);
      } catch (err) {
        setError('Falha ao carregar histórico');
        console.error('Error fetching history:', err);
      }
    };

    fetchHistory();
    const interval = setInterval(fetchHistory, 60000); // Update every minute
    return () => clearInterval(interval);
  }, []);

  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Histórico de Leituras
        </CardTitle>
        <CardDescription>
          {error ? error : 'Dados dos últimos 60 minutos (atualização a cada minuto)'}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis 
              dataKey="time" 
              stroke="hsl(var(--muted-foreground))"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="hsl(var(--muted-foreground))"
              style={{ fontSize: '12px' }}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px',
              }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="temperatura" 
              stroke="hsl(var(--chart-1))" 
              strokeWidth={2}
              name="Temperatura (°C)"
            />
            <Line 
              type="monotone" 
              dataKey="umidade" 
              stroke="hsl(var(--chart-2))" 
              strokeWidth={2}
              name="Umidade (%)"
            />
            <Line 
              type="monotone" 
              dataKey="pressao" 
              stroke="hsl(var(--chart-3))" 
              strokeWidth={2}
              name="Pressão (hPa)"
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};
