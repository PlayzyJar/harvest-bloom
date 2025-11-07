// Configuração centralizada da API
// Detecta automaticamente a URL baseada na origem da página
const API_BASE_URL = window.location.origin.replace(/:8080$/, ':5000') + '/api';

// Tipos de resposta da API
export interface LDRResponse {
  ldr: number | null;
  status?: string;
}

export interface DHT11Response {
  success: boolean;
  temperature: number | null;
  humidity: number | null;
  unit_temp?: string;
  unit_humid?: string;
  error?: string;
}

export interface LEDStatus {
  status: 'on' | 'off';
}

export interface UltrasonicReading {
  distance_cm: number;
}

// Funções auxiliares para fazer requisições
export const api = {
  // LDR
  getLDR: async (): Promise<LDRResponse> => {
    const response = await fetch(`${API_BASE_URL}/ldr`);
    if (!response.ok) throw new Error("Erro ao buscar dados do LDR");
    return response.json();
  },

  // DHT11
  getDHT11: async (): Promise<DHT11Response> => {
    const response = await fetch(`${API_BASE_URL}/sensor/dht11`);
    if (!response.ok) throw new Error("Erro ao buscar dados do DHT11");
    return response.json();
  },

  // LED
  turnLedOn: async (): Promise<LEDStatus> => {
    const response = await fetch(`${API_BASE_URL}/led/on`, {
      method: "POST",
    });
    if (!response.ok) throw new Error("Erro ao ligar LED");
    return response.json();
  },

  turnLedOff: async (): Promise<LEDStatus> => {
    const response = await fetch(`${API_BASE_URL}/led/off`, {
      method: "POST",
    });
    if (!response.ok) throw new Error("Erro ao desligar LED");
    return response.json();
  },

  getLedStatus: async (): Promise<LEDStatus> => {
    const response = await fetch(`${API_BASE_URL}/led/status`);
    if (!response.ok) throw new Error("Erro ao buscar status do LED");
    return response.json();
  },

  // Ultrassônico (HC-SR04)
  getUltrasonicCurrent: async (): Promise<UltrasonicReading> => {
    const response = await fetch(`${API_BASE_URL}/ultrasonic`);
    if (!response.ok) throw new Error("Erro ao buscar distância");
    return response.json();
  },
};

// Exporta também as funções individuais para compatibilidade
export const turnLedOn = api.turnLedOn;
export const turnLedOff = api.turnLedOff;
export const getLedStatus = api.getLedStatus;
export const getUltrasonicCurrent = api.getUltrasonicCurrent;
