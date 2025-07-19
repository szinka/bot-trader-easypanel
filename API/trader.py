# API/trader.py
import logging
import os
from iqoptionapi.api import IQOptionAPI as IQ_Option
import time

class Trader:
    def __init__(self):
        self.api = None
        self.conta_atual = None
        
        # Carrega credenciais do EasyPanel
        email = os.getenv('IQ_EMAIL')
        senha = os.getenv('IQ_PASSWORD')
        
        if not email or not senha:
            logging.critical("Credenciais IQ Option não configuradas no EasyPanel!")
            return
            
        self.conectar_iq_option(email, senha)
    
    def conectar_iq_option(self, email, senha):
        logging.info("Conectando à IQ Option...")
        try:
            self.api = IQ_Option(email, senha)
            
            # Conecta à API
            check, reason = self.api.connect()
            if check:
                logging.info("Conexão com IQ Option bem-sucedida.")
                # Muda para conta de prática
                self.api.change_balance("PRACTICE")
                saldo = self.api.get_balance()
                logging.info(f"Saldo inicial (PRACTICE): ${saldo}")
            else:
                logging.critical(f"Falha na conexão com IQ Option: {reason}")
        except Exception as e:
            logging.critical(f"ERRO CRÍTICO DURANTE A INICIALIZAÇÃO: {e}")
    
    def selecionar_conta(self, tipo_conta):
        if not self.api:
            return False
            
        if tipo_conta.upper() == "REAL":
            self.api.change_balance("REAL")
        else:
            self.api.change_balance("PRACTICE")
            
        self.conta_atual = tipo_conta.upper()
        logging.info(f"Conta alterada para: {self.conta_atual}")
        return True
    
    def get_saldo(self):
        if not self.api:
            return 0
        return self.api.get_balance()
    
    def get_candles(self, ativo, timeframe, quantidade):
        if not self.api:
            return None
            
        try:
            candles = self.api.get_candles(ativo, timeframe * 60, quantidade, time.time())
            return candles
        except Exception as e:
            logging.error(f"Erro ao buscar candles: {e}")
            return None
    
    def comprar_ativo(self, ativo, valor, acao, duracao):
        if not self.api:
            return False, None
            
        try:
            logging.info(f"Executando compra: {acao.upper()} em {ativo} por ${valor}")
            
            if acao.lower() == "call":
                check, order_id = self.api.buy(valor, ativo, "call", duracao)
            else:
                check, order_id = self.api.buy(valor, ativo, "put", duracao)
                
            return check, order_id
        except Exception as e:
            logging.error(f"Erro na compra: {e}")
            return False, None