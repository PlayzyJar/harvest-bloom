# libs/input_gpio/__init__.py
"""
Módulo de entrada GPIO para WiFi Manager.
Fornece gerenciamento de botões e teclado virtual.
"""

from .buttons import ButtonManager
from .virtual_keyboard import VirtualKeyboard

__all__ = ['ButtonManager', 'VirtualKeyboard']
