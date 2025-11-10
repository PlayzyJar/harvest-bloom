// PumpControl.tsx
import { useEffect, useState } from "react";
import { subscribeHumidity } from "@/lib/ambientStore";
import { Card, CardHeader, CardDescription, CardContent } from "@/components/ui/card"
export const PumpControl = () => {
  const [ambientHumidity, setAmbientHumidity] = useState<number | null>(null);

  useEffect(() => {
    const unsubscribe = subscribeHumidity(setAmbientHumidity);
    return unsubscribe;
  }, []);

  // Lógica visual: Ligada se < 35, Desligada se >= 35 ou null
  const pumpState = ambientHumidity !== null ? ambientHumidity < 40 : false;

  return (
    <Card>
      <CardHeader>
        {/* ... seu código ... */}
        <CardDescription>
          Relé da bomba de irrigação via GPIO6<br />
          <span className="font-mono text-xs">
            Umidade Atual: {ambientHumidity !== null ? `${ambientHumidity}%` : "N/A"}
          </span>
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

