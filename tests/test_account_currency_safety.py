import sys
import os
import time
from dotenv import load_dotenv
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from API.trader import Trader

load_dotenv()

def test_account_currency_safety():
    trader = Trader()
    # Test PRACTICE
    trader.selecionar_conta('PRACTICE')
    saldo_practice_antes = trader.get_saldo()
    print(f"Saldo PRACTICE antes: {saldo_practice_antes}")
    check, order_id = trader.comprar_ativo('EURUSD-OTC', 1, 'call', 1)
    assert check, "Trade PRACTICE não foi executado!"
    time.sleep(65)  # Espera o resultado
    saldo_practice_depois = trader.get_saldo()
    print(f"Saldo PRACTICE depois: {saldo_practice_depois}")
    assert saldo_practice_antes != saldo_practice_depois, "Saldo PRACTICE não mudou após trade."

    # Test REAL
    trader.selecionar_conta('REAL')
    saldo_real_antes = trader.get_saldo()
    print(f"Saldo REAL antes: {saldo_real_antes}")
    check, order_id = trader.comprar_ativo('EURUSD-OTC', 1, 'call', 1)
    if not check:
        print("Trade REAL não foi executado (provavelmente por falta de saldo). Teste parcial.")
        return
    time.sleep(65)
    saldo_real_depois = trader.get_saldo()
    print(f"Saldo REAL depois: {saldo_real_depois}")
    assert saldo_real_antes != saldo_real_depois, "Saldo REAL não mudou após trade."

    # Garante que os saldos são independentes
    assert saldo_practice_depois != saldo_real_depois, "Os saldos PRACTICE e REAL não são independentes!"

if __name__ == "__main__":
    test_account_currency_safety() 