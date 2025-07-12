# bot_cientista_v1.py
from iqoptionapi.stable_api import IQ_Option
import logging
import time
import random # Importamos a biblioteca para decisões aleatórias

# Configuração básica de logging para vermos tudo no EasyPanel
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

# --- CONEXÃO ---
# Use sua nova senha!
email = "szinkamiza@gmail.com"
senha = "123lucas123" 

# Tenta conectar com um loop para resiliência
while True:
    Iq = IQ_Option(email, senha)
    Iq.connect()
    if Iq.check_connect():
        logging.info(">>> Conexão bem-sucedida! <<<")
        break
    else:
        logging.error("Falha na conexão, tentando novamente em 1 minuto...")
        time.sleep(60)

Iq.change_balance("PRACTICE") 
logging.info(f"Saldo inicial: ${Iq.get_balance()}")

# --- CONFIGURAÇÕES DO BOT CIENTISTA ---
ATIVO = "EURUSD-OTC"
VALOR_ENTRADA = 1.0 # Valor fixo para cada operação
DURACAO = 1 # Duração em minutos
INTERVALO_ENTRE_TRADES = 10 # Segundos de espera entre o fim de uma operação e o início de outra

# --- LOOP DE OPERAÇÃO AUTÔNOMA 24/7 ---
logging.info(f"--- Iniciando loop de operações autônomas para o ativo {ATIVO} ---")

while True:
    try:
        # 1. A "IA" decide a próxima ação (cara ou coroa)
        acao = random.choice(["call", "put"])
        
        logging.info("="*40)
        logging.info(f"Iniciando nova operação...")
        
        # 2. Pega o saldo ANTES
        saldo_anterior = Iq.get_balance()
        logging.info(f"Saldo ANTES: ${saldo_anterior} | Decisão da IA: {acao.upper()}")

        # 3. Envia a ordem
        check, order_id = Iq.buy(VALOR_ENTRADA, ATIVO, acao, DURACAO)

        if check:
            logging.info(f"Ordem enviada com sucesso. ID: {order_id}. Aguardando {DURACAO} min...")
            
            # 4. Espera a operação terminar
            time.sleep(DURACAO * 60 + 5) # Espera a duração + 5s de margem
            
            # 5. Pega o saldo DEPOIS
            saldo_posterior = Iq.get_balance()
            
            # 6. Audita e registra o resultado
            diferenca = round(saldo_posterior - saldo_anterior, 2)
            
            resultado_final = "EMPATE"
            if diferenca > 0:
                resultado_final = "WIN"
            elif diferenca < 0:
                resultado_final = "LOSS"

            logging.info(f"### RESULTADO ### Ativo: {ATIVO}, Ação: {acao.upper()}, Resultado: {resultado_final}, Lucro/Perda: ${diferenca}, Saldo Final: ${saldo_posterior}")

        else:
            logging.error(f"Falha ao enviar ordem para o ativo {ATIVO}.")

        # 7. Espera antes da próxima operação
        logging.info(f"Aguardando {INTERVALO_ENTRE_TRADES} segundos para o próximo ciclo.")
        logging.info("="*40 + "\n")
        time.sleep(INTERVALO_ENTRE_TRADES)

    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado no loop principal: {e}")
        logging.info("Aguardando 1 minuto antes de tentar novamente...")
        time.sleep(60)