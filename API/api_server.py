# API/api_server.py
from flask import Flask, request, jsonify
import logging
import os
import time
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env (para desenvolvimento local)
load_dotenv()

# Importa as classes e módulos da sua nova estrutura
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
    # Inicializa o gerenciador com o saldo da conta de prática
    gerenciador = GerenciamentoTorreMK(trader.get_saldo(), config_gerenciamento)

    estado_salvo = database.carregar_estado(db_conn)
    if estado_salvo:
        gerenciador.total_wins, gerenciador.level_entries = estado_salvo
    logging.info("Gerenciador 'Torre MK' iniciado com as configurações do ambiente.")

except Exception as e:
    logging.critical(f"ERRO CRÍTICO DURANTE A INICIALIZAÇÃO: {e}")
    exit()

# --- Endpoints da API ---
@app.route('/get_saldo', methods=['GET'])
def rota_get_saldo():
    try:
        # Permite verificar o saldo da conta especificada (PRACTICE por padrão)
        tipo_conta = request.args.get('tipo_conta', 'PRACTICE')
        trader.selecionar_conta(tipo_conta)
        return jsonify({"status": "sucesso", "saldo": trader.get_saldo(), "conta": tipo_conta.upper()})
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
        
        # --- Novas opções ---
        tipo_conta = sinal.get('tipo_conta', 'PRACTICE')
        valor_entrada_req = sinal.get('valor_entrada', 'gen')

        # Seleciona a conta antes de qualquer outra ação
        trader.selecionar_conta(tipo_conta)
        
        saldo_anterior = trader.get_saldo()
        
        # Define o valor do investimento
        if isinstance(valor_entrada_req, (int, float)):
            valor_investido = float(valor_entrada_req)
        elif valor_entrada_req == 'gen':
            valor_investido = gerenciador.get_proxima_entrada()
        else:
            return jsonify({"status": "erro", "mensagem": "Valor de entrada inválido."}), 400

        check, order_id = trader.comprar_ativo(
            sinal['ativo'], valor_investido, sinal['acao'], int(sinal['duracao'])
        )
        if not check:
            return jsonify({"status": "erro", "mensagem": "Ordem rejeitada em Binária e Digital"}), 500

        # Aguarda o resultado da operação
        time.sleep(int(sinal['duracao']) * 60 + 5) 
        
        saldo_posterior = trader.get_saldo()
        diferenca = round(saldo_posterior - saldo_anterior, 2)
        resultado = "WIN" if diferenca > 0 else "LOSS"
        
        # Processa o resultado apenas se a entrada foi gerenciada
        if valor_entrada_req == 'gen':
            gerenciador.processar_resultado(resultado, saldo_posterior)
            database.salvar_estado(db_conn, gerenciador.total_wins, gerenciador.level_entries)

        trade_info = {
            'ativo': sinal['ativo'], 
            'acao': sinal['acao'], 
            'resultado': resultado, 
            'lucro': diferenca, 
            'valor_investido': valor_investido, 
            'saldo_final': saldo_posterior
        }
        database.salvar_trade(db_conn, trade_info)

        return jsonify({"status": "sucesso", "resultado": resultado, "lucro": diferenca})
    except Exception as e:
        logging.error(f"Erro na rota /trade: {e}", exc_info=True)
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/get_historico_trades', methods=['GET'])
def rota_get_historico():
    """Endpoint para buscar o histórico de todos os trades."""
    try:
        historico = database.get_historico_trades(db_conn)
        # Converte campos NUMERIC para float para serialização JSON
        for trade in historico:
            for key, value in trade.items():
                if isinstance(value, decimal.Decimal):
                    trade[key] = float(value)
        return jsonify({"status": "sucesso", "historico": historico})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/resetar_historico', methods=['POST'])
def rota_resetar_historico():
    """Endpoint para limpar o histórico de trades e o estado do gerenciamento."""
    try:
        # Limpa as tabelas
        database.resetar_historico_trades(db_conn)
        database.resetar_estado_gerenciamento(db_conn)
        
        # Reinicia o objeto gerenciador na memória
        banca_inicial = trader.get_saldo() # Pega o saldo atual para reiniciar
        gerenciador.__init__(banca_inicial, config_gerenciamento)
        
        logging.info("Histórico e estado de gerenciamento foram resetados com sucesso.")
        return jsonify({"status": "sucesso", "mensagem": "Histórico e estado de gerenciamento resetados."})
    except Exception as e:
        logging.error(f"Erro ao resetar o histórico: {e}", exc_info=True)
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/ping', methods=['GET'])
def rota_de_ping():
    """Uma rota de teste para verificar se o servidor está no ar."""
    return jsonify({"status": "sucesso", "mensagem": "pong"})

# Adiciona importação para lidar com tipo Decimal do banco de dados
import decimal