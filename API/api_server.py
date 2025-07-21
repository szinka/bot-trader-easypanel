# API/api_server.py
from flask import Flask, request, jsonify
import logging
import os
import time
import decimal
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Importa os módulos essenciais
from API.trader import Trader
from API.gerenciamento import GerenciadorMultiConta
import API.database as database

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
    logging.info(f"  - GERENCIAMENTO_PERCENT: {os.getenv('GERENCIAMENTO_PERCENT', 5.0)}%")
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
@app.route('/profile', methods=['GET'])
def rota_get_profile():
    """Retorna a moeda da conta selecionada."""
    try:
        tipo_conta = request.args.get('tipo_conta', 'PRACTICE')
        trader.selecionar_conta(tipo_conta)
        moeda = trader.get_moeda_conta()
        return jsonify({
            "status": "sucesso",
            "conta": tipo_conta.upper(),
            "moeda": moeda
        })
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/balance', methods=['GET'])
def rota_get_saldo():
    """Consulta saldo da conta."""
    try:
        tipo_conta = request.args.get('tipo_conta', 'PRACTICE')
        trader.selecionar_conta(tipo_conta)
        moeda = trader.get_moeda_conta()
        saldo = trader.get_saldo()
        logging.info(f"Consulta de saldo para conta {tipo_conta} ({moeda})")
        
        return jsonify({
            "status": "sucesso", 
            "saldo": saldo, 
            "conta": tipo_conta.upper(),
            "moeda": moeda,
            "mensagem": f"Saldo atual na conta {tipo_conta.upper()}: {moeda} {saldo}"
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
        if not sinal or 'ativo' not in sinal or ('acao' not in sinal and 'call' not in sinal and 'put' not in sinal) or 'duracao' not in sinal:
            return jsonify({"status": "erro", "mensagem": "Campos obrigatórios: ativo, acao/call/put, duracao"}), 400
        
        tipo_conta = sinal.get('tipo_conta', 'PRACTICE')
        valor_entrada_req = sinal.get('valor_entrada', 'gen')

        # Seleciona a conta
        trader.selecionar_conta(tipo_conta)
        moeda = trader.get_moeda_conta()
        saldo_anterior = trader.get_saldo()
        logging.info(f"Iniciando trade na conta {tipo_conta} ({moeda}) com saldo de {saldo_anterior}")
        
        # Validação de saldo
        if saldo_anterior <= 0:
            return jsonify({
                "status": "erro", 
                "mensagem": f"Saldo insuficiente na conta {tipo_conta}. Saldo atual: {moeda} {saldo_anterior}"
            }), 400
        
        # Define valor do investimento
        if isinstance(valor_entrada_req, (int, float)):
            valor_investido = float(valor_entrada_req)
            
            # Validação de 5% da banca para valores manuais
            if valor_investido > saldo_anterior * 0.05:
                return jsonify({
                    "status": "erro", 
                    "mensagem": f"Valor de entrada ({valor_investido}) excede 5% da banca ({saldo_anterior * 0.05:.2f})"
                }), 400
                
        elif valor_entrada_req == 'gen':
            valor_investido = gerenciador_multi.get_proxima_entrada(tipo_conta, saldo_anterior)
        else:
            return jsonify({"status": "erro", "mensagem": "Valor de entrada inválido."}), 400

        # Determina a ação (call/put)
        acao = sinal.get('acao', sinal.get('call', sinal.get('put')))
        if acao not in ['call', 'put']:
            return jsonify({"status": "erro", "mensagem": "Ação deve ser 'call' ou 'put'"}), 400
        
        # Executa a ordem
        check, order_id = trader.comprar_ativo(
            sinal['ativo'], valor_investido, acao, int(sinal['duracao'])
        )
        
        if not check:
            return jsonify({"status": "erro", "mensagem": "Ordem rejeitada em Binária e Digital"}), 500

        # Retorna resposta instantânea com informações do trade
        return jsonify({
            "status": "sucesso",
            "mensagem": "Trade executado com sucesso!",
            "trade_info": {
                "ativo": sinal['ativo'],
                "acao": acao,
                "duracao": sinal['duracao'],
                "tipo_conta": tipo_conta,
                "valor_investido": valor_investido,
                "saldo_anterior": saldo_anterior,
                "order_id": order_id
            },
            "saldo_atual": saldo_anterior,
            "conta": tipo_conta.upper()
        })
    except Exception as e:
        logging.error(f"Erro na rota /trade: {e}", exc_info=True)
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/get_historico_trades', methods=['GET'])
@app.route('/history', methods=['GET'])
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
@app.route('/management', methods=['GET'])
def rota_get_estado_gerenciador():
    """Consulta estado do gerenciador."""
    try:
        tipo_conta = request.args.get('tipo_conta', 'PRACTICE')
        
        # Inicializa o gerenciador se não existir
        trader.selecionar_conta(tipo_conta)
        banca_atual = trader.get_saldo()
        gerenciador_multi.get_proxima_entrada(tipo_conta, banca_atual)  # Isso cria o gerenciador
        
        estado = gerenciador_multi.get_estado_gerenciador(tipo_conta)
        
        if estado:
            return jsonify({"status": "sucesso", "estado": estado})
        else:
            # Se ainda não existe, retorna estado inicial
            return jsonify({
                "status": "sucesso", 
                "estado": {
                    "total_wins": 0,
                    "level_entries": {1: max(1.0, banca_atual * 0.05)},
                    "nivel_atual": 1
                }
            })
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/resetar_historico', methods=['POST'])
@app.route('/management/reset', methods=['POST'])
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

@app.route('/resetar_gerenciamento', methods=['POST'])
@app.route('/management/reset_gerenciamento', methods=['POST'])
def rota_resetar_gerenciamento():
    """Reseta apenas o gerenciamento, pegando 10% da banca atual."""
    try:
        dados = request.get_json() or {}
        tipo_conta = dados.get('tipo_conta', 'PRACTICE')
        
        # Seleciona a conta e pega o saldo atual
        trader.selecionar_conta(tipo_conta)
        banca_atual = trader.get_saldo()
        
        # Calcula nova entrada baseada em 10% da banca atual
        nova_entrada = round(banca_atual * 0.10, 2)
        nova_entrada = max(2.0, nova_entrada)  # Garante mínimo de R$ 2,00
        
        # Reseta apenas o gerenciamento
        database.resetar_estado_gerenciamento(db_conn, tipo_conta)
        gerenciador_multi.resetar_gerenciador(tipo_conta, banca_atual)
        
        # Verifica se o reset foi aplicado corretamente
        estado_apos_reset = gerenciador_multi.get_estado_gerenciador(tipo_conta)
        
        mensagem = f"Gerenciamento resetado para {tipo_conta}. Nova entrada: ${nova_entrada} (10% de ${banca_atual})"
        
        return jsonify({
            "status": "sucesso", 
            "mensagem": mensagem,
            "dados": {
                "tipo_conta": tipo_conta,
                "banca_atual": banca_atual,
                "nova_entrada": nova_entrada,
                "estado_apos_reset": estado_apos_reset
            }
        })
    except Exception as e:
        logging.error(f"Erro ao resetar gerenciamento: {e}", exc_info=True)
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/ping', methods=['GET'])
@app.route('/status', methods=['GET'])
def rota_de_ping():
    """Teste de conectividade."""
    return jsonify({
        "status": "sucesso", 
        "mensagem": "pong"
    })

@app.route('/get_saldos', methods=['GET'])
def rota_get_saldos():
    """Consulta saldo de ambas as contas."""
    try:
        # Saldo PRACTICE
        trader.selecionar_conta('PRACTICE')
        saldo_practice = trader.get_saldo()
        
        # Saldo REAL
        trader.selecionar_conta('REAL')
        saldo_real = trader.get_saldo()
        
        return jsonify({
            "status": "sucesso",
            "saldos": {
                "PRACTICE": {
                    "saldo": saldo_practice,
                    "disponivel": saldo_practice > 0
                },
                "REAL": {
                    "saldo": saldo_real,
                    "disponivel": saldo_real > 0
                }
            },
            "mensagem": f"PRACTICE: ${saldo_practice} | REAL: ${saldo_real}"
        })
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

# --- API Status ---
@app.route('/', methods=['GET'])
def api_status():
    """Status da API."""
    return jsonify({
        "status": "sucesso",
        "mensagem": "Bot Trader API funcionando",
        "endpoints": {
            "trade": "/trade",
            "balance": "/balance", 
            "history": "/history",
            "management": "/management",
            "reset_management": "/resetar_gerenciamento",
            "status": "/status"
        }
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=False)