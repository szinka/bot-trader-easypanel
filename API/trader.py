# API/trader.py
import logging
import os
from iqoptionapi.stable_api import IQ_Option
import time

# Lock global para evitar múltiplos logins
IQ_LOGIN_ATTEMPTED = False
IQ_LOGIN_SUCCESS = False
IQ_LOGIN_ERROR = None

class Trader:
    """
    Classe responsável por toda a comunicação com a IQ Option.
    Garante seleção de conta, execução de trades, consulta de saldo e candles.
    """
    def __init__(self):
        global IQ_LOGIN_ATTEMPTED, IQ_LOGIN_SUCCESS, IQ_LOGIN_ERROR
        self.api = None
        self.conta_atual = None
        email = os.getenv('IQ_EMAIL')
        senha = os.getenv('IQ_PASSWORD')
        if not email or not senha:
            logging.critical("Credenciais IQ Option não configuradas no EasyPanel!")
            return
        if IQ_LOGIN_ATTEMPTED:
            if IQ_LOGIN_SUCCESS:
                logging.info("Login na IQ Option já realizado por outro processo.")
            else:
                logging.critical(f"Login na IQ Option já falhou anteriormente: {IQ_LOGIN_ERROR}")
            return
        IQ_LOGIN_ATTEMPTED = True
        try:
            self.conectar_iq_option(email, senha)
            IQ_LOGIN_SUCCESS = True
        except Exception as e:
            IQ_LOGIN_ERROR = str(e)
            print("\n❌ Erro ao conectar na IQ Option:", IQ_LOGIN_ERROR)
            print("Dica: Verifique se não há múltiplos processos rodando, se você não atingiu o limite de requisições, ou se as credenciais estão corretas. Aguarde alguns minutos e tente novamente.\n")
            logging.critical(f"ERRO CRÍTICO DURANTE A INICIALIZAÇÃO: {IQ_LOGIN_ERROR}")
            raise

    def conectar_iq_option(self, email, senha):
        logging.info(f"Conectando à IQ Option com email: {email}")
        try:
            self.api = IQ_Option(email, senha)
            check, reason = self.api.connect()
            if check:
                logging.info("Conexão com IQ Option bem-sucedida.")
                self.api.change_balance("PRACTICE")
                saldo = self.api.get_balance()
                logging.info(f"Saldo inicial (PRACTICE): ${saldo}")
            else:
                logging.critical(f"Falha na conexão com IQ Option: {reason}")
        except Exception as e:
            logging.critical(f"ERRO CRÍTICO DURANTE A INICIALIZAÇÃO: {e}")

    def reconectar(self):
        """Tenta reconectar automaticamente se a conexão cair."""
        if self.api:
            logging.warning("Reconectando à IQ Option...")
            check, reason = self.api.connect()
            if check:
                logging.info("Reconexão bem-sucedida.")
                if self.conta_atual:
                    self.api.change_balance(self.conta_atual)
            else:
                logging.critical(f"Falha na reconexão: {reason}")

    def selecionar_conta(self, tipo_conta):
        """Seleciona a conta REAL ou PRACTICE na IQ Option."""
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
        """Retorna o saldo da conta selecionada."""
        if not self.api:
            return 0
        return self.api.get_balance()

    def get_candles(self, ativo, timeframe, quantidade):
        """Busca candles do ativo na conta selecionada com volume."""
        if not self.api:
            return None
        try:
            candles = self.api.get_candles(ativo, timeframe * 60, quantidade, time.time())
            
            # Processa os candles para garantir que o volume seja incluído
            processed_candles = []
            for candle in candles:
                processed_candle = {
                    'from': candle.get('from', 0),
                    'open': candle.get('open', 0),
                    'high': candle.get('high', 0),
                    'low': candle.get('low', 0),
                    'close': candle.get('close', 0),
                    'volume': candle.get('volume', 0)  # Garante que volume seja incluído
                }
                processed_candles.append(processed_candle)
            
            logging.info(f"Retornando {len(processed_candles)} candles para {ativo} com volume")
            return processed_candles
        except Exception as e:
            logging.error(f"Erro ao buscar candles: {e}")
            return None

    def comprar_ativo(self, ativo, valor, acao, duracao):
        """Executa uma ordem de compra na conta selecionada."""
        if not self.api:
            return False, None
        try:
            logging.info(f"Executando compra: {acao.upper()} em {ativo} por ${valor}")
            # Reconecta se necessário
            if not self.api.check_connect():
                self.reconectar()
                if not self.api.check_connect():
                    logging.error("Conexão perdida com IQ Option e reconexão falhou.")
                    return False, None
            if acao.lower() == "call":
                check, order_id = self.api.buy(valor, ativo, "call", duracao)
            else:
                check, order_id = self.api.buy(valor, ativo, "put", duracao)
            logging.info(f"Resultado da compra: {check}, Order ID: {order_id}")
            return check, order_id
        except Exception as e:
            logging.error(f"Erro na compra: {e}")
            return False, None

    def get_moeda_conta(self):
        """Retorna a moeda da conta selecionada (ex: BRL, USD, EUR)."""
        if not self.api:
            return None
        try:
            profile = self.api.get_profile_ansyc()
            if profile and 'currency' in profile:
                return profile['currency']
            return None
        except Exception as e:
            logging.error(f"Erro ao obter moeda da conta: {e}")
            return None