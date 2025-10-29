import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Archive } from "lucide-react";

// HistoricalChart is kept as a placeholder. The project now focuses on the
// Ultrasonic (HC-SR04) sensor; historical charts for other sensors were removed.
export const HistoricalChart = () => {
  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Archive className="h-5 w-5" />
          Histórico (desativado)
        </CardTitle>
        <CardDescription>
          Histórico de temperatura/umidade/pressão desativado. Veja o monitor ultrassônico.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">Componente mantido por compatibilidade visual apenas.</p>
      </CardContent>
    </Card>
  );
};
