import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RefreshCcw } from "lucide-react";
import { toast } from "@/hooks/use-toast";

// Funções da API REST:
const getPumpStatus = async () => {
  const res = await fetch('/api/pump/status');
  return res.json();
};
const turnPumpOn = async () => fetch('/api/pump/on', {method: 'POST'});
const turnPumpOff = async () => fetch('/api/pump/off', {method: 'POST'});

export const PumpControl = () => {
  const [pumpState, setPumpState] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    getPumpStatus().then(status => setPumpState(status.status === 'on'));
  }, []);

  const togglePump = async () => {
    setIsLoading(true);
    try {
      if (!pumpState) await turnPumpOn();
      else await turnPumpOff();
      setPumpState(!pumpState);
      toast({
        title: pumpState ? "Bomba desligada" : "Bomba ligada",
        description: `Estado alterado com sucesso às ${new Date().toLocaleTimeString()}`
      });
    } catch (err) {
      toast({
        title: "Erro",
        description: "Falha ao controlar bomba",
        variant: "destructive",
      });
    }
    setIsLoading(false);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <RefreshCcw className="h-5 w-5" />
          Controle da Bomba
        </CardTitle>
        <CardDescription>
          Relé da bomba de irrigação via GPIO6
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground">Estado Atual</p>
            <p className="text-2xl font-bold">
              {pumpState ? (
                <span className="text-success">Ligada</span>
              ) : (
                <span className="text-muted-foreground">Desligada</span>
              )}
            </p>
          </div>
          <div className={`h-16 w-16 rounded-full ${pumpState ? 'bg-success animate-pulse shadow-lg shadow-success/50' : 'bg-muted'} transition-all duration-300`} />
        </div>
      </CardContent>
    </Card>
  );
};

