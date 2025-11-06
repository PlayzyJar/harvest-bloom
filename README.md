# Harvest Bloom – Plataforma de Monitoramento e Automação com Raspberry Pi

Sistema completo e modular para monitoramento, controle e automação de ambientes inteligentes (miniestufas, salas, ambientes corporativos) via Raspberry Pi. Integra interface física (display OLED + botões), web dashboard e API REST para gerenciamento de conectividade Wi-Fi, sensores (temperatura, umidade, distância) e atuadores (LED, relés) em tempo real.

## 🎯 Funcionalidades Principais

- **Gerenciamento Wi-Fi Inteligente**: Multirede, configuração de senha por interface física/web, monitoramento de sinal RSSI
- **Display OLED SSD1306 Interativo**: Menu de navegação com status da rede, sensores, atuadores e URL de acesso web
- **Monitoramento em Tempo Real**: Hostname, IP atual, SSID conectado, nível de sinal, estado SSH e número de usuários conectados
- **Controle de Atuadores**: LED ON/OFF, relés, automações customizáveis
- **Sensores Integrados**: DHT11/22 (temperatura/umidade), HC-SR04 (ultrassônico/distância)
- **API REST Completa**: Endpoints JSON para integração com dashboards e sistemas externos
- **Frontend Web Moderno**: Dashboard React/TypeScript para visualização e controle remoto
- **Arquitetura Modular**: Fácil expansão para novos sensores, lógicas de automação e integrações

## 🛠 Stack Tecnológico

| Componente | Tecnologia |
|-----------|-----------|
| **Hardware** | Raspberry Pi 3/4/5 |
| **Sistema Operacional** | Raspberry Pi OS / Debian Bookworm |
| **Linguagem Backend** | Python 3.13+ |
| **API** | Flask + Flask-CORS |
| **Drivers Hardware** | Adafruit Blinka, CircuitPython |
| **Interface Gráfica** | Pillow (PIL), SSD1306 Display Driver |
| **Frontend Web** | React 18+, TypeScript, Axios |
| **Gerenciamento Wi-Fi** | NetworkManager / nmcli |
| **GPIO / Sensores** | gpiozero, lgpio, adafruit-dht |

## 📋 Pré-requisitos

### Hardware
- Raspberry Pi 3, 4 ou 5 com Wi-Fi integrado (ou adaptador USB)
- Display OLED SSD1306 (128x64 pixels, interface I2C)
- Sensor DHT11/22 (temperatura/umidade) — *opcional*
- Sensor HC-SR04 (ultrassônico) — *opcional*
- LED com resistor (GPIO) — *opcional*
- Teclado USB ou interface de botões físicos (GPIO)

### Sistema
```bash
sudo apt update && sudo apt install python3 python3-pip i2c-tools libgpiod3 python3-lgpio
```

### Dependências Python
```bash
pip install -r requirements.txt
```

### Frontend
```bash
Node.js 16+ e npm 7+
```

## ⚡ Instalação Rápida

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/harvest-bloom.git
   cd harvest-bloom
   ```

2. **Configure o backend:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Inicie o backend:**
   ```bash
   cd backend
   python3 app.py
   ```

4. **Configure o frontend (opcional, em outro terminal):**
   ```bash
   cd frontend_rasp
   npm install
   npm run dev
   ```

5. **Acesse a placa:**
   - **Físico**: Use botões/teclado no display OLED para navegar
   - **Web**: Abra `http://<IP_da_placa>:8080` no navegador

## 📁 Estrutura do Projeto

```
harvest-bloom/
├── backend/
│   ├── app.py                      # API Flask principal
│   ├── utils/
│   │   └── wifi_utils.py          # Gerenciamento de Wi-Fi (nmcli)
│   ├── libs/
│   │   ├── display/               # Drivers do display SSD1306
│   │   │   ├── display_utils.py
│   │   │   └── virtual_keyboard_display.py
│   │   ├── input_gpio/            # Gerenciamento de botões/teclado
│   │   │   ├── buttons.py
│   │   │   └── virtual_keyboard.py
│   │   └── sensors/               # Drivers de sensores
│   │       ├── dht11_simple.py    # DHT11/22 temperatura/umidade
│   │       └── __init__.py
│   └── requirements.txt
├── frontend_rasp/
│   ├── src/
│   │   ├── lib/
│   │   │   ├── api.ts            # Cliente API (dinâmico por IP)
│   │   │   └── utils.ts
│   │   ├── components/            # Componentes React
│   │   └── pages/                 # Páginas do dashboard
│   ├── package.json
│   └── vite.config.ts
├── tests/
│   ├── test_dht11.py
│   ├── test_display.py
│   └── test_wifi.py
├── README.md                       # Este arquivo
├── GUIDE.md                        # Guia detalhado de instalação e uso
├── requirements.txt                # Dependências Python
└── LICENSE                         # MIT License
```

## 🚀 Uso Básico

### Via Interface Física (Display + Botões)

1. Ligue a Raspberry Pi
2. Veja o splash "Harvest Bloom" por 3 segundos
3. Navegue pelo menu usando:
   - **Setas Esquerda/Direita**: Scroll em listas
   - **SELECT**: Confirmar, conectar, entrar
   - **MODE**: Voltar/retornar ao menu anterior
4. Visualize informações da rede, sensores, atuadores e URL de acesso web
5. Configure novas redes e senhas via interface visual

### Via API REST

**Base URL**: `http://<IP_placa>:8080/api`

Exemplos:

```bash
# Obter status da rede
curl http://192.168.0.10:8080/api/wifi/status

# Controlar LED
curl -X POST http://192.168.0.10:8080/api/led/on

# Ler sensores
curl http://192.168.0.10:8080/api/sensor/dht11
```

Veja mais em [GUIDE.md](GUIDE.md#api-rest).

## 📖 Documentação Detalhada

Para instruções completas de instalação, troubleshooting, expansão de funcionalidades e exemplos avançados, consulte [GUIDE.md](GUIDE.md).

## 🔧 Integração de Novos Sensores

1. Crie um driver em `backend/libs/sensors/seu_sensor.py`
2. Importe-o no `app.py` e crie um endpoint REST
3. Exiba os dados no display ou no dashboard web

Exemplo:

```python
from libs.sensors.seu_sensor import MeuSensor

sensor = MeuSensor()

@app.route('/api/sensor/seu_sensor', methods=['GET'])
def get_sensor_data():
    valor = sensor.read()
    return jsonify({'valor': valor})
```

## 🐛 Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| Display não acende | Verifique I2C: `sudo i2cdetect -y 1` |
| Erro libgpiod | `sudo apt install python3-lgpio` |
| API não responde | Confira IP, porta 8080, e kill processos Python antigos |
| Botões não respondem | Verifique permissões em `/dev/input/` ou GPIO |
| Sensor não lê | Revise pino GPIO configurado e dependências do sensor |

## 📊 Performance e Limitações

- Display atualiza a cada 2 segundos
- API responde em ~100-200ms em rede local de 100Mbps
- Suporta até 10 usuários SSH simultâneos (limitação do sistema)
- Sensores DHT11 têm taxa de erro natural de 10-30% (implementado retry)

## 📜 Licença

MIT License — Veja [LICENSE](LICENSE) para detalhes completos.

## 👥 Autores

Desenvolvido como projeto final do **Curso de Linux Embarcado** para aplicação prática de conceitos de GPIO, I2C, Wi-Fi, APIs e automação em Raspberry Pi.

**Equipe**: [Adicione nomes aqui]  
**Data**: Novembro de 2025

---

## 🤝 Contribuindo

Contribuições, bug reports e sugestões são bem-vindas! Abra uma issue ou pull request no repositório.

---

**Pronto para produção?** Veja [GUIDE.md](GUIDE.md) para deploy, segurança e otimizações.
