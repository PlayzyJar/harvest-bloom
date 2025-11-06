# GUIDE.md – Guia Completo Harvest Bloom

Guia detalhado para instalação, configuração, uso avançado e troubleshooting do sistema Harvest Bloom.

---

## 📑 Índice

1. [Instalação Física](#instalação-física)
2. [Instalação de Software](#instalação-de-software)
3. [Primeira Execução](#primeira-execução)
4. [Uso da Interface Física](#uso-da-interface-física)
5. [Uso da API REST](#uso-da-api-rest)
6. [Estrutura de Código](#estrutura-de-código)
7. [Integração de Novos Sensores](#integração-de-novos-sensores)
8. [Troubleshooting](#troubleshooting)
9. [Deploy e Segurança](#deploy-e-segurança)
10. [FAQ](#faq)

---

## 1. Instalação Física

### 1.1 Display SSD1306

Conecte o display OLED I2C aos pinos corretos da Raspberry Pi:

| Display | Raspberry Pi |
|---------|-------------|
| VCC | 3.3V (pino 1) |
| GND | GND (pino 6 ou 9) |
| SDA | GPIO2 (pino 3) |
| SCL | GPIO3 (pino 5) |

### 1.2 Sensor DHT11 (Temperatura/Umidade)

| DHT11 | Raspberry Pi |
|-------|-------------|
| VCC | 3.3V (pino 1) |
| GND | GND (pino 6) |
| DATA | GPIO4 (pino 7) |

*Nota*: Pode usar outro GPIO. Veja `backend/libs/sensors/dht11_simple.py` e adapte o pino.

### 1.3 Sensor HC-SR04 (Ultrassônico)

| HC-SR04 | Raspberry Pi |
|---------|-------------|
| VCC | 5V (pino 2) |
| GND | GND (pino 6) |
| TRIG | GPIO17 (pino 11) |
| ECHO | GPIO27 (pino 13) |

*Nota*: ECHO precisa de divisor de tensão 5V→3.3V se usar pino de 3.3V.

### 1.4 LED de Controle

| LED | Raspberry Pi |
|-----|-------------|
| Ânodo | GPIO18 (pino 12) |
| Cátodo | GND + Resistor 220Ω |

### 1.5 Botões/Teclado

- **USB keyboard**: Conecte em qualquer porta USB
- **Botões GPIO**: Use GPIO com pull-up interno configurável

Habilite I2C na Raspberry Pi:

```bash
sudo raspi-config
# Interface Options → I2C → Enable
# Reinicie
```

Verifique I2C:

```bash
sudo i2cdetect -y 1
# Deve mostrar endereço 0x3C para o display
```

---

## 2. Instalação de Software

### 2.1 Dependências do Sistema

```bash
sudo apt update
sudo apt upgrade
sudo apt install python3 python3-pip python3-venv i2c-tools libgpiod3 python3-lgpio git
```

### 2.2 Backend Python

```bash
git clone https://github.com/seu-usuario/harvest-bloom.git
cd harvest-bloom

# Crie venv
python3 -m venv venv
source venv/bin/activate

# Instale dependências
pip install --upgrade pip
pip install -r requirements.txt
```

**Verificar instalação:**

```bash
python -c "import board; import adafruit_ssd1306; print('✓ Dependências OK')"
```

### 2.3 Frontend Web (Opcional)

```bash
cd frontend_rasp

# Instale Node.js se não tiver
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

# Setup frontend
npm install
npm run build  # Para produção
# ou
npm run dev    # Para desenvolvimento
```

---

## 3. Primeira Execução

### 3.1 Inicie o Backend

```bash
cd backend
source ../venv/bin/activate
sudo python3 app.py
```

*Por que sudo?* Acesso a GPIO, I2C e Wi-Fi exigem permissões de root.

**Esperado:**

```
✓ Display inicializado
✓ Botões GPIO configurados
✓ Teclado virtual inicializado
SISTEMA INICIADO - Fase 1
```

### 3.2 Veja o Splash "Harvest Bloom"

Depois de 3 segundos, o menu principal aparece.

### 3.3 Conecte a Rede Wi-Fi

1. Pressione seta direita/esquerda para listar redes
2. Selecione uma com "SELECT"
3. Se conhecida, conecta automaticamente
4. Se nova, teclado virtual aparece para entrar a senha
5. Depois de conectar, vê o IP, RSSI, SSH, etc.

---

## 4. Uso da Interface Física

### 4.1 Navegação de Menu

| Botão | Ação |
|-------|------|
| **Seta Esquerda** | Move seleção para esquerda (teclado/menu) |
| **Seta Direita** | Move seleção para direita |
| **SELECT / Enter** | Confirma, conecta, entra em submenu |
| **MODE / ESC** | Volta, retorna ao menu anterior |

### 4.2 Estados do Menu

- **CHECK_WIFI**: Detecta conexão, escolhe estado
- **MAIN_CONNECTED**: Exibe IP, SSID, SSH, nível de sinal
  - Press MODE → Exibe URL de acesso web
  - Press SELECT → Lista de redes disponíveis
- **MAIN_DISCONNECTED**: Lista redes, permite conectar
- **WIFI_LIST**: Scroll e seleção de redes
- **PASSWORD_ENTRY**: Teclado para entrada de senha
- **CONNECTING**: Feedback durante conexão
- **SHOW_URL**: Exibe `http://<IP>:8080` em grande

### 4.3 Teclado Virtual

- Navegue com setas
- SELECT confirma caractere
- MODE alterna entre maiúsculas/minúsculas/números

---

## 5. Uso da API REST

### 5.1 Base URL

```
http://<IP_placa>:8080/api
```

### 5.2 Endpoints Implementados

#### Wi-Fi

```bash
# Status da conexão Wi-Fi
GET http://192.168.0.10:8080/api/wifi/status
# Retorna: { "ssid": "MeuWiFi", "ip": "192.168.0.10", "signal": "-50 dBm", ... }

# Escanear redes disponíveis
GET http://192.168.0.10:8080/api/wifi/scan
# Retorna: { "redes": ["rede1", "rede2", ...] }

# Conectar a uma rede
POST http://192.168.0.10:8080/api/wifi/connect
# Body: { "ssid": "MeuWiFi", "password": "senha123" }
```

#### Sensores

```bash
# Leitura DHT11 (Temperatura/Umidade)
GET http://192.168.0.10:8080/api/sensor/dht11
# Retorna: { "temperature": 25.5, "humidity": 60.2, "unit_temp": "°C", "unit_humid": "%" }

# Leitura HC-SR04 (Distância Ultrassônica)
GET http://192.168.0.10:8080/api/sensor/ultrasonic
# Retorna: { "distance_cm": 15.3 }
```

#### Atuadores

```bash
# Ligar LED
POST http://192.168.0.10:8080/api/led/on

# Desligar LED
POST http://192.168.0.10:8080/api/led/off

# Status do LED
GET http://192.168.0.10:8080/api/led/status
# Retorna: { "status": "on" | "off" }
```

#### Sistema

```bash
# Info da placa
GET http://192.168.0.10:8080/api/system/info
# Retorna: { "hostname": "raspberrypi", "ip": "192.168.0.10", "ssh_users": 1, ... }
```

### 5.3 Exemplos com cURL

```bash
# Verificar status Wi-Fi
curl http://192.168.0.10:8080/api/wifi/status | jq

# Ler sensor DHT11
curl http://192.168.0.10:8080/api/sensor/dht11 | jq '.data'

# Ligar LED
curl -X POST http://192.168.0.10:8080/api/led/on
```

### 5.4 Integração com Frontend

O frontend React/TypeScript acessa a API dinamicamente:

```typescript
// frontend_rasp/src/lib/api.ts
const API_BASE_URL = window.location.origin.replace(/:3000$/, ':8080') + '/api';

export async function getWiFiStatus() {
  const response = await fetch(`${API_BASE_URL}/wifi/status`);
  return response.json();
}
```

Assim, independente do IP da placa na rede, o frontend sempre encontra a API.

---

## 6. Estrutura de Código

### 6.1 Backend

```
backend/
├── app.py                          # Flask principal, todas as rotas
├── requirements.txt
├── libs/
│   ├── display/
│   │   ├── display_utils.py       # draw_info_screen(), draw_wifi_list()
│   │   └── virtual_keyboard_display.py
│   ├── input_gpio/
│   │   ├── buttons.py             # ButtonManager (esquerda/direita/select/mode)
│   │   └── virtual_keyboard.py    # VirtualKeyboard para senha/entrada
│   └── sensors/
│       ├── dht11_simple.py        # Classe DHT11 para leitura
│       └── __init__.py
└── utils/
    └── wifi_utils.py              # scan_wifi_networks(), connect_to_wifi()
```

### 6.2 Frontend

```
frontend_rasp/
├── src/
│   ├── lib/
│   │   ├── api.ts                 # Cliente API com descoberta dinâmica de IP
│   │   └── utils.ts
│   ├── components/
│   │   ├── WifiStatus.tsx
│   │   ├── Sensors.tsx
│   │   ├── LEDControl.tsx
│   │   └── ...
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   └── Settings.tsx
│   └── App.tsx
├── package.json
└── vite.config.ts
```

### 6.3 Fluxo de Execução

1. `app.py` inicia, cria display, botões, teclado
2. Entra em loop principal (`while True`)
3. Lê estado de Wi-Fi, atualiza display
4. Aguarda cliques de botões (callbacks)
5. Simultaneamente, Flask serve API em porta 8080
6. Frontend acessa API dinamicamente e renderiza

---

## 7. Integração de Novos Sensores

### 7.1 Adicionar um Novo Sensor

**Passo 1**: Crie driver em `backend/libs/sensors/seu_sensor.py`

```python
# libs/sensors/seu_sensor.py
import board
import analogio  # ou biblioteca específica

class SeuSensor:
    def __init__(self, pin=board.A0):
        self.sensor = analogio.AnalogIn(pin)
    
    def read(self):
        valor_raw = self.sensor.value
        valor_volts = (valor_raw / 65536) * 3.3
        return valor_volts
    
    def cleanup(self):
        self.sensor.deinit()
```

**Passo 2**: Importe e use no `app.py`

```python
from libs.sensors.seu_sensor import SeuSensor

sensor = SeuSensor()

@app.route('/api/sensor/seu_sensor', methods=['GET'])
def get_seu_sensor():
    try:
        valor = sensor.read()
        return jsonify({'success': True, 'data': {'valor': valor}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

**Passo 3**: Exiba no display

```python
# No loop principal de app.py, adicione:
valor_sensor = sensor.read()
draw.text((10, 50), f"Seu Sensor: {valor_sensor:.2f}", font=font, fill=255)
```

**Passo 4**: Adicione ao frontend (React)

```typescript
// src/components/SeuSensor.tsx
export function SeuSensor() {
  const [valor, setValor] = useState(0);
  
  useEffect(() => {
    fetch(`${API_BASE_URL}/sensor/seu_sensor`)
      .then(r => r.json())
      .then(data => setValor(data.data.valor));
  }, []);
  
  return <div>Seu Sensor: {valor.toFixed(2)}</div>;
}
```

---

## 8. Troubleshooting

### 8.1 Display Não Acende

**Verificar I2C:**

```bash
sudo i2cdetect -y 1
```

Procure por `0x3C` na saída. Se não aparecer:
- Verifique conexões SDA/SCL e VCC/GND
- Verifique se I2C foi habilitado em raspi-config
- Tente outro display SSD1306 para descartar hardware

### 8.2 Erro "libgpiod" ou "Timed out waiting for PulseIn"

**Causa**: Versão de libgpiod incompatível com driver do Blinka.

**Solução**:

```bash
sudo apt install python3-lgpio libgpiod3
pip install lgpio --force-reinstall
```

Se ainda der erro, você pode estar em Debian Trixie/Bookworm com libgpiod3 só, e driver do DHT precisa de libgpiod2. Neste caso, considere usar um SO mais antigo (Bullseye) ou esperar por atualização do Adafruit.

### 8.3 API Não Responde (Conexão Recusada)

**Verificar:**

```bash
# Porta 8080 aberta?
sudo netstat -tuln | grep 8080

# Processo rodando?
ps aux | grep python | grep app.py

# Firewall?
sudo ufw status
```

**Reiniciar:**

```bash
# Mate processos Python antigos
sudo killall python3

# Rode novamente
sudo python3 backend/app.py
```

### 8.4 Botões/Teclado Não Responsivo

**Para USB Keyboard:**

```bash
# Verifique se detectado
ls /dev/input/event*

# Teste leitura
sudo cat /dev/input/event0
# Pressione tecla, deve exibir caracteres
```

**Para GPIO:**

```bash
# Verifique GPIO
gpio readall

# Teste com script simples
python3 -c "from gpiozero import Button; b = Button(2); print('Pronto')"
```

### 8.5 Sensor DHT11 Não Lê

**Verificar Pino:**

No seu `backend/libs/sensors/dht11_simple.py`, confirme:

```python
sensor = DHT11(gpio=board.D4)  # GPIO4 é padrão
# Se usar outro, mude para: board.D17, board.D18, etc.
```

**Teste Simples:**

```bash
cd backend
python3 -c "
from libs.sensors.dht11_simple import DHT11
s = DHT11()
temp, humid = s.read()
print(f'Temp: {temp}°C, Umidade: {humid}%')
"
```

Se retornar `None, None`, sensor não está respondendo. Verifique conexões.

### 8.6 Erro "ModuleNotFoundError"

**Sempre rode com a venv ativa:**

```bash
source venv/bin/activate
sudo python3 app.py
```

Ou rode sem ativar:

```bash
sudo venv/bin/python3 app.py
```

---

## 9. Deploy e Segurança

### 9.1 Rodar como Serviço Systemd (Produção)

Crie `/etc/systemd/system/harvest-bloom.service`:

```ini
[Unit]
Description=Harvest Bloom WiFi Manager
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/harvest-bloom
Environment="PATH=/home/pi/harvest-bloom/venv/bin"
ExecStart=/home/pi/harvest-bloom/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Ative:

```bash
sudo systemctl daemon-reload
sudo systemctl enable harvest-bloom
sudo systemctl start harvest-bloom
sudo systemctl status harvest-bloom
```

### 9.2 SSL/HTTPS (Recomendado para Produção)

Use Nginx com self-signed cert ou Let's Encrypt:

```bash
sudo apt install nginx-full certbot python3-certbot-nginx

# Self-signed (teste):
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/harvest.key -out /etc/ssl/certs/harvest.crt

# Configure nginx para proxy reverso com HTTPS
```

### 9.3 Firewall

```bash
sudo ufw enable
sudo ufw default deny incoming
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 8080/tcp    # Harvest Bloom
sudo ufw allow 80/tcp      # HTTP (opcional)
```

---

## 10. FAQ

### P: Posso usar outro display que não SSD1306?

R: Sim, com adaptação. O projeto usa `adafruit-circuitpython-ssd1306`. Se usar outro, importe a biblioteca correspondente e adapte `display_utils.py`.

### P: Qual versão de Raspberry Pi?

R: Testado em Pi 3, 4 e 5. Pi Zero funcionará, mas mais lentamente. Pi 1/2 podem ter problemas com Python 3.13.

### P: Preciso de internet?

R: NÃO. O sistema funciona 100% em rede local. Não faz requisições externas (a menos que você adicione integração com cloud).

### P: Posso expandir a interface web?

R: SIM! Frontend é React/TypeScript moderno. Adicione componentes, pages e chame novos endpoints da API conforme necessário.

### P: Como faço monitoramento contínuo (guardar dados)?

R: Adicione um banco de dados (SQLite, PostgreSQL) e crie endpoints para salvar leituras periódicas de sensores. O GUIDE futuro cobrirá isso.

### P: Suporta múltiplas placs?

R: Não, mas poderia ser expandido com broker MQTT ou agregador central. Fora do escopo deste projeto.

---

**Fim do GUIDE.md**

Para dúvidas, revise o código, comente issues no GitHub ou abra um PR!
