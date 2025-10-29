import { LEDControl } from "@/components/LEDControl";
import { SensorMonitor } from "@/components/SensorMonitor";
import { HistoricalChart } from "@/components/HistoricalChart";
import { ActionHistory } from "@/components/ActionHistory";
import { Cpu, Wifi } from "lucide-react";

const Index = () => {
  return (
    <div className="min-h-screen bg-background p-4">
      <div className="mx-auto max-w-md">
        <h1 className="text-3xl font-bold mb-8 text-center">
          Controle do LED - Raspberry Pi
        </h1>
        <LEDControl />
      </div>
    </div>
  );
};

export default Index;
