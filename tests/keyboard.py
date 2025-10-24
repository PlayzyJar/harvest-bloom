# keyboard.py
from evdev import InputDevice, categorize, ecodes
import threading


class Keyboard:
    def __init__(self, device_path):
        self.dev = InputDevice(device_path)
        self.caps_lock = False
        self.shift_pressed = False
        self.buffer = []
        self.lock = threading.Lock()

        # Keymap
        self.keycode_map = {
            'KEY_A': 'a', 'KEY_B': 'b', 'KEY_C': 'c', 'KEY_D': 'd',
            'KEY_E': 'e', 'KEY_F': 'f', 'KEY_G': 'g', 'KEY_H': 'h',
            'KEY_I': 'i', 'KEY_J': 'j', 'KEY_K': 'k', 'KEY_L': 'l',
            'KEY_M': 'm', 'KEY_N': 'n', 'KEY_O': 'o', 'KEY_P': 'p',
            'KEY_Q': 'q', 'KEY_R': 'r', 'KEY_S': 's', 'KEY_T': 't',
            'KEY_U': 'u', 'KEY_V': 'v', 'KEY_W': 'w', 'KEY_X': 'x',
            'KEY_Y': 'y', 'KEY_Z': 'z',
            'KEY_SPACE': ' ',
            'KEY_1': '1', 'KEY_2': '2', 'KEY_3': '3', 'KEY_4': '4', 'KEY_5': '5',
            'KEY_6': '6', 'KEY_7': '7', 'KEY_8': '8', 'KEY_9': '9', 'KEY_0': '0',
            'KEY_MINUS': '-', 'KEY_EQUAL': '=', 'KEY_COMMA': ',', 'KEY_DOT': '.',
            'KEY_SLASH': '/', 'KEY_SEMICOLON': ';', 'KEY_APOSTROPHE': "'",
            'KEY_LEFTBRACE': '[', 'KEY_RIGHTBRACE': ']', 'KEY_BACKSLASH': '\\'
        }

        self.shift_map = {
            '1': '!', '2': '@', '3': '#', '4': '$', '5': '%',
            '6': '^', '7': '&', '8': '*', '9': '(', '0': ')',
            '-': '_', '=': '+', '[': '{', ']': '}', '\\': '|',
            ';': ':', "'": '"', ',': '<', '.': '>', '/': '?'
        }

    def process_key(self, key):
        with self.lock:
            # print(self.buffer)
            # Caps Lock
            if key.keycode == 'KEY_CAPSLOCK' and key.keystate == key.key_down:
                self.caps_lock = not self.caps_lock

            # Shift
            elif key.keycode in ['KEY_LEFTSHIFT', 'KEY_RIGHTSHIFT']:
                if key.keystate == key.key_down:
                    self.shift_pressed = True
                elif key.keystate == key.key_up:
                    self.shift_pressed = False

            # Backspace
            elif key.keycode == 'KEY_BACKSPACE' and key.keystate == key.key_down:
                if self.buffer:
                    self.buffer.pop()
                    self.buffer.append('\x08')

            # ESC
            elif key.keycode == 'KEY_ESC' and key.keystate == key.key_down:
                self.buffer.append('\x1b')  # ESC código ASCII

            # Setas para cima e baixo
            elif key.keycode == 'KEY_UP' and key.keystate == key.key_down:
                self.buffer.append('\x1b[A')  # seq. escape para seta cima

            elif key.keycode == 'KEY_DOWN' and key.keystate == key.key_down:
                self.buffer.append('\x1b[B')  # seq. escape para seta baixo

            # Enter
            elif key.keycode in ['KEY_ENTER', 'KEY_KPENTER'] and key.keystate == key.key_down:
                self.buffer.append('\r')

            # Chars
            elif key.keystate == key.key_down:
                if key.keycode in self.keycode_map:
                    char = self.keycode_map[key.keycode]

                    # Aplica CapsLock e Shift
                    if char.isalpha():
                        if self.caps_lock ^ self.shift_pressed:  # XOR
                            char = char.upper()
                        else:
                            char = char.lower()
                    else:
                        if self.shift_pressed and char in self.shift_map:
                            char = self.shift_map[char]

                    self.buffer.append(char)
                    return char
        return None

    def keyboard_loop(self):
        for event in self.dev.read_loop():
            if event.type == ecodes.EV_KEY:
                key = categorize(event)
                self.process_key(key)

    def start(self):
        t = threading.Thread(target=self.keyboard_loop, daemon=True)
        t.start()

    def get_buffer(self):
        with self.lock:
            return "".join(self.buffer)

    def clear_buffer(self):
        with self.lock:
            self.buffer.clear()

    # loop com callback
    def listen(self, callback):
        """
        Recebe uma função callback que será chamada para cada caractere digitado.
        Exemplo:
            def my_callback(char):
                print("Recebido:", char)
            kb.listen(my_callback)
        """
        try:
            ultimo_buffer = ""
            while True:
                buf = self.get_buffer()
                if len(buf) > len(ultimo_buffer):
                    novos = buf[len(ultimo_buffer):]
                    for c in novos:
                        callback(c)
                    ultimo_buffer = buf
        except KeyboardInterrupt:
            print("\nKeyboard listening interrompido pelo usuário.")


# Setup
def start_keyboard(device_path):
    kb = Keyboard(device_path)
    kb.start()
    return kb
