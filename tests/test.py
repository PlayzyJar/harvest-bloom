from libs.keyboard.keyboard import start_keyboard
import time

# Inicializa o teclado
kb = start_keyboard('/dev/input/event0')

# ----------------------------
# Teste 1: leitura do buffer completo
# ----------------------------
print("=== Teste 1: Buffer completo ===")
print("Digite algumas letras e espere 5 segundos...")
time.sleep(5)

# Lê todo o buffer acumulado
palavra = kb.get_buffer()
print("\nPalavra lida do buffer:", palavra)

# Limpa buffer para o próximo teste
kb.clear_buffer()

# ----------------------------
# Teste 2: leitura caractere a caractere com callback
# ----------------------------
print("\n=== Teste 2: Callback por caractere ===")
print("Digite algumas letras. Pressione Ctrl+C para encerrar o teste.")

# Função callback simples que imprime cada caractere recebido


def meu_callback(char):
    print(char, end="", flush=True)


# Escuta o teclado usando a função listen da lib
kb.listen(meu_callback)
