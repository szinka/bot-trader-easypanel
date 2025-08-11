# API/trader.py
import logging
import os
from iqoptionapi.stable_api import IQ_Option
import time
import threading

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
        self._keepalive_thread = None
        self._keepalive_stop = threading.Event()
        self.keepalive_seconds = int(os.getenv('KEEPALIVE_SECONDS', '60') or '60')
        self.trade_locks = {}
        self._trade_locks_guard = threading.Lock()
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
                # inicia keepalive para manter conexão ativa
                self._iniciar_keepalive()
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

    def _keepalive_loop(self):
        """Mantém a conexão ativa verificando periodicamente e reconectando somente se cair."""
        if self.keepalive_seconds <= 0:
            return
        while not self._keepalive_stop.is_set():
            try:
                if self.api and not self.api.check_connect():
                    self.reconectar()
            except Exception:
                logging.debug("Falha ao checar conexão no keepalive.")
            # intervalo curto o suficiente para estabilidade, sem flood
            self._keepalive_stop.wait(self.keepalive_seconds)

    def _iniciar_keepalive(self):
        if self._keepalive_thread and self._keepalive_thread.is_alive():
            return
        self._keepalive_thread = threading.Thread(target=self._keepalive_loop, daemon=True)
        self._keepalive_thread.start()

    def _get_trade_lock(self):
        """Retorna um lock por conta (REAL/PRACTICE)."""
        key = (self.conta_atual, None)
        with self._trade_locks_guard:
            if key not in self.trade_locks:
                self.trade_locks[key] = threading.Lock()
            return self.trade_locks[key]

    def selecionar_conta(self, tipo_conta, tournament_id=None):
        """Seleciona a conta REAL ou PRACTICE na IQ Option."""
        if not self.api:
            return False
        conta = tipo_conta.upper()
        try:
            if conta == "REAL":
                self.api.change_balance("REAL")
            elif conta == "PRACTICE":
                self.api.change_balance("PRACTICE")
            else:
                logging.error(f"Tipo de conta inválido: {tipo_conta}")
                return False
            self.conta_atual = conta
            logging.info(f"Conta alterada para: {self.conta_atual}")
            return True
        except Exception as e:
            logging.error(f"Erro ao alterar conta: {e}")
            return False

    def get_saldo(self):
        """Retorna o saldo da conta selecionada."""
        if not self.api:
            return 0
        return self.api.get_balance()

    def get_candles(self, ativo, timeframe, quantidade):
        """Busca candles do ativo na conta selecionada."""
        if not self.api:
            return None
        try:
            candles = self.api.get_candles(ativo, timeframe * 60, quantidade, time.time())
            return candles
        except Exception as e:
            logging.error(f"Erro ao buscar candles: {e}")
            return None

    def comprar_ativo(self, ativo, valor, acao, duracao):
        """Executa uma ordem de compra na conta selecionada."""
        if not self.api:
            return False, None
        try:
            with self._get_trade_lock():
                logging.info(f"Executando compra: {acao.upper()} em {ativo} por ${valor}")
                # Reconecta se necessário
                if not self.api.check_connect():
                    self.reconectar()
                    if not self.api.check_connect():
                        logging.error("Conexão perdida com IQ Option e reconexão falhou.")
                        return False, None
                # Tenta BINÁRIA diretamente (removendo digital)
                logging.info("Executando trade BINÁRIA...")
                if acao.lower() == "call":
                    check, order_id = self.api.buy(valor, ativo, "call", duracao)
                else:
                    check, order_id = self.api.buy(valor, ativo, "put", duracao)
                logging.info(f"Resultado da compra BINÁRIA: {check}, Order ID: {order_id}")
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