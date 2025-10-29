import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Power } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { turnLedOn, turnLedOff, getLedStatus } from "@/lib/api";

interface HistoryEntry {
  action: 'on' | 'off';
  timestamp: string;
}

export const LEDControl = () => {
  const [ledState, setLedState] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState<HistoryEntry[]>([]);

  // Buscar estado inicial do LED
  useEffect(() => {
    const fetchLedStatus = async () => {
      try {
        const status = await getLedStatus();
        setLedState(status.status === 'on');
      } catch (err) {
        console.error('Error fetching LED status:', err);
        toast({
          title: "Erro",
          description: "Falha ao buscar estado do LED",
          variant: "destructive",
        });
      }
    };

    fetchLedStatus();
  }, []);

  const toggleLED = async () => {
    setIsLoading(true);
    try {
      const newState = !ledState;
      if (newState) {
        await turnLedOn();
      } else {
        await turnLedOff();
      }
      
      setLedState(newState);
      setHistory(prev => [
        {
          action: newState ? 'on' : 'off',
          timestamp: new Date().toISOString()
        },
        ...prev.slice(0, 9) // Manter apenas os últimos 10 registros
      ]);
      toast({
        title: !ledState ? "LED Ligado" : "LED Desligado",
        description: `Estado alterado com sucesso às ${new Date().toLocaleTimeString()}`,
      });
    } catch (err) {
      toast({
        title: "Erro",
        description: "Falha ao controlar LED",
        variant: "destructive",
      });
      console.error('Error controlling LED:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Power className="h-5 w-5" />
          Controle do LED
        </CardTitle>
        <CardDescription>
          Controle do LED GPIO da Raspberry Pi
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground">Estado Atual</p>
            <p className="text-2xl font-bold">
              {ledState ? (
                <span className="text-success">Ligado</span>
              ) : (
                <span className="text-muted-foreground">Desligado</span>
              )}
            </p>
          </div>
          <div className={`h-16 w-16 rounded-full ${ledState ? 'bg-success animate-pulse shadow-lg shadow-success/50' : 'bg-muted'} transition-all duration-300`} />
        </div>
        <Button
          onClick={toggleLED}
          disabled={isLoading}
          className="w-full"
          variant={ledState ? "destructive" : "default"}
        >
          {isLoading ? "Processando..." : ledState ? "Desligar LED" : "Ligar LED"}
        </Button>
      </CardContent>
      {/* Histórico */}
      {history.length > 0 && (
        <CardContent className="border-t pt-4">
          <div className="text-sm font-medium mb-2">Histórico de Ações</div>
          <div className="space-y-2 max-h-[200px] overflow-y-auto">
            {history.map((entry, index) => (
              <div
                key={index}
                className="flex items-center justify-between text-sm"
              >
                <div className="flex items-center gap-2">
                  <div
                    className={`h-2 w-2 rounded-full ${
                      entry.action === 'on' ? 'bg-success' : 'bg-muted-foreground'
                    }`}
                  />
                  <span>{entry.action === 'on' ? 'Ligado' : 'Desligado'}</span>
                </div>
                <span className="text-muted-foreground">
                  {new Date(entry.timestamp).toLocaleTimeString()}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      )}
    </Card>
  );
};
