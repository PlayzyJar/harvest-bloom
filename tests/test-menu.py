from keyboard import start_keyboard
import subprocess
import time

import busio
from board import SCL, SDA
from PIL import Image, ImageDraw, ImageFont

import adafruit_ssd1306


# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Load default font.
font = ImageFont.truetype("fonts/LSANS.ttf", 10)

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)


def run_cmd(cmd):
    return subprocess.check_output(cmd, shell=True).decode("utf-8").strip()


def scan_wifi_networks():
    """Retorna uma lista de dicts com SSID e sinal (%) das redes disponíveis."""
    try:
        output = subprocess.check_output(
            ["sudo", "nmcli", "-t", "-f", "SSID", "device", "wifi", "list"],
            text=True
        )

        redes = []

        for linha in output.strip().split('\n'):
            ssid = linha.strip()

            redes.append(ssid)

        return redes
    except Exception as e:
        print("Erro ao escanear redes:", e)
        return []


def get_known_wifi_ssids():
    output = subprocess.check_output(
        ["nmcli", "-t", "-f", "NAME", "connection", "show"], text=True
    )

    ssids = []

    for line in output.strip().split("\n"):
        ssid = line.strip()
        ssids.append(ssid)

    return ssids


def connect_to_wifi(ssid, senha=None):
    known_ssids = get_known_wifi_ssids()

    try:
        if ssid in known_ssids:
            res = f"sudo nmcli con up '{ssid}'"
            # Rede já conhecida: ativa conexão salva
            subprocess.check_output(res, shell=True)
            print(f"rodou o nmcli connection up '{ssid}'")
        else:
            # Rede nova: conecta e salva config
            res = f"sudo nmcli dev wifi connect '{ssid}' password '{senha}'"
            subprocess.check_output(res, shell=True)
            print(f"rodou o comando nmcli device wifi connect {
                  ssid} password {senha}")

        success = res.returncode == 0

        msg = res.stdout + res.stderr

        return success, msg
    except Exception as e:
        return False, str(e)


menu_estado = 'MAIN'  # ou 'LISTA_WIFI' ou 'ENTRA_SENHA' ou 'STATUS'
wifi_lista = scan_wifi_networks()
wifi_sel = 0
senha = ''
mensagem = ''

kb = start_keyboard('/dev/input/event0')

while True:
    if menu_estado == 'MAIN':
        # Desenha tela principal
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        draw.text((0, 0), "Host: foo", font=font, fill=255)
        draw.text((0, 10), "Wi-Fi: OK", font=font, fill=255)
        draw.text((0, 30), "Press Enter: Wi-Fi", font=font, fill=255)
        disp.image(image)
        disp.show()

        k = kb.get_buffer()[-1:]  # pega última tecla
        if k == '\r':
            menu_estado = 'LISTA_WIFI'
            kb.clear_buffer()

    elif menu_estado == 'LISTA_WIFI':
        # Desenha lista simulada de redes
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        draw.text((0, 0), "Redes Wi-Fi:", font=font, fill=255)
        for i, rede in enumerate(wifi_lista):
            prefix = '>' if i == wifi_sel else ' '
            draw.text((0, 15 + i*10), f"{prefix} {rede}", font=font, fill=255)
        disp.image(image)
        disp.show()

        if kb.get_buffer().endswith('\x1b[A'):  # seta para cima
            if wifi_sel > 0:
                wifi_sel -= 1
                kb.clear_buffer()

        elif kb.get_buffer().endswith('\x1b[B'):  # seta para baixo
            if wifi_sel < len(wifi_lista) - 1:
                wifi_sel += 1
                kb.clear_buffer()

        elif kb.get_buffer().endswith('\r'):
            # string ou dict['ssid'], adapte ao seu caso
            ssid_sel = wifi_lista[wifi_sel]
            print(f"selecionado: {ssid_sel}")
            # Atualiza a lista de conhecidos, por garantia

            known_ssids = get_known_wifi_ssids()

            for known in known_ssids:
                print(f"conhecido: {known}")

            if ssid_sel in known_ssids:
                menu_estado = 'STATUS_CONECTANDO'
                senha = None
            else:
                print("colocar a senha")
                menu_estado = 'ENTRA_SENHA'
            kb.clear_buffer()

        elif kb.get_buffer().endswith('\x1b'):  # ESC
            menu_estado = 'MAIN'
            kb.clear_buffer()

    elif menu_estado == 'ENTRA_SENHA':
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        draw.text((0, 0), "SSID:", font=font, fill=255)
        draw.text((35, 0), ssid_sel, font=font, fill=255)
        draw.text((0, 20), "Senha:", font=font, fill=255)
        senha_stars = "*" * len(senha)
        draw.text((50, 20), senha_stars, font=font, fill=255)
        draw.text((0, 45), "ENTER: OK  BKSP: Apaga", font=font, fill=255)
        disp.image(image)
        disp.show()

        if kb.get_buffer().endswith('\r'):
            # Enter foi pressionado
            menu_estado = 'STATUS_CONECTANDO'
            kb.clear_buffer()

        elif kb.get_buffer().endswith('\x08'):
            # Backspace (verifique se é '\x7f' ou '\x08' no seu teclado)
            senha = senha[:-1]
            kb.clear_buffer()

        elif kb.get_buffer().endswith('\x1b'):
            # ESC pressionado, cancela operação
            menu_estado = 'MAIN'
            senha = ""
            kb.clear_buffer()

        elif kb.get_buffer()[-1:] not in ['\r', '\x08', '\x1b'] and kb.get_buffer():
            # Qualquer outro caracter digitado
            senha += kb.get_buffer()[-1:]
            kb.clear_buffer()

    elif menu_estado == 'STATUS_CONECTANDO':
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        draw.text((5, 20), "Conectando...", font=font, fill=255)
        disp.image(image)
        disp.show()

        # Chama função de conexão (lembre que pode demorar)
        ok, msg = connect_to_wifi(ssid_sel, senha)

        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        if ok:
            draw.text((10, 20), "Conectado!", font=font, fill=255)
        else:
            draw.text((0, 15), "ERRO ao conectar!", font=font, fill=255)
            # Mostra parte da msg de erro
            draw.text((0, 30), msg[:18], font=font, fill=255)
        disp.image(image)
        disp.show()
        time.sleep(2)  # Mantém tela de status por 2s

        # Limpa senha e buffer pro próximo ciclo
        senha = ""
        kb.clear_buffer()
        menu_estado = 'MAIN'

    time.sleep(0.1)
