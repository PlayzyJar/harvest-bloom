# libs/display/virtual_keyboard_display.py
"""
Funções de renderização do teclado virtual no display SSD1306.
"""


def draw_virtual_keyboard(draw, width, height, font, keyboard, ssid=""):
    """
    Desenha o teclado virtual no display.

    Layout:
    - Linha 1-2: SSID e senha digitada
    - Linha 3-5: Grid de caracteres
    - Linha 6: Modo atual e instruções

    Args:
        draw: Objeto ImageDraw
        width, height: Dimensões do display
        font: Fonte para texto
        keyboard: Objeto VirtualKeyboard
        ssid: Nome da rede (opcional)
    """
    # Limpa display
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Linha 1: SSID (se fornecido)
    y_pos = 0
    if ssid:
        draw.text((0, y_pos), f"SSID: {ssid[:12]}", font=font, fill=255)
        y_pos += 10

    # Linha 2: Senha digitada (sem máscara para facilitar testes)
    senha_display = keyboard.password[-14:] if len(
        keyboard.password) > 14 else keyboard.password
    draw.text((0, y_pos), f"Pwd: {senha_display}", font=font, fill=255)
    y_pos += 12

    # Grid de caracteres (apenas primeira linha visível + cursor)
    layout = keyboard.get_current_layout()
    current_char = keyboard.get_current_char()

    # Mostra 7 caracteres ao redor do cursor
    visible_range = 7
    start_idx = max(0, keyboard.cursor_pos - 3)
    end_idx = min(len(layout), start_idx + visible_range)

    # Ajusta se estiver no final
    if end_idx - start_idx < visible_range and end_idx == len(layout):
        start_idx = max(0, end_idx - visible_range)

    # Desenha caracteres visíveis
    x_pos = 0
    for i in range(start_idx, end_idx):
        char = layout[i]
        char_width = 16  # Largura fixa por caractere

        # Destaca o caractere selecionado
        if i == keyboard.cursor_pos:
            # Fundo invertido
            draw.rectangle(
                (x_pos, y_pos - 1, x_pos + char_width - 2, y_pos + 11),
                outline=255, fill=255
            )
            draw.text((x_pos + 2, y_pos), char[:3], font=font, fill=0)
        else:
            draw.text((x_pos + 2, y_pos), char[:3], font=font, fill=255)

        x_pos += char_width

    y_pos += 14

    # Indicadores de mais caracteres
    if keyboard.cursor_pos > 3:
        draw.text((0, y_pos), "<", font=font, fill=255)
    if keyboard.cursor_pos < len(layout) - 4:
        draw.text((width - 8, y_pos), ">", font=font, fill=255)

    y_pos += 10

    # Footer: Modo e instruções
    mode_name = keyboard.get_mode_name()
    draw.text((0, height - 10), f"Mode:{mode_name}", font=font, fill=255)
    draw.text((60, height - 10), "L/R:Nav SEL:OK", font=font, fill=255)


def draw_virtual_keyboard_compact(draw, width, height, font, keyboard, ssid=""):
    """
    Versão compacta: mostra grid 3x3 do teclado.

    Args:
        draw: Objeto ImageDraw
        width, height: Dimensões
        font: Fonte
        keyboard: Objeto VirtualKeyboard
        ssid: Nome da rede
    """
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Senha
    y_pos = 0
    if ssid:
        draw.text((0, y_pos), ssid[:16], font=font, fill=255)
        y_pos += 9

    senha_display = keyboard.password[-16:]
    draw.text((0, y_pos), senha_display, font=font, fill=255)
    y_pos += 11

    # Grid 3x3 centralizado no cursor
    layout = keyboard.get_current_layout()

    # Pega 9 caracteres ao redor do cursor (3x3)
    center = keyboard.cursor_pos
    start = max(0, center - 4)
    visible_chars = layout[start:start + 9]

    # Desenha grid 3x3
    for row in range(3):
        x_pos = 5
        for col in range(3):
            idx = row * 3 + col
            if idx >= len(visible_chars):
                break

            char = visible_chars[idx]
            global_idx = start + idx

            # Verifica se é o cursor
            if global_idx == keyboard.cursor_pos:
                draw.rectangle(
                    (x_pos - 2, y_pos - 1, x_pos + 16, y_pos + 9),
                    outline=255, fill=255
                )
                draw.text((x_pos, y_pos), char[:3], font=font, fill=0)
            else:
                draw.rectangle(
                    (x_pos - 2, y_pos - 1, x_pos + 16, y_pos + 9),
                    outline=255, fill=0
                )
                draw.text((x_pos, y_pos), char[:3], font=font, fill=255)

            x_pos += 20

        y_pos += 11

    # Footer
    draw.text((0, height - 9),
              f"{keyboard.get_mode_name()}", font=font, fill=255)
    draw.text((40, height - 9), "MODE:Switch", font=font, fill=255)
