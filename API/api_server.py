# API/api_server.py
from flask import Flask, request, jsonify
import logging
import os
import time
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Importa os módulos essenciais
from .trader import Trader
from .gerenciamento import GerenciadorMultiConta
from . import database

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# --- Inicialização dos Componentes ---
try:
    trader = Trader()
    db_conn = database.get_db_connection()
    database.setup_database(db_conn)

    config_gerenciamento = {
        'entry_percentage': float(os.getenv('ENTRY_PERCENTAGE', 5.0)),
        'wins_to_level_up': int(os.getenv('WINS_TO_LEVEL_UP', 5)),
        'loss_compensation': int(os.getenv('LOSS_COMPENSATION', 1))
    }
    
    # Log das configurações carregadas
    logging.info(f"Configurações carregadas:")
    logging.info(f"  - ENTRY_PERCENTAGE: {os.getenv('ENTRY_PERCENTAGE', 5.0)}%")
    logging.info(f"  - GERENCIAMENTO_PERCENT: {os.getenv('GERENCIAMENTO_PERCENT', 10.0)}%")
    logging.info(f"  - WINS_TO_LEVEL_UP: {os.getenv('WINS_TO_LEVEL_UP', 5)}")
    logging.info(f"  - LOSS_COMPENSATION: {os.getenv('LOSS_COMPENSATION', 1)}")
    
    # Inicializa o gerenciador multi-conta
    gerenciador_multi = GerenciadorMultiConta(config_gerenciamento)
    gerenciador_multi.set_db_connection(db_conn)
    
    logging.info("Bot Trader iniciado com sucesso!")

except Exception as e:
    logging.critical(f"ERRO CRÍTICO DURANTE A INICIALIZAÇÃO: {e}")
    exit()

# --- Endpoints Essenciais ---
@app.route('/get_saldo', methods=['GET'])
def rota_get_saldo():
    """Consulta saldo da conta."""
    try:
        tipo_conta = request.args.get('tipo_conta', 'PRACTICE')
        trader.selecionar_conta(tipo_conta)
        saldo = trader.get_saldo()
        
        return jsonify({
            "status": "sucesso", 
            "saldo": saldo, 
            "conta": tipo_conta.upper()
        })
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/get_candles', methods=['POST'])
def rota_get_candles():
    """Busca candles de um ativo."""
    try:
        dados = request.get_json()
        
        # Validações básicas
        if not dados or 'ativo' not in dados or 'timeframe' not in dados or 'quantidade' not in dados:
            return jsonify({"status": "erro", "mensagem": "Campos obrigatórios: ativo, timeframe, quantidade"}), 400
        
        velas = trader.get_candles(dados['ativo'], dados['timeframe'], dados['quantidade'])
        
        if not velas:
            return jsonify({"status": "erro", "mensagem": "Não foi possível buscar velas"}), 404
        
        return jsonify({
            "status": "sucesso", 
            "velas": velas
        })
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/trade', methods=['POST'])
def rota_de_trade():
    """Executa uma operação de trade."""
    try:
        sinal = request.get_json()
        
        # Validações básicas
        if not sinal or 'ativo' not in sinal or 'acao' not in sinal or 'duracao' not in sinal:
            return jsonify({"status": "erro", "mensagem": "Campos obrigatórios: ativo, acao, duracao"}), 400
        
        tipo_conta = sinal.get('tipo_conta', 'PRACTICE')
        valor_entrada_req = sinal.get('valor_entrada', 'gen')

        # Seleciona a conta
        trader.selecionar_conta(tipo_conta)
        saldo_anterior = trader.get_saldo()
        
        # Define valor do investimento
        if isinstance(valor_entrada_req, (int, float)):
            valor_investido = float(valor_entrada_req)
            
            # Validação de 10% da banca para valores manuais
            if valor_investido > saldo_anterior * 0.10:
                return jsonify({
                    "status": "erro", 
                    "mensagem": f"Valor de entrada ({valor_investido}) excede 10% da banca ({saldo_anterior * 0.10:.2f})"
                }), 400
                
        elif valor_entrada_req == 'gen':
            valor_investido = gerenciador_multi.get_proxima_entrada(tipo_conta, saldo_anterior)
        else:
            return jsonify({"status": "erro", "mensagem": "Valor de entrada inválido."}), 400

        # Executa a ordem
        check, order_id = trader.comprar_ativo(
            sinal['ativo'], valor_investido, sinal['acao'], int(sinal['duracao'])
        )
        
        if not check:
            return jsonify({"status": "erro", "mensagem": "Ordem rejeitada em Binária e Digital"}), 500

        # Aguarda resultado
        time.sleep(int(sinal['duracao']) * 60 + 5) 
        
        saldo_posterior = trader.get_saldo()
        diferenca = round(saldo_posterior - saldo_anterior, 2)
        resultado = "WIN" if diferenca > 0 else "LOSS"
        
        # Processa resultado se gerenciado
        if valor_entrada_req == 'gen':
            gerenciador_multi.processar_resultado(tipo_conta, resultado, saldo_posterior)

        # Salva trade
        trade_info = {
            'tipo_conta': tipo_conta,
            'ativo': sinal['ativo'], 
            'acao': sinal['acao'], 
            'resultado': resultado, 
            'lucro': diferenca, 
            'valor_investido': valor_investido, 
            'saldo_final': saldo_posterior
        }
        database.salvar_trade(db_conn, trade_info)

        return jsonify({
            "status": "sucesso", 
            "resultado": resultado, 
            "lucro": diferenca
        })
    except Exception as e:
        logging.error(f"Erro na rota /trade: {e}", exc_info=True)
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/get_historico_trades', methods=['GET'])
def rota_get_historico():
    """Busca histórico de trades."""
    try:
        tipo_conta = request.args.get('tipo_conta', None)
        historico = database.get_historico_trades(db_conn, tipo_conta)
        
        # Converte campos NUMERIC para float
        for trade in historico:
            for key, value in trade.items():
                if isinstance(value, decimal.Decimal):
                    trade[key] = float(value)
        
        return jsonify({
            "status": "sucesso", 
            "historico": historico
        })
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/get_estado_gerenciador', methods=['GET'])
def rota_get_estado_gerenciador():
    """Consulta estado do gerenciador."""
    try:
        tipo_conta = request.args.get('tipo_conta', 'PRACTICE')
        estado = gerenciador_multi.get_estado_gerenciador(tipo_conta)
        
        if estado:
            return jsonify({"status": "sucesso", "estado": estado})
        else:
            return jsonify({"status": "erro", "mensagem": f"Gerenciador não encontrado para {tipo_conta}"}), 404
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/resetar_historico', methods=['POST'])
def rota_resetar_historico():
    """Reseta histórico de trades."""
    try:
        dados = request.get_json() or {}
        tipo_conta = dados.get('tipo_conta', None)
        
        # Limpa tabelas
        database.resetar_historico_trades(db_conn, tipo_conta)
        database.resetar_estado_gerenciamento(db_conn, tipo_conta)
        
        # Reinicia gerenciadores
        if tipo_conta:
            trader.selecionar_conta(tipo_conta)
            banca_atual = trader.get_saldo()
            gerenciador_multi.resetar_gerenciador(tipo_conta, banca_atual)
        else:
            for conta in ['REAL', 'PRACTICE']:
                try:
                    trader.selecionar_conta(conta)
                    banca_atual = trader.get_saldo()
                    gerenciador_multi.resetar_gerenciador(conta, banca_atual)
                except Exception as e:
                    logging.warning(f"Não foi possível resetar gerenciador para {conta}: {e}")
        
        mensagem = f"Histórico resetado para {tipo_conta if tipo_conta else 'todas as contas'}."
        return jsonify({"status": "sucesso", "mensagem": mensagem})
    except Exception as e:
        logging.error(f"Erro ao resetar histórico: {e}", exc_info=True)
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/ping', methods=['GET'])
def rota_de_ping():
    """Teste de conectividade."""
    return jsonify({
        "status": "sucesso", 
        "mensagem": "pong"
    })

# Importação para Decimal
import decimal

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=False)