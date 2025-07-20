
import os
import time
import logging
from dotenv import load_dotenv
from iqoptionapi.stable_api import IQ_Option

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carrega variáveis de ambiente
load_dotenv()

def test_realtime_trade_results():
    """
    Este teste demonstra como capturar o resultado de um trade em tempo real
    usando o WebSocket da IQ Option.
    """
    email = os.getenv('IQ_EMAIL')
    password = os.getenv('IQ_PASSWORD')

    if not email or not password:
        logging.error("Credenciais IQ_EMAIL e IQ_PASSWORD não encontradas no .env")
        return

    iq = IQ_Option(email, password)
    check, reason = iq.connect()

    if not check:
        logging.error(f"Falha na conexão: {reason}")
        return

    logging.info("✅ Conexão bem-sucedida!")
    iq.change_balance("PRACTICE")

    # --- Executando o Trade ---
    ativo = "EURUSD-OTC"
    valor_entrada = 1
    acao = "call"
    duracao = 1 # Minutos

    logging.info(f"Executando um trade de ${valor_entrada} em {ativo}...")
    check, order_id = iq.buy(valor_entrada, ativo, acao, duracao)

    if not check:
        logging.error("Falha ao executar o trade.")
        return

    logging.info(f"🚀 Trade enviado com sucesso! Order ID: {order_id}")
    logging.info("Aguardando o resultado do trade em tempo real...")

    # --- Capturando o Resultado ---
    # A biblioteca já lida com o WebSocket em background.
    # A função `check_win_v4` espera pelo resultado de um order_id específico.
    # Esta função é bloqueante e aguarda o resultado.
    resultado, lucro = iq.check_win_v4(order_id)

    if lucro is not None:
        logging.info(f"🎉 Resultado recebido para o Order ID {order_id}:")
        status = "Win" if lucro > 0 else "Loss" if lucro < 0 else "Empate"
        logging.info(f"   - Status: {status}")
        logging.info(f"   - Lucro/Perda: ${lucro}")
    else:
        logging.error(f"Não foi possível obter o resultado para o Order ID {order_id}. O ativo pode ter fechado ou a operação expirou sem resultado.")

if __name__ == "__main__":
    test_realtime_trade_results() 