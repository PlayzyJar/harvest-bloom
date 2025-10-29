import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle } from "lucide-react";

// This component is intentionally simplified since temperature/humidity/pressure
// monitoring was removed from the front-end. The UltrasonicMonitor is used instead.
export const SensorMonitor = () => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5" />
          Monitor de Sensores (desativado)
        </CardTitle>
        <CardDescription>
          As leituras de temperatura/umidade/pressão foram removidas. Use o monitor ultrassônico.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">Componente mantido apenas por compatibilidade; não faz chamadas.</p>
      </CardContent>
    </Card>
  );
};
