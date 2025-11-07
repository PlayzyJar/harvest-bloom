# libs/input_gpio/buttons.py
"""
Gerenciamento de botões GPIO usando a biblioteca lgpio.
Fornece leitura com debouncing e callbacks assíncronos.
Compatível com Raspberry Pi 4/5 e sistemas modernos.
"""

import lgpio
import time
from threading import Thread, Lock


class ButtonManager:
    """
    Gerencia 4 botões físicos conectados aos pinos GPIO.
    Usa lgpio para leitura com debouncing via polling.
    """

    # Pinos GPIO (BCM) — ajuste conforme o hardware real
    PIN_LEFT = 17
    PIN_RIGHT = 27
    PIN_SELECT = 22
    PIN_MODE = 23

    DEBOUNCE_TIME = 0.2  # 200ms

    def __init__(self):
        """Inicializa GPIO, configura pinos e inicia monitoramento."""
        self.chip = lgpio.gpiochip_open(0)  # geralmente chip 0 no RPi

        # Configura todos os pinos como entrada com pull-up
        for pin in [self.PIN_LEFT, self.PIN_RIGHT, self.PIN_SELECT, self.PIN_MODE]:
            lgpio.gpio_claim_input(self.chip, pin, lgpio.SET_PULL_UP)

        self.last_press = {
            "left": 0,
            "right": 0,
            "select": 0,
            "mode": 0
        }

        self.callbacks = {
            "left": None,
            "right": None,
            "select": None,
            "mode": None
        }

        self.lock = Lock()
        self.running = True

        # Thread de monitoramento
        self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def _monitor_loop(self):
        """Loop que monitora os botões e dispara callbacks."""
        while self.running:
            current_time = time.time()

            # Leitura de todos os botões
            buttons = {
                "left": lgpio.gpio_read(self.chip, self.PIN_LEFT),
                "right": lgpio.gpio_read(self.chip, self.PIN_RIGHT),
                "select": lgpio.gpio_read(self.chip, self.PIN_SELECT),
                "mode": lgpio.gpio_read(self.chip, self.PIN_MODE),
            }

            for name, value in buttons.items():
                if value == 0:  # ativo em nível baixo
                    if current_time - self.last_press[name] > self.DEBOUNCE_TIME:
                        self.last_press[name] = current_time
                        callback = self.callbacks[name]
                        if callback:
                            callback()

            time.sleep(0.05)  # 50ms de polling

    def set_callbacks(self, on_left=None, on_right=None, on_select=None, on_mode=None):
        """
        Define funções de callback para cada botão.

        Args:
            on_left: função chamada ao pressionar 'left'
            on_right: função chamada ao pressionar 'right'
            on_select: função chamada ao pressionar 'select'
            on_mode: função chamada ao pressionar 'mode'
        """
        with self.lock:
            if on_left:
                self.callbacks["left"] = on_left
            if on_right:
                self.callbacks["right"] = on_right
            if on_select:
                self.callbacks["select"] = on_select
            if on_mode:
                self.callbacks["mode"] = on_mode

    def cleanup(self):
        """Encerra monitoramento e libera recursos GPIO."""
        self.running = False
        self.monitor_thread.join(timeout=1.0)
        lgpio.gpiochip_close(self.chip)
