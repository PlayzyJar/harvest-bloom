import { LEDControl } from "@/components/LEDControl";
import { UltrasonicMonitor } from "@/components/UltrasonicMonitor";
import { ActionHistory } from "@/components/ActionHistory";
import { SensorMonitor } from "@/components/SensorMonitor";
import { DHT11Monitor } from "@/components/DHT11Monitor";
import { Activity, Cpu } from "lucide-react";
import { PumpControl } from  "@/components/PumpControl";

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted/30 p-4 md:p-6">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="flex items-center justify-center gap-3 mb-2">
            <Cpu className="h-8 w-8 text-primary" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
              Painel de Controle
            </h1>
          </div>
          <p className="text-muted-foreground">
            Monitoramento e controle em tempo real - Raspberry Pi
          </p>
        </div>

        {/* Layout Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Coluna Esquerda - Controles */}
          <div className="lg:col-span-1 space-y-6">
            {/* Controle do LED */}
            <LEDControl />
            {/* Sensores Ambientais */}
            <div className="space-y-6">
              <DHT11Monitor />
              <SensorMonitor />
              <PumpControl />
            </div>
          </div>

          {/* Coluna Central/Direita */}
          <div className="lg:col-span-2 space-y-6">
            {/* Monitor Ultrassônico */}
            <UltrasonicMonitor />
            
            {/* Histórico de Ações */}
            <div className="bg-card rounded-lg border shadow-sm">
              <div className="p-4 border-b">
                <div className="flex items-center gap-2">
                  <Activity className="h-5 w-5 text-primary" />
                  <h2 className="text-lg font-semibold">Histórico de Eventos</h2>
                </div>
              </div>
              <div className="p-4">
                <ActionHistory />
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-muted-foreground">
          <p>Sistema de automação IoT • Atualização em tempo real</p>
        </div>
      </div>
    </div>
  );
};

export default Index;
