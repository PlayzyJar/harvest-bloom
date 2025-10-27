# main.py
"""
Projeto Final - Curso Linux Embarcado
WiFi Manager com interface GPIO para Raspberry Pi

Fase 1: Inicialização e Interface Local
- Exibe informações do sistema no display OLED SSD1306
- Detecta estado da conexão Wi-Fi
- Modo conectado: hostname, IP, sinal Wi-Fi, SSH, usuários, SSID
- Modo desconectado: lista SSIDs disponíveis para configuração
"""

import subprocess
import time
import busio
from board import SCL, SDA
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

from libs.input_gpio.buttons import ButtonManager
from libs.input_gpio.virtual_keyboard import VirtualKeyboard
from libs.display.display_utils import (
    draw_info_screen, draw_wifi_list
)
from libs.display.virtual_keyboard_display import draw_virtual_keyboard
from utils.wifi_utils import (
    scan_wifi_networks, get_known_wifi_ssids, connect_to_wifi
)


# ============================================================================
# INICIALIZAÇÃO DO HARDWARE
# ============================================================================

print("Inicializando hardware...")

# Display SSD1306
try:
    i2c = busio.I2C(SCL, SDA)
    disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
    disp.fill(0)
    disp.show()
    print("✓ Display inicializado")
except Exception as e:
    print(f"✗ Erro ao inicializar display: {e}")
    exit(1)

# Configuração da imagem
width = disp.width
height = disp.height
image = Image.new("1", (width, height))
draw = ImageDraw.Draw(image)

# Fonte
try:
    font = ImageFont.truetype("fonts/LSANS.ttf", 9)
    print("✓ Fonte carregada")
except:
    print("! Fonte customizada não encontrada, usando padrão")
    font = ImageFont.load_default()

# Botões GPIO
try:
    buttons = ButtonManager()
    print("✓ Botões GPIO configurados")
except Exception as e:
    print(f"✗ Erro ao configurar botões: {e}")
    exit(1)

# Teclado virtual
vkeyboard = VirtualKeyboard()
print("✓ Teclado virtual inicializado")


# ============================================================================
# FUNÇÕES DE COLETA DE INFORMAÇÕES DO SISTEMA
# ============================================================================

def get_wifi_signal_level():
    """
    Obtém nível do sinal Wi-Fi em dBm.

    Retorna:
        str: Nível do sinal (ex: "-50 dBm") ou "N/A"
    """
    try:
        output = subprocess.check_output(
            "iw dev wlan0 link | awk '/signal/ {print $2 \" dBm\"}'",
            shell=True,
            text=True
        ).strip()
        return output if output else "N/A"
    except:
        return "N/A"


def check_wifi_connected():
    """
    Verifica se Wi-Fi está conectado.

    Retorna:
        tuple: (conectado: bool, ssid: str)
    """
    try:
        ssid = subprocess.check_output(
            "iwgetid -r",
            shell=True,
            text=True
        ).strip()
        return True, ssid
    except:
        return False, ""


def get_system_info():
    """
    Coleta todas as informações do sistema para Fase 1.

    Retorna:
        dict: Informações do sistema
    """
    info = {}

    # Hostname
    try:
        info['host'] = subprocess.check_output(
            "hostname",
            shell=True,
            text=True
        ).strip()
    except:
        info['host'] = "N/A"

    # IP
    try:
        info['ip'] = subprocess.check_output(
            "hostname -I | awk '{print $1}'",
            shell=True,
            text=True
        ).strip()
    except:
        info['ip'] = "N/A"

    # Wi-Fi conectado?
    is_connected, ssid = check_wifi_connected()
    info['wifi_connected'] = is_connected
    info['ssid'] = ssid if is_connected else "Desconectado"

    # Nível do sinal Wi-Fi
    if is_connected:
        info['wifi_signal'] = get_wifi_signal_level()
        info['wifi_status'] = "Conectado"
    else:
        info['wifi_signal'] = "N/A"
        info['wifi_status'] = "Desconectado"

    # SSH ativo?
    try:
        ssh_result = subprocess.check_output(
            "systemctl is-active ssh",
            shell=True,
            text=True
        ).strip()
        info['ssh_status'] = "Ativo" if ssh_result == "active" else "Inativo"
    except:
        info['ssh_status'] = "Inativo"

    # Usuários SSH conectados
    try:
        info['ssh_users'] = subprocess.check_output(
            "who | grep -c 'pts/' || echo 0",
            shell=True,
            text=True
        ).strip()
    except:
        info['ssh_users'] = "0"

    return info


# ============================================================================
# VARIÁVEIS DE ESTADO DO MENU
# ============================================================================

# Estados: CHECK_WIFI, MAIN_CONNECTED, MAIN_DISCONNECTED, WIFI_LIST, PASSWORD_ENTRY, CONNECTING
menu_estado = 'CHECK_WIFI'
wifi_lista = []
wifi_sel = 0
ssid_sel = ""
sistema_info = {}
last_update = 0
UPDATE_INTERVAL = 2  # Atualiza info a cada 2 segundos


# ============================================================================
# CALLBACKS DOS BOTÕES GPIO
# ============================================================================

def on_button_left():
    """Botão LEFT: navega para esquerda."""
    global wifi_sel

    if menu_estado == 'WIFI_LIST':
        if wifi_sel > 0:
            wifi_sel -= 1
    elif menu_estado == 'PASSWORD_ENTRY':
        vkeyboard.move_left()


def on_button_right():
    """Botão RIGHT: navega para direita."""
    global wifi_sel

    if menu_estado == 'WIFI_LIST':
        if wifi_sel < len(wifi_lista) - 1:
            wifi_sel += 1
    elif menu_estado == 'PASSWORD_ENTRY':
        vkeyboard.move_right()


def on_button_select():
    """Botão SELECT: confirma seleção."""
    global menu_estado, wifi_sel, ssid_sel

    if menu_estado == 'MAIN_CONNECTED':
        # Conectado: SELECT abre lista de redes (para trocar)
        menu_estado = 'WIFI_LIST'
        wifi_lista[:] = scan_wifi_networks()
        wifi_sel = 0

    elif menu_estado == 'MAIN_DISCONNECTED':
        # Desconectado: SELECT abre lista de redes
        menu_estado = 'WIFI_LIST'
        wifi_lista[:] = scan_wifi_networks()
        wifi_sel = 0

    elif menu_estado == 'WIFI_LIST':
        # Seleciona rede
        if wifi_lista:
            ssid_sel = wifi_lista[wifi_sel]
            known_ssids = get_known_wifi_ssids()

            if ssid_sel in known_ssids:
                # Rede conhecida: conecta direto
                menu_estado = 'CONNECTING'
            else:
                # Rede nova: pede senha
                vkeyboard.reset()
                menu_estado = 'PASSWORD_ENTRY'

    elif menu_estado == 'PASSWORD_ENTRY':
        # Confirma caractere
        result = vkeyboard.select_char()
        if result == 'DONE':
            menu_estado = 'CONNECTING'


def on_button_mode():
    """Botão MODE: modo/voltar."""
    global menu_estado

    if menu_estado == 'WIFI_LIST':
        # Volta para tela principal
        menu_estado = 'CHECK_WIFI'

    elif menu_estado == 'PASSWORD_ENTRY':
        # Alterna modo do teclado
        vkeyboard.toggle_mode()

    elif menu_estado == 'MAIN_CONNECTED':
        # Atualiza informações manualmente
        pass


# Configura callbacks dos botões
buttons.set_callbacks(
    on_left=on_button_left,
    on_right=on_button_right,
    on_select=on_button_select,
    on_mode=on_button_mode
)

print("✓ Callbacks configurados")
print("\n" + "="*50)
print("SISTEMA INICIADO - Fase 1")
print("="*50)


# ============================================================================
# LOOP PRINCIPAL
# ============================================================================

try:
    while True:
        current_time = time.time()

        # ====== CHECK_WIFI: Verifica estado da conexão ======
        if menu_estado == 'CHECK_WIFI':
            # Atualiza informações do sistema
            sistema_info = get_system_info()

            # Decide próximo estado baseado na conexão
            if sistema_info['wifi_connected']:
                menu_estado = 'MAIN_CONNECTED'
            else:
                menu_estado = 'MAIN_DISCONNECTED'

            last_update = current_time

        # ====== MAIN_CONNECTED: Mostra informações (Wi-Fi conectado) ======
        elif menu_estado == 'MAIN_CONNECTED':
            # Atualiza info periodicamente
            if current_time - last_update >= UPDATE_INTERVAL:
                sistema_info = get_system_info()
                last_update = current_time

                # Se desconectou, muda estado
                if not sistema_info['wifi_connected']:
                    menu_estado = 'CHECK_WIFI'
                    continue

            # Desenha tela de informações
            draw_info_screen(
                draw, width, height, font,
                host=sistema_info['host'],
                ip=sistema_info['ip'],
                wifi_status=sistema_info['wifi_status'],
                wifi_signal=sistema_info['wifi_signal'],
                ssh_status=sistema_info['ssh_status'],
                ssh_users=sistema_info['ssh_users'],
                ssid=sistema_info['ssid']
            )

            # Footer customizado
            draw.rectangle((0, height - 9, width, height), outline=0, fill=0)
            draw.text((0, height - 8), "SELECT: Trocar Rede",
                      font=font, fill=255)

            disp.image(image)
            disp.show()

        # ====== MAIN_DISCONNECTED: Mostra lista de SSIDs ======
        elif menu_estado == 'MAIN_DISCONNECTED':
            # Escaneia redes disponíveis
            if not wifi_lista or current_time - last_update >= 10:
                wifi_lista = scan_wifi_networks()
                last_update = current_time

            if wifi_lista:
                # Mostra lista de redes
                draw_wifi_list(draw, width, height, font, wifi_lista, wifi_sel)

                # Footer customizado
                draw.rectangle((0, height - 9, width, height),
                               outline=0, fill=0)
                draw.text((0, height - 8), "L/R:Nav SEL:Conectar",
                          font=font, fill=255)
            else:
                # Nenhuma rede encontrada
                draw.rectangle((0, 0, width, height), outline=0, fill=0)
                draw.text((10, 20), "Nenhuma rede", font=font, fill=255)
                draw.text((10, 30), "encontrada", font=font, fill=255)
                draw.text((0, height - 8), "Escaneando...",
                          font=font, fill=255)

            disp.image(image)
            disp.show()

        # ====== WIFI_LIST: Lista de redes (modo conectado) ======
        elif menu_estado == 'WIFI_LIST':
            if not wifi_lista:
                wifi_lista = scan_wifi_networks()

            draw_wifi_list(draw, width, height, font, wifi_lista, wifi_sel)

            # Footer
            draw.rectangle((0, height - 9, width, height), outline=0, fill=0)
            draw.text((0, height - 8), "L/R:Nav SEL:Ok MODE:Back",
                      font=font, fill=255)

            disp.image(image)
            disp.show()

        # ====== PASSWORD_ENTRY: Entrada de senha ======
        elif menu_estado == 'PASSWORD_ENTRY':
            draw_virtual_keyboard(
                draw, width, height, font,
                vkeyboard, ssid_sel
            )

            disp.image(image)
            disp.show()

        # ====== CONNECTING: Conectando à rede ======
        elif menu_estado == 'CONNECTING':
            # Mostra "Conectando..."
            draw.rectangle((0, 0, width, height), outline=0, fill=0)
            draw.text((15, 20), "Conectando...", font=font, fill=255)
            draw.text((5, 35), ssid_sel[:18], font=font, fill=255)
            disp.image(image)
            disp.show()

            # Tenta conectar
            senha = vkeyboard.password if vkeyboard.password else None
            sucesso, msg = connect_to_wifi(ssid_sel, senha)

            # Mostra resultado
            draw.rectangle((0, 0, width, height), outline=0, fill=0)
            if sucesso:
                draw.text((20, 25), "Conectado!", font=font, fill=255)
                draw.text((10, 40), "Aguarde...", font=font, fill=255)
            else:
                draw.text((25, 20), "Erro!", font=font, fill=255)
                draw.text((5, 35), msg[:20], font=font, fill=255)
                draw.text((5, 50), "Voltando...", font=font, fill=255)

            disp.image(image)
            disp.show()
            time.sleep(3)

            # Reseta e volta ao início
            vkeyboard.reset()
            wifi_lista = []
            menu_estado = 'CHECK_WIFI'

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\n\nEncerrando aplicação...")
    buttons.cleanup()
    disp.fill(0)
    disp.show()
    print("✓ Aplicação encerrada")
except Exception as e:
    print(f"\n✗ Erro durante execução: {e}")
    import traceback
    traceback.print_exc()
    buttons.cleanup()
    disp.fill(0)
    disp.show()
