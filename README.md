# WiFi Manager - Raspberry Pi

Gerenciador de conexões Wi-Fi com interface visual usando display OLED SSD1306 e teclado USB. Desenvolvido para Raspberry Pi com sistema operacional Linux.

## Funcionalidades

- Visualização de informações do sistema (hostname, IP, status SSH)
- Listagem de redes Wi-Fi disponíveis com scroll responsivo
- Conexão automática em redes conhecidas
- Entrada de senha para redes novas via teclado físico
- Interface visual intuitiva com navegação por setas

## Hardware Necessário

- Raspberry Pi (testado em Pi 3/4)
- Display OLED SSD1306 128x64 (interface I2C)
- Teclado USB
- Adaptador Wi-Fi (se não embutido)

## Requisitos de Software

```bash
sudo apt update
sudo apt install python3 python3-pip
```

### Dependências Python

```bash
pip3 install adafruit-circuitpython-ssd1306
pip3 install pillow
pip3 install evdev
pip3 install board
pip3 install busio
```

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/wifi-manager-pi.git
cd wifi-manager-pi
```

2. Instale as dependências:
```bash
pip3 install -r requirements.txt
```

3. Identifique o device do teclado:
```bash
ls /dev/input/
# Geralmente event0, event1, etc.
# Edite main.py e ajuste o path em start_keyboard()
```

## Como Usar

### Execução

```bash
python3 main.py
```

### Navegação

**Tela Principal (INFO):**
- `ESC` - Abre menu de Wi-Fi

**Menu de Redes:**
- `↑` / `↓` - Navega entre redes
- `ENTER` - Seleciona rede
- `ESC` - Volta para tela principal

**Entrada de Senha:**
- Digite a senha usando o teclado
- `BACKSPACE` - Remove último caractere
- `ENTER` - Confirma e conecta
- `ESC` - Cancela

## Estrutura do Projeto

```
wifi-manager-pi/
├── main.py                 # Aplicação principal
├── libs/
│   ├── keyboard/
│   │   └── keyboard.py     # Driver do teclado USB
│   └── display/
│       └── display_utils.py # Funções de renderização
├── utils/
│   └── wifi_utils.py       # Funções de gerenciamento Wi-Fi
├── fonts/
│   └── LSANS.ttf          # Fonte para display
└── tests/                  # Testes de desenvolvimento
```

## Configuração do I2C

Habilite o I2C no Raspberry Pi:

```bash
sudo raspi-config
# Interface Options > I2C > Enable
sudo reboot
```

Verifique se o display está conectado:

```bash
sudo i2cdetect -y 1
# Deve aparecer o endereço 0x3C ou 0x3D
```

## Permissões

O programa precisa de permissões sudo para:
- Escanear redes Wi-Fi (`nmcli`)
- Conectar a novas redes

Execute com sudo ou configure permissões:

```bash
sudo python3 main.py
```

## Troubleshooting

**Display não inicializa:**
- Verifique conexões I2C (SDA, SCL, VCC, GND)
- Confirme endereço I2C com `i2cdetect`
- Teste se I2C está habilitado

**Teclado não responde:**
- Verifique device path em `main.py`
- Use `sudo python3` para garantir acesso ao /dev/input

**Scan de redes vazio:**
- Confirme que Wi-Fi está ativo: `nmcli radio wifi on`
- Execute com sudo

**Erro de import:**
- Instale dependências: `pip3 install -r requirements.txt`
- Execute da raiz do projeto

## Tecnologias

- Python 3
- Adafruit CircuitPython SSD1306
- NetworkManager (nmcli)
- evdev (input handling)
- PIL/Pillow (graphics)

## Licença

MIT License - veja LICENSE para detalhes.

## Autor

Desenvolvido como projeto acadêmico.
