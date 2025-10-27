# utils/wifi_utils.py
"""
Funções utilitárias para gerenciar conexões Wi-Fi usando nmcli.
Fornece scan de redes, verificação de conexões conhecidas e conexão a redes.
"""

import subprocess
import time


def scan_wifi_networks():
    """
    Escaneia redes Wi-Fi disponíveis.

    Retorna:
        list: Lista de SSIDs disponíveis (strings)
    """
    try:
        # Força um rescan para garantir lista atualizada
        subprocess.run(["sudo", "nmcli", "dev", "wifi", "rescan"],
                       check=False, timeout=10)
        time.sleep(2)  # Aguarda conclusão do scan

        output = subprocess.check_output(
            ["sudo", "nmcli", "-t", "-f", "SSID", "device", "wifi", "list"],
            text=True
        )

        redes = []
        ja_viu = set()

        for linha in output.strip().split('\n'):
            ssid = linha.strip()
            # Evita duplicatas e SSIDs vazios
            if ssid and ssid not in ja_viu:
                redes.append(ssid)
                ja_viu.add(ssid)

        return redes
    except Exception as e:
        print(f"Erro ao escanear redes: {e}")
        return []


def get_known_wifi_ssids():
    """
    Obtém lista de redes Wi-Fi já conhecidas (salvas no sistema).

    Retorna:
        list: Lista de SSIDs salvos (strings)
    """
    try:
        output = subprocess.check_output(
            ["nmcli", "-t", "-f", "NAME", "connection", "show"],
            text=True
        )

        ssids = []
        for line in output.strip().split("\n"):
            ssid = line.strip()
            if ssid:
                ssids.append(ssid)

        return ssids
    except Exception as e:
        print(f"Erro ao obter redes conhecidas: {e}")
        return []


def connect_to_wifi(ssid, senha=None):
    """
    Conecta a uma rede Wi-Fi.

    Se a rede for conhecida, ativa a conexão salva.
    Se for nova, conecta com a senha fornecida e salva a configuração.

    Args:
        ssid (str): Nome da rede
        senha (str, optional): Senha da rede (obrigatório para redes novas)

    Retorna:
        tuple: (sucesso: bool, mensagem: str)
    """
    known_ssids = get_known_wifi_ssids()

    try:
        if ssid in known_ssids:
            # Rede já conhecida: ativa conexão salva
            result = subprocess.run(
                ["sudo", "nmcli", "connection", "up", ssid],
                capture_output=True,
                text=True,
                timeout=30
            )
        else:
            # Rede nova: conecta e salva config
            if not senha:
                return False, "Senha obrigatória para rede nova"

            result = subprocess.run(
                ["sudo", "nmcli", "device", "wifi", "connect", ssid,
                 "password", senha],
                capture_output=True,
                text=True,
                timeout=60
            )

        if result.returncode == 0:
            return True, "Conectado com sucesso"
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            return False, error_msg[:40]  # Limita tamanho da mensagem

    except subprocess.TimeoutExpired:
        return False, "Timeout na conexão"
    except Exception as e:
        return False, str(e)[:40]


def is_connected_to_network(ssid=None):
    """
    Verifica se está conectado a uma rede (ou a uma específica).

    Args:
        ssid (str, optional): Se fornecido, verifica se está conectado a essa rede

    Retorna:
        bool: True se conectado, False caso contrário
    """
    try:
        result = subprocess.check_output(
            ["nmcli", "-t", "-f", "STATE", "general"],
            text=True
        )

        if "connected" in result.lower():
            if ssid:
                # Verifica se está conectado a esse SSID específico
                active = subprocess.check_output(
                    ["iwgetid", "-r"],
                    text=True
                ).strip()
                return active == ssid
            return True
        return False
    except Exception:
        return False
