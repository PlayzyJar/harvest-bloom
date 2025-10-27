# libs/input_gpio/virtual_keyboard.py
"""
Teclado virtual para entrada de senha usando display e botões GPIO.
Estilo TV: navegação por caracteres com LEFT/RIGHT, SELECT para confirmar.
"""


class VirtualKeyboard:
    """
    Teclado virtual com 3 modos: ABC, 123, Especiais.
    Permite entrada de senha navegando por caracteres.
    """

    # Layouts de caracteres
    LAYOUT_ABC = [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
        'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
        's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
        'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
        'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
        'OK', 'DEL', 'SPC'
    ]

    LAYOUT_123 = [
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        'OK', 'DEL', 'SPC'
    ]

    LAYOUT_SPECIAL = [
        '!', '@', '#', '$', '%', '^', '&', '*', '(', ')',
        '-', '_', '=', '+', '[', ']', '{', '}', '\\', '|',
        ';', ':', "'", '"', ',', '.', '<', '>', '/', '?',
        'OK', 'DEL', 'SPC'
    ]

    MODE_NAMES = ['ABC', '123', '!@#']

    def __init__(self):
        """Inicializa o teclado virtual."""
        self.password = ""
        self.cursor_pos = 0
        self.mode = 0  # 0=ABC, 1=123, 2=Especial
        self.layouts = [self.LAYOUT_ABC, self.LAYOUT_123, self.LAYOUT_SPECIAL]

    def get_current_layout(self):
        """Retorna o layout atual baseado no modo."""
        return self.layouts[self.mode]

    def get_current_char(self):
        """Retorna o caractere na posição do cursor."""
        layout = self.get_current_layout()
        return layout[self.cursor_pos]

    def move_left(self):
        """Move cursor para esquerda (circular)."""
        self.cursor_pos -= 1
        if self.cursor_pos < 0:
            self.cursor_pos = len(self.get_current_layout()) - 1

    def move_right(self):
        """Move cursor para direita (circular)."""
        self.cursor_pos += 1
        if self.cursor_pos >= len(self.get_current_layout()):
            self.cursor_pos = 0

    def select_char(self):
        """
        Seleciona o caractere atual.

        Retorna:
            str: 'DONE' se confirmou senha, 'CONTINUE' caso contrário
        """
        char = self.get_current_char()

        if char == 'OK':
            return 'DONE'
        elif char == 'DEL':
            if self.password:
                self.password = self.password[:-1]
        elif char == 'SPC':
            self.password += ' '
        else:
            self.password += char

        return 'CONTINUE'

    def toggle_mode(self):
        """Alterna entre modos ABC → 123 → !@# → ABC."""
        self.mode = (self.mode + 1) % 3
        self.cursor_pos = 0  # Reseta posição ao trocar modo

    def get_mode_name(self):
        """Retorna nome do modo atual."""
        return self.MODE_NAMES[self.mode]

    def reset(self):
        """Reseta o teclado virtual."""
        self.password = ""
        self.cursor_pos = 0
        self.mode = 0

    def get_display_grid(self, chars_per_row=9):
        """
        Retorna layout atual em formato de grid para exibição.

        Args:
            chars_per_row: Quantos caracteres por linha

        Retorna:
            list: Lista de listas (linhas do teclado)
        """
        layout = self.get_current_layout()
        rows = []
        for i in range(0, len(layout), chars_per_row):
            rows.append(layout[i:i+chars_per_row])
        return rows
