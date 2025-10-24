# main.py
"""
Main application para gerenciador de Wi-Fi com display SSD1306 e teclado.

Fluxo de estados:
- MAIN: Tela principal com informações do sistema
- WIFI_LIST: Lista de redes disponíveis
- PASSWORD_ENTRY: Entrada de senha
- CONNECTING: Conectando à rede
"""

import subprocess
import time
import busio
from board import SCL, SDA
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

from libs.keyboard.keyboard import start_keyboard
from libs.display.display_utils import (
    draw_info_screen, draw_wifi_list, draw_password_entry,
    draw_connecting_screen, draw_status_screen
)
from utils.wifi_utils import (
    scan_wifi_networks, get_known_wifi_ssids, connect_to_wifi
)


# ============================================================================
# INICIALIZAÇÃO DO HARDWARE
# ============================================================================

# Display SSD1306
i2c = busio.I2C(SCL, SDA)
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
disp.fill(0)
disp.show()

# Imagem para desenho
width = disp.width
height = disp.height
image = Image.new("1", (width, height))
draw = ImageDraw.Draw(image)

# Fonte
font = ImageFont.truetype("fonts/LSANS.ttf", 10)

# Teclado
kb = start_keyboard('/dev/input/event0')


# ============================================================================
# UTILITÁRIOS DO SISTEMA
# ============================================================================

def get_system_info():
    """Coleta informações do sistema para exibição."""
    try:
        host = subprocess.check_output(
            "hostname", shell=True, text=True
        ).strip()
    except:
        host = "N/A"

    try:
        ip = subprocess.check_output(
            "hostname -I | awk '{print $1}'", shell=True, text=True
        ).strip()
    except:
        ip = "N/A"

    try:
        # Tenta obter SSID atual
        ssid = subprocess.check_output(
            "iwgetid -r", shell=True, text=True
        ).strip()
        wifi_status = "OK"
    except:
        ssid = "Desconectado"
        wifi_status = "OFF"

    try:
        ssh_result = subprocess.check_output(
            "systemctl is-active ssh", shell=True, text=True
        ).strip()
        ssh_status = "ON" if ssh_result == "active" else "OFF"
    except:
        ssh_status = "OFF"

    try:
        ssh_users = subprocess.check_output(
            "who | grep -c 'pts/' || echo 0", shell=True, text=True
        ).strip()
    except:
        ssh_users = "0"

    return {
        'host': host,
        'ip': ip,
        'ssid': ssid,
        'wifi_status': wifi_status,
        'ssh_status': ssh_status,
        'ssh_users': ssh_users
    }


# ============================================================================
# VARIÁVEIS DE ESTADO
# ============================================================================

menu_estado = 'MAIN'
wifi_lista = []
wifi_sel = 0
ssid_sel = ""
senha = ""
sistema_info = get_system_info()

# Para controlar timeout da tela de status
status_time = 0
STATUS_DISPLAY_TIME = 2  # Segundos que a tela de status permanece


# ============================================================================
# LOOP PRINCIPAL
# ============================================================================

try:
    while True:
        # ====== ESTADO: MAIN (Tela Principal) ======
        if menu_estado == 'MAIN':
            sistema_info = get_system_info()

            draw_info_screen(
                draw, width, height, font,
                host=sistema_info['host'],
                ip=sistema_info['ip'],
                wifi_status=sistema_info['wifi_status'],
                ssh_status=sistema_info['ssh_status'],
                ssh_users=sistema_info['ssh_users'],
                ssid=sistema_info['ssid']
            )

            disp.image(image)
            disp.show()

            # Detecção de tecla
            if kb.get_buffer().endswith('\x1b'):  # ESC
                menu_estado = 'WIFI_LIST'
                wifi_lista = scan_wifi_networks()
                wifi_sel = 0
                kb.clear_buffer()

            time.sleep(0.1)

        # ====== ESTADO: WIFI_LIST (Lista de Redes) ======
        elif menu_estado == 'WIFI_LIST':
            if not wifi_lista:
                # Se lista vazia, tenta escanear novamente
                wifi_lista = scan_wifi_networks()

            draw_wifi_list(
                draw, width, height, font,
                wifi_lista, wifi_sel
            )

            disp.image(image)
            disp.show()

            # Navegação
            if kb.get_buffer().endswith('\x1b[A'):  # Seta para cima
                if wifi_sel > 0:
                    wifi_sel -= 1
                kb.clear_buffer()

            elif kb.get_buffer().endswith('\x1b[B'):  # Seta para baixo
                if wifi_sel < len(wifi_lista) - 1:
                    wifi_sel += 1
                kb.clear_buffer()

            elif kb.get_buffer().endswith('\r'):  # Enter
                ssid_sel = wifi_lista[wifi_sel]
                known_ssids = get_known_wifi_ssids()

                if ssid_sel in known_ssids:
                    # Rede conhecida: conecta direto
                    menu_estado = 'CONNECTING'
                    senha = None
                else:
                    # Rede nova: pede senha
                    menu_estado = 'PASSWORD_ENTRY'
                    senha = ""

                kb.clear_buffer()

            elif kb.get_buffer().endswith('\x1b'):  # ESC
                menu_estado = 'MAIN'
                wifi_sel = 0
                kb.clear_buffer()

            time.sleep(0.1)

        # ====== ESTADO: PASSWORD_ENTRY (Entrada de Senha) ======
        elif menu_estado == 'PASSWORD_ENTRY':
            draw_password_entry(
                draw, width, height, font,
                ssid_sel, senha
            )

            disp.image(image)
            disp.show()

            # Processamento de teclas
            if kb.get_buffer().endswith('\r'):  # Enter
                menu_estado = 'CONNECTING'
                kb.clear_buffer()

            elif kb.get_buffer().endswith('\x08'):  # Backspace
                if senha:
                    senha = senha[:-1]
                kb.clear_buffer()

            elif kb.get_buffer().endswith('\x1b'):  # ESC
                menu_estado = 'WIFI_LIST'
                senha = ""
                kb.clear_buffer()

            elif kb.get_buffer() and not kb.get_buffer().endswith(('\r', '\x08', '\x1b')):
                # Adiciona novo caractere
                novos_chars = kb.get_buffer()
                for char in novos_chars:
                    if char not in ['\r', '\x08', '\x1b', '\x1b[A', '\x1b[B']:
                        senha += char
                kb.clear_buffer()

            time.sleep(0.1)

        # ====== ESTADO: CONNECTING (Conectando) ======
        elif menu_estado == 'CONNECTING':
            # Mostra tela de "Conectando..."
            draw_connecting_screen(draw, width, height, font, ssid_sel)
            disp.image(image)
            disp.show()

            # Tenta conectar
            sucesso, msg = connect_to_wifi(ssid_sel, senha)

            # Mostra resultado
            draw_status_screen(draw, width, height, font, sucesso, msg)
            disp.image(image)
            disp.show()

            # Aguarda antes de voltar ao menu
            time.sleep(STATUS_DISPLAY_TIME)

            # Se conectou com sucesso, atualiza lista de conhecidos
            if sucesso:
                get_known_wifi_ssids()  # Atualiza cache

            # Volta para MAIN
            menu_estado = 'MAIN'
            senha = ""
            kb.clear_buffer()

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nPrograma encerrado pelo usuário.")
    disp.fill(0)
    disp.show()
except Exception as e:
    print(f"Erro durante execução: {e}")
    disp.fill(0)
    disp.show()
