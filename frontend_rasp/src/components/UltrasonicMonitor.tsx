import { useEffect, useState, useRef } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Ruler, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";
import { getUltrasonicCurrent, UltrasonicReading } from "@/lib/api";

type Reading = {
  timestamp: number;
  distance: number;
};

export const UltrasonicMonitor = () => {
  const [readings, setReadings] = useState<Reading[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [last, setLast] = useState<number | null>(null);
  const mounted = useRef(true);

  const STORAGE_KEY = 'ultrasonic_readings_v1';

  useEffect(() => {
    mounted.current = true;

    // load persisted readings
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed: Reading[] = JSON.parse(raw);
        if (Array.isArray(parsed) && parsed.length) {
          setReadings(parsed.slice(-60));
          setLast(parsed[parsed.length - 1].distance);
        }
      }
    } catch (err) {
      console.warn('Failed to parse stored ultrasonic readings', err);
    }

    const addReading = (distance: number) => {
      setLast(distance);
      setReadings(prev => {
        const next = [...prev, { timestamp: Date.now(), distance }];
        // keep only last 60 entries
        const sliced = next.length > 60 ? next.slice(next.length - 60) : next;
        try { localStorage.setItem(STORAGE_KEY, JSON.stringify(sliced)); } catch {};
        return sliced;
      });
    };

    const fetchOnce = async () => {
      try {
        const res: UltrasonicReading = await getUltrasonicCurrent();
        if (!mounted.current) return;
        addReading(Number(res.distance_cm));
        setError(null);
      } catch (err) {
        console.error('Ultrasonic fetch error', err);
        if (!mounted.current) return;
        setError('Falha ao obter distância');
      }
    };

    // initial fetch
    fetchOnce();
    // poll every 1.5s
    const interval = setInterval(fetchOnce, 1500);

    return () => {
      mounted.current = false;
      clearInterval(interval);
    };
  }, []);

  const exportCSV = () => {
    if (!readings.length) return;
    const header = ['timestamp_iso', 'time_local', 'distance_cm'];
    const rows = readings.map(r => {
      const iso = new Date(r.timestamp).toISOString();
      const local = new Date(r.timestamp).toLocaleString('pt-BR');
      return [iso, local, r.distance.toFixed(3)];
    });
    const csv = [header, ...rows].map(r => r.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const now = new Date().toISOString().replace(/[:.]/g, '-');
    a.download = `ultrasonic_history_${now}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const clearHistory = () => {
    setReadings([]);
    setLast(null);
    try { localStorage.removeItem(STORAGE_KEY); } catch {}
  };

  const chartData = readings.map(r => ({
    time: new Date(r.timestamp).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    distance: Number(r.distance.toFixed(2)),
  }));

  const min = readings.length ? Math.min(...readings.map(r => r.distance)) : 0;
  const max = readings.length ? Math.max(...readings.map(r => r.distance)) : 0;
  const avg = readings.length ? readings.reduce((s, r) => s + r.distance, 0) / readings.length : 0;

  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Ruler className="h-5 w-5" />
          Monitor Ultrassônico
        </CardTitle>
        <CardDescription>
          {error ? error : 'Leituras em tempo real (últimos ~' + readings.length + ' valores)'}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex justify-end gap-2 mb-4">
          <Button variant="outline" size="sm" onClick={exportCSV} disabled={!readings.length}>Exportar CSV</Button>
          <Button variant="ghost" size="sm" onClick={clearHistory} disabled={!readings.length}>Limpar</Button>
        </div>

        <div className="mb-4 grid gap-4 md:grid-cols-3">
          <div className="rounded-lg p-4 bg-chart-1/10 border border-border/50">
            <div className="flex items-center gap-3">
              <Activity className="h-8 w-8 text-chart-1" />
              <div>
                <p className="text-sm text-muted-foreground">Distância</p>
                <p className="text-2xl font-bold text-chart-1">{last !== null ? `${last.toFixed(1)} cm` : '—'}</p>
              </div>
            </div>
          </div>
          <div className="rounded-lg p-4 bg-chart-2/10 border border-border/50">
            <p className="text-sm text-muted-foreground">Mín</p>
            <p className="text-xl font-semibold text-chart-2">{readings.length ? `${min.toFixed(1)} cm` : '—'}</p>
          </div>
          <div className="rounded-lg p-4 bg-chart-3/10 border border-border/50">
            <p className="text-sm text-muted-foreground">Máx / Média</p>
            <p className="text-xl font-semibold text-chart-3">{readings.length ? `${max.toFixed(1)} cm / ${avg.toFixed(1)} cm` : '—'}</p>
          </div>
        </div>

        <div style={{ width: '100%', height: 280 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="time" stroke="hsl(var(--muted-foreground))" />
              <YAxis stroke="hsl(var(--muted-foreground))" />
              <Tooltip
                contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: 8 }}
              />
              <Line type="monotone" dataKey="distance" stroke="hsl(var(--chart-1))" strokeWidth={2} name="Distância (cm)" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
};

export default UltrasonicMonitor;
