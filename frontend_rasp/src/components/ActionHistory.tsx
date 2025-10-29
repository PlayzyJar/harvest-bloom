import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { History } from "lucide-react";

interface Action {
  id: number;
  timestamp: string;
  action: string;
  device: string;
  status: "success" | "error";
}

// Simulated action history
const mockActions: Action[] = [
  { id: 1, timestamp: new Date().toLocaleString('pt-BR'), action: "Ligar", device: "LED", status: "success" },
  { id: 2, timestamp: new Date(Date.now() - 120000).toLocaleString('pt-BR'), action: "Desligar", device: "LED", status: "success" },
  { id: 3, timestamp: new Date(Date.now() - 300000).toLocaleString('pt-BR'), action: "Ligar", device: "LED", status: "success" },
  { id: 4, timestamp: new Date(Date.now() - 600000).toLocaleString('pt-BR'), action: "Leitura", device: "Sensor DHT11", status: "success" },
  { id: 5, timestamp: new Date(Date.now() - 900000).toLocaleString('pt-BR'), action: "Desligar", device: "LED", status: "success" },
];

export const ActionHistory = () => {
  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <History className="h-5 w-5" />
          Histórico de Ações
        </CardTitle>
        <CardDescription>
          Registro das últimas operações realizadas no sistema
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Data/Hora</TableHead>
                <TableHead>Dispositivo</TableHead>
                <TableHead>Ação</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {mockActions.map((action) => (
                <TableRow key={action.id}>
                  <TableCell className="font-mono text-sm">
                    {action.timestamp}
                  </TableCell>
                  <TableCell>{action.device}</TableCell>
                  <TableCell>{action.action}</TableCell>
                  <TableCell>
                    <Badge 
                      variant={action.status === "success" ? "default" : "destructive"}
                      className={action.status === "success" ? "bg-success" : ""}
                    >
                      {action.status === "success" ? "Sucesso" : "Erro"}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
};
