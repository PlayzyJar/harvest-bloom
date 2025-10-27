# libs/input_gpio/buttons.py
"""
Gerenciamento de botões GPIO para navegação e entrada de dados.
Usa RPi.GPIO para detectar pressionamento de botões físicos.
"""

import RPi.GPIO as GPIO
import time
from threading import Thread, Lock


class ButtonManager:
    """
    Gerencia 4 botões GPIO com debouncing e callbacks.
    """

    # Pinos GPIO (BCM) - AJUSTE CONFORME SEU HARDWARE
    PIN_LEFT = 17      # Botão esquerda
    PIN_RIGHT = 27     # Botão direita
    PIN_SELECT = 22    # Botão selecionar/confirmar
    PIN_MODE = 23      # Botão modo/voltar

    DEBOUNCE_TIME = 0.2  # 200ms de debounce

    def __init__(self):
        """Inicializa GPIO e configura botões."""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Configura todos os pinos como INPUT com pull-up
        for pin in [self.PIN_LEFT, self.PIN_RIGHT, self.PIN_SELECT, self.PIN_MODE]:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Estado dos botões (para debouncing)
        self.last_press = {
            'left': 0,
            'right': 0,
            'select': 0,
            'mode': 0
        }

        self.lock = Lock()
        self.running = True

        # Callbacks (definidos externamente)
        self.on_left = None
        self.on_right = None
        self.on_select = None
        self.on_mode = None

        # Thread de monitoramento
        self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def _monitor_loop(self):
        """Loop de monitoramento dos botões."""
        while self.running:
            current_time = time.time()

            # Verifica cada botão
            if GPIO.input(self.PIN_LEFT) == GPIO.LOW:
                if current_time - self.last_press['left'] > self.DEBOUNCE_TIME:
                    self.last_press['left'] = current_time
                    if self.on_left:
                        self.on_left()

            if GPIO.input(self.PIN_RIGHT) == GPIO.LOW:
                if current_time - self.last_press['right'] > self.DEBOUNCE_TIME:
                    self.last_press['right'] = current_time
                    if self.on_right:
                        self.on_right()

            if GPIO.input(self.PIN_SELECT) == GPIO.LOW:
                if current_time - self.last_press['select'] > self.DEBOUNCE_TIME:
                    self.last_press['select'] = current_time
                    if self.on_select:
                        self.on_select()

            if GPIO.input(self.PIN_MODE) == GPIO.LOW:
                if current_time - self.last_press['mode'] > self.DEBOUNCE_TIME:
                    self.last_press['mode'] = current_time
                    if self.on_mode:
                        self.on_mode()

            time.sleep(0.05)  # 50ms de polling

    def set_callbacks(self, on_left=None, on_right=None, on_select=None, on_mode=None):
        """
        Define funções de callback para cada botão.

        Args:
            on_left: Função chamada ao pressionar esquerda
            on_right: Função chamada ao pressionar direita
            on_select: Função chamada ao pressionar select
            on_mode: Função chamada ao pressionar mode
        """
        with self.lock:
            if on_left:
                self.on_left = on_left
            if on_right:
                self.on_right = on_right
            if on_select:
                self.on_select = on_select
            if on_mode:
                self.on_mode = on_mode

    def cleanup(self):
        """Limpa GPIO e para monitoramento."""
        self.running = False
        self.monitor_thread.join(timeout=1.0)
        GPIO.cleanup()
