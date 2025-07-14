# bot_api.py (Versão Final com Banco de Dados)
from flask import Flask, request, jsonify
from iqoptionapi.stable_api import IQ_Option
import logging
import time
from gerenciamento import GerenciamentoTorreMK
import database # <<< IMPORTA NOSSO NOVO MÓDULO

# --- Seção 1: Configurações e Conexão ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
app = Flask(__name__)

config_gerenciamento = {
    'entry_percentage': 10.0,
    'wins_to_level_up': 5,
    'loss_compensation': 1
}

email = "szinkamiza@gmail.com"
senha = "123lucas123" 

logging.info("Iniciando Bot API...")
# Conecta ao Banco de Dados PRIMEIRO
db_conn = database.get_db_connection()
# Garante que as tabelas existam
database.setup_database(db_conn)

# Conecta à IQ Option
Iq = IQ_Option(email, senha)
Iq.connect()

if not Iq.check_connect():
    logging.error("Falha crítica na conexão com IQ Option.")
    exit()

Iq.change_balance("PRACTICE")
saldo_inicial_banca = Iq.get_balance()
logging.info(f"Conexão bem-sucedida. Saldo inicial: ${saldo_inicial_banca}")

# --- CRIA E CARREGA O ESTADO DO GERENCIADOR ---
# Tenta carregar o estado salvo do banco de dados
estado_salvo = database.carregar_estado(db_conn)
# Inicia o gerenciador com o saldo atual
gerenciador = GerenciamentoTorreMK(saldo_inicial_banca, config_gerenciamento)

# Se encontrou um estado salvo, atualiza o gerenciador
if estado_salvo:
    gerenciador.total_wins, gerenciador.level_entries = estado_salvo

logging.info(f"Gerenciador 'Torre MK' iniciado. Estado: {gerenciador.total_wins} wins. Próxima entrada: ${gerenciador.get_proxima_entrada()}")

# --- Seção 2: A Rota da API ---
@app.route('/trade', methods=['POST'])
def rota_de_trade():
    try:
        sinal_do_n8n = request.get_json()
        ativo = sinal_do_n8n['ativo']
        acao = sinal_do_n8n['acao']
        duracao = int(sinal_do_n8n['duracao'])

        saldo_anterior = Iq.get_balance()
        valor_investido = gerenciador.get_proxima_entrada()
        if valor_investido < 1: valor_investido = 1.0

        logging.info(f"Executando ordem: {acao.upper()} em {ativo} | Entrada: ${valor_investido}")
        check, order_id = Iq.buy(valor_investido, ativo, acao, duracao)

        if not check:
            return jsonify({"status": "erro", "mensagem": "Ordem rejeitada"}), 500

        time.sleep(duracao * 60 + 5)
        saldo_posterior = Iq.get_balance()
        diferenca = round(saldo_posterior - saldo_anterior, 2)
        resultado_final = "WIN" if diferenca > 0 else "LOSS"
        
        gerenciador.processar_resultado(resultado_final, saldo_posterior)
        logging.info(f"RESULTADO: {resultado_final} | Lucro/Perda: ${diferenca}")

        # --- ### LÓGICA DE BANCO DE DADOS ### ---
        # 1. Prepara os dados do trade
        trade_info = {
            'ativo': ativo, 'acao': acao, 'resultado': resultado_final, 'lucro': diferenca,
            'valor_investido': valor_investido, 'saldo_final': saldo_posterior
        }
        # 2. Salva o trade individual
        database.salvar_trade(db_conn, trade_info)

        # 3. Salva o novo estado do gerenciamento
        database.salvar_estado(db_conn, gerenciador.total_wins, gerenciador.level_entries)
        # --- ### FIM DA LÓGICA DB ### ---
        
        return jsonify({"status": "sucesso", "resultado": resultado_final, "lucro": diferenca})

    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

# --- ROTA DE DIAGNÓSTICO PARA LISTAR ATIVOS ---
@app.route('/ativos', methods=['GET'])
def listar_ativos_abertos():
    logging.info("Recebida requisição para listar ativos abertos...")
    try:
        # Pega todos os ativos abertos da IQ Option
        ativos = Iq.get_all_open_time()

        # Filtra apenas os ativos de opções binárias que estão abertos
        ativos_binarios_abertos = []
        for ativo_nome in ativos["binary"]:
            if ativos["binary"][ativo_nome]["open"]:
                ativos_binarios_abertos.append(ativo_nome)

        logging.info(f"Encontrados {len(ativos_binarios_abertos)} ativos binários abertos.")

        return jsonify({
            "status": "sucesso",
            "total_abertos": len(ativos_binarios_abertos),
            "ativos": ativos_binarios_abertos
        })

    except Exception as e:
        logging.error(f"Erro ao listar ativos: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

# --- Seção 3: Inicia o Servidor ---
if __name__ == '__main__':
    logging.info("Servidor API com persistência de dados iniciado. Aguardando na porta 80.")
    app.run(host='0.0.0.0', port=80)