# API/trader.py
import os
from iqoptionapi.stable_api import IQ_Option
import logging
import time

class Trader:
    def __init__(self):
        email = os.getenv("IQ_EMAIL")
        password = os.getenv("IQ_PASSWORD")
        if not email or not password:
            raise ValueError("Credenciais IQ_EMAIL e IQ_PASSWORD não definidas nas variáveis de ambiente.")
        
        logging.info("Conectando à IQ Option...")
        self.api = IQ_Option(email, password)
        self.api.connect()

        if not self.api.check_connect():
            raise ConnectionError("Falha na conexão com a IQ Option")
        
        self.api.change_balance("PRACTICE")
        logging.info(f"Conexão com IQ Option bem-sucedida. Saldo: ${self.get_saldo()}")

    def get_saldo(self):
        return self.api.get_balance()

    def get_candles(self, ativo, timeframe, quantidade):
        logging.info(f"Buscando {quantidade} velas de {ativo} (Timeframe: {timeframe}s)...")
        return self.api.get_candles(ativo, int(timeframe), int(quantidade), time.time())

    def comprar_ativo(self, ativo, valor, acao, duracao):
        logging.info(f"Executando compra: {acao.upper()} em {ativo} por ${valor}")
        check, order_id = self.api.buy(valor, ativo, acao, duracao)
        if not check:
            logging.warning("Compra como Binária falhou. Tentando como Digital...")
            check, order_id = self.api.buy_digital_spot(ativo, valor, acao, duracao)
        
        return check, order_id