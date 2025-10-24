# libs/display/display_utils.py
"""
Funções utilitárias para desenho no display SSD1306.
Centraliza toda a lógica visual para manter a main limpa.
"""

from PIL import ImageDraw, ImageFont


def clear_display(draw, width, height):
    """Limpa o display (desenha retângulo preto)."""
    draw.rectangle((0, 0, width, height), outline=0, fill=0)


def draw_info_screen(draw, width, height, font, host="", ip="", wifi_status="",
                     ssh_status="", ssh_users="", ssid=""):
    """
    Desenha a tela principal com informações do sistema.

    Args:
        draw: Objeto ImageDraw
        width, height: Dimensões do display
        font: Fonte para texto
        host, ip, wifi_status, ssh_status, ssh_users, ssid: Informações a exibir
    """
    clear_display(draw, width, height)

    y_pos = 2
    line_height = 9

    draw.text((0, y_pos), f"Host: {host}", font=font, fill=255)
    y_pos += line_height

    draw.text((0, y_pos), f"IP: {ip}", font=font, fill=255)
    y_pos += line_height

    draw.text((0, y_pos), f"WiFi: {wifi_status}", font=font, fill=255)
    y_pos += line_height

    draw.text((0, y_pos), f"SSH: {ssh_status}", font=font, fill=255)
    y_pos += line_height

    draw.text((0, y_pos), f"Users: {ssh_users}", font=font, fill=255)
    y_pos += line_height

    draw.text((0, y_pos), f"SSID: {ssid}", font=font, fill=255)

    # Footer
    draw.text((0, height - 8), "ESC: WiFi Menu", font=font, fill=255)


def draw_wifi_list(draw, width, height, font, wifi_list, selected_index):
    """
    Desenha lista de redes Wi-Fi com scroll e highlight.

    A rede selecionada aparece com fundo invertido (mais elegante).
    Mostra scroll indicator se houver mais redes.

    Args:
        draw: Objeto ImageDraw
        width, height: Dimensões
        font: Fonte
        wifi_list: Lista de SSIDs
        selected_index: Índice da rede selecionada
    """
    clear_display(draw, width, height)

    # Configuração do scroll
    items_per_page = 5
    scroll_start = max(0, selected_index - 2)  # Mantém seleção no meio
    scroll_end = min(len(wifi_list), scroll_start + items_per_page)

    # Ajusta scroll_start se necessário
    if selected_index >= len(wifi_list) - 2:
        scroll_start = max(0, len(wifi_list) - items_per_page)

    # Título
    draw.text((0, 2), "Redes WiFi:", font=font, fill=255)

    y_pos = 14
    line_height = 10

    # Desenha redes na página atual
    for i in range(scroll_start, scroll_end):
        ssid = wifi_list[i][:20]  # Limita SSID a 20 caracteres
        is_selected = (i == selected_index)

        if is_selected:
            # Highlight com fundo invertido (preto no branco)
            draw.rectangle(
                (0, y_pos - 1, width - 1, y_pos + 8),
                outline=255, fill=255
            )
            draw.text((2, y_pos), ssid, font=font, fill=0)  # Texto preto
        else:
            draw.text((2, y_pos), ssid, font=font, fill=255)  # Texto branco

        y_pos += line_height

    # Indicators de scroll
    if scroll_start > 0:
        draw.text((width - 6, 14), "^", font=font, fill=255)

    if scroll_end < len(wifi_list):
        draw.text((width - 6, height - 10), "v", font=font, fill=255)

    # Footer
    draw.text((0, height - 8), "↑↓ Nav  ENTER Select  ESC Back",
              font=font, fill=255)


def draw_password_entry(draw, width, height, font, ssid, password, show_instructions=True):
    """
    Desenha tela de entrada de senha.

    Args:
        draw: Objeto ImageDraw
        width, height: Dimensões
        font: Fonte
        ssid: Nome da rede (para exibição)
        password: Senha digitada (para contar caracteres)
        show_instructions: Se mostra instruções ou não
    """
    clear_display(draw, width, height)

    # Cabeçalho
    draw.text((0, 2), "Conexao WiFi", font=font, fill=255)
    draw.text((0, 14), f"SSID: {ssid[:18]}", font=font, fill=255)

    # Campo de senha
    draw.text((0, 28), "Senha:", font=font, fill=255)
    password_display = "*" * len(password)
    draw.text((50, 28), password_display[:15], font=font, fill=255)

    if show_instructions:
        draw.text((0, 45), "ENTER: OK  BKSP: Apaga", font=font, fill=255)
        draw.text((0, 55), "ESC: Cancelar", font=font, fill=255)


def draw_connecting_screen(draw, width, height, font, ssid):
    """
    Desenha tela de "Conectando...".

    Args:
        draw: Objeto ImageDraw
        width, height: Dimensões
        font: Fonte
        ssid: Nome da rede
    """
    clear_display(draw, width, height)

    draw.text((15, 15), "Conectando...", font=font, fill=255)
    draw.text((10, 35), ssid[:20], font=font, fill=255)


def draw_status_screen(draw, width, height, font, success, message=""):
    """
    Desenha tela de resultado (conectado ou erro).

    Args:
        draw: Objeto ImageDraw
        width, height: Dimensões
        font: Fonte
        success: True se conectou, False se erro
        message: Mensagem de erro (se houver)
    """
    clear_display(draw, width, height)

    if success:
        draw.text((20, 25), "Conectado!", font=font, fill=255)
        draw.text((0, 45), "Voltando ao menu...", font=font, fill=255)
    else:
        draw.text((10, 15), "ERRO!", font=font, fill=255)
        draw.text((0, 30), "Falha na conexao", font=font, fill=255)
        if message:
            draw.text((0, 42), message[:20], font=font, fill=255)
