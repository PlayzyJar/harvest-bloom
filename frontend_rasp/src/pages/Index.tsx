import { LEDControl } from "@/components/LEDControl";
import { UltrasonicMonitor } from "@/components/UltrasonicMonitor";
import { ActionHistory } from "@/components/ActionHistory";
import { Cpu, Wifi } from "lucide-react";
import { SensorMonitor } from "@/components/SensorMonitor";

const Index = () => {
  return (
    <div className="min-h-screen bg-background p-4">
      <div className="mx-auto max-w-6xl">
        <h1 className="text-3xl font-bold mb-8 text-center">Controle do LED - Raspberry Pi</h1>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          <div className="md:col-span-1">
            <LEDControl />
            <div className="mt-6">
              <ActionHistory />
	      <SensorMonitor />
            </div>
          </div>
          <div className="md:col-span-2">
            <UltrasonicMonitor />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
