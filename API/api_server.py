# API/api_server.py
from flask import Flask, request, jsonify
import logging
import os
import time
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env (para desenvolvimento local)
load_dotenv()

# Importa as classes e módulos da sua nova estrutura
# O ponto (.) indica que estamos a importar da mesma pasta (do pacote API)
from .trader import Trader
from .gerenciamento import GerenciamentoTorreMK
from . import database

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# --- Inicialização dos Componentes ---
# Garante que os componentes só sejam inicializados uma vez.
try:
    trader = Trader()
    db_conn = database.get_db_connection()
    database.setup_database(db_conn)

    config_gerenciamento = {
        'entry_percentage': float(os.getenv('ENTRY_PERCENTAGE', 5.0)),
        'wins_to_level_up': int(os.getenv('WINS_TO_LEVEL_UP', 5)),
        'loss_compensation': int(os.getenv('LOSS_COMPENSATION', 1))
    }
    gerenciador = GerenciamentoTorreMK(trader.get_saldo(), config_gerenciamento)

    estado_salvo = database.carregar_estado(db_conn)
    if estado_salvo:
        gerenciador.total_wins, gerenciador.level_entries = estado_salvo
    logging.info("Gerenciador 'Torre MK' iniciado com as configurações do ambiente.")

except Exception as e:
    logging.critical(f"ERRO CRÍTICO DURANTE A INICIALIZAÇÃO: {e}")
    # Se a inicialização falhar, a aplicação não deve subir.
    # Em um ambiente real, o Docker tentaria reiniciar o container.
    exit()

# --- Endpoints da API ---
@app.route('/get_saldo', methods=['GET'])
def rota_get_saldo():
    try:
        return jsonify({"status": "sucesso", "saldo": trader.get_saldo()})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/get_candles', methods=['POST'])
def rota_get_candles():
    try:
        dados = request.get_json()
        velas = trader.get_candles(dados['ativo'], dados['timeframe'], dados['quantidade'])
        if not velas:
            return jsonify({"status": "erro", "mensagem": "Não foi possível buscar velas"}), 404
        return jsonify({"status": "sucesso", "velas": velas})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/trade', methods=['POST'])
def rota_de_trade():
    try:
        sinal = request.get_json()
        saldo_anterior = trader.get_saldo()
        valor_investido = gerenciador.get_proxima_entrada()

        check, order_id = trader.comprar_ativo(
            sinal['ativo'], valor_investido, sinal['acao'], int(sinal['duracao'])
        )
        if not check:
            return jsonify({"status": "erro", "mensagem": "Ordem rejeitada em Binária e Digital"}), 500

        time.sleep(int(sinal['duracao']) * 60 + 5)
        saldo_posterior = trader.get_saldo()
        diferenca = round(saldo_posterior - saldo_anterior, 2)
        resultado = "WIN" if diferenca > 0 else "LOSS"
        
        gerenciador.processar_resultado(resultado, saldo_posterior)
        trade_info = {'ativo': sinal['ativo'], 'acao': sinal['acao'], 'resultado': resultado, 'lucro': diferenca, 'valor_investido': valor_investido, 'saldo_final': saldo_posterior}
        database.salvar_trade(db_conn, trade_info)
        database.salvar_estado(db_conn, gerenciador.total_wins, gerenciador.level_entries)

        return jsonify({"status": "sucesso", "resultado": resultado, "lucro": diferenca})
    except Exception as e:
        logging.error(f"Erro na rota /trade: {e}", exc_info=True)
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/ping', methods=['GET'])
def rota_de_ping():
    """Uma rota de teste extremamente simples para verificar se o servidor está no ar e o código atualizado."""
    return jsonify({"status": "sucesso", "mensagem": "pong"})