# API/api_server.py
from flask import Flask, request, jsonify
import logging
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Importa os módulos essenciais
from API.trader import Trader
from API.gerenciamento import GerenciadorMultiConta

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# --- Inicialização dos Componentes ---
try:
    trader = Trader()
    # Configuração de gerenciamento: valores percentuais
    config_gerenciamento = {
        'entrada_padrao': float(os.getenv('ENTRY_PERCENTAGE', 3.0)),  # % padrão da banca
        'limite_maximo': float(os.getenv('GERENCIAMENTO_PERCENT', 5.0))  # limite percentual máximo
    }
    
    # Log das configurações carregadas
    logging.info(f"Configurações carregadas:")
    logging.info(f"  - ENTRY_PERCENTAGE: {os.getenv('ENTRY_PERCENTAGE', 3.0)}%")
    logging.info(f"  - GERENCIAMENTO_PERCENT (limite): {os.getenv('GERENCIAMENTO_PERCENT', 5.0)}%")
    
    # Inicializa o gerenciador multi-conta
    gerenciador_multi = GerenciadorMultiConta(config_gerenciamento)
    
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

        if not trader.selecionar_conta(tipo_conta):
            return jsonify({"status": "erro", "mensagem": "Falha ao selecionar conta"}), 400
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
        if not trader.selecionar_conta(tipo_conta):
            return jsonify({"status": "erro", "mensagem": "Falha ao selecionar conta"}), 400
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
    """Executa uma operação de trade. O valor de entrada é sempre calculado como porcentagem do saldo atual, conforme informado no input HTTP."""
    try:
        sinal = request.get_json()
        
        # Validações básicas
        if not sinal or 'ativo' not in sinal or ('acao' not in sinal and 'call' not in sinal and 'put' not in sinal) or 'duracao' not in sinal:
            return jsonify({"status": "erro", "mensagem": "Campos obrigatórios: ativo, acao/call/put, duracao"}), 400
        
        tipo_conta = sinal.get('tipo_conta', 'PRACTICE')
        # aceita percentuais como: percent_banca, percent, valor_entrada (em % da banca)
        percent_param = (
            sinal.get('percent_banca', None)
            if sinal.get('percent_banca', None) is not None else
            sinal.get('percent', None)
            if sinal.get('percent', None) is not None else
            sinal.get('valor_entrada', None)
        )

        # Seleciona a conta
        if not trader.selecionar_conta(tipo_conta):
            return jsonify({"status": "erro", "mensagem": "Falha ao selecionar conta"}), 400
        moeda = trader.get_moeda_conta()
        saldo_anterior = trader.get_saldo()
        logging.info(f"Iniciando trade na conta {tipo_conta} ({moeda}) com saldo de {saldo_anterior} e percentual solicitado: {percent_param}")
        
        # Validação de saldo
        if saldo_anterior <= 0:
            return jsonify({
                "status": "erro", 
                "mensagem": f"Saldo insuficiente na conta {tipo_conta}. Saldo atual: {moeda} {saldo_anterior}"
            }), 400
        
        # Define valor do investimento pela porcentagem da banca
        if percent_param is not None:
            try:
                percent_value = float(percent_param)
            except (TypeError, ValueError):
                return jsonify({"status": "erro", "mensagem": "Percentual inválido."}), 400
            valor_investido = gerenciador_multi.get_proxima_entrada(tipo_conta, saldo_anterior, percent_value)
        else:
            valor_investido = gerenciador_multi.get_proxima_entrada(tipo_conta, saldo_anterior)

        # Determina a ação (call/put)
        # Normaliza ação: aceita call/put, buy/sell, compra/venda
        acao_raw = sinal.get('acao', sinal.get('action', sinal.get('call', sinal.get('put'))))
        acao_map = {
            'call': 'call', 'buy': 'call', 'comprar': 'call', 'compra': 'call',
            'put': 'put', 'sell': 'put', 'vender': 'put', 'venda': 'put'
        }
        acao_key = str(acao_raw).strip().lower() if acao_raw is not None else None
        acao = acao_map.get(acao_key)
        if acao not in ['call', 'put']:
            return jsonify({"status": "erro", "mensagem": "Ação deve ser compra/venda (buy/sell) ou call/put"}), 400
        
        # Executa a ordem
        check, order_id = trader.comprar_ativo(
            sinal['ativo'], valor_investido, acao, int(sinal['duracao'])
        )
        
        if not check:
            return jsonify({"status": "erro", "mensagem": "Ordem rejeitada na Binária"}), 500

        # Retorna resposta com informações do trade
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

@app.route('/history', methods=['GET'])
def rota_get_historico():
    """Histórico de trades (stub sem persistência)."""
    return jsonify({"status": "sucesso", "historico": []})

@app.route('/management', methods=['GET'])
def rota_get_estado_gerenciador():
    """Estado do gerenciador (stub)."""
    tipo_conta = request.args.get('tipo_conta', 'PRACTICE')
    if not trader.selecionar_conta(tipo_conta):
        return jsonify({"status": "erro", "mensagem": "Falha ao selecionar conta"}), 400
    _ = trader.get_saldo()
    return jsonify({
        "status": "sucesso", 
        "estado": {
            "total_wins": 0,
            "total_losses": 0,
            "nivel_atual": 1,
            "winrate": 0.0
        }
    })

@app.route('/management/reset', methods=['POST'])
def rota_resetar_historico():
    """Reset de gerenciamento (stub)."""
    dados = request.get_json() or {}
    tipo_conta = dados.get('tipo_conta', 'PRACTICE')
    if not trader.selecionar_conta(tipo_conta):
        return jsonify({"status": "erro", "mensagem": "Falha ao selecionar conta"}), 400
    _ = trader.get_saldo()
    return jsonify({"status": "sucesso", "mensagem": f"Gerenciamento resetado para {tipo_conta}."})

# Endpoint mantido acima: /management/reset (stub)

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
            "reset_management": "/management/reset",
            "status": "/status"
        }
    })

if __name__ == "__main__":
    trader.selecionar_conta('REAL')
    banca_real = trader.get_saldo()
    proxima_entrada = gerenciador_multi.get_proxima_entrada('REAL', banca_real)
    print("\n✅ Server ligado com sucesso")
    print(f"[Conta: REAL | Banca: ${banca_real} | Próxima entrada: ${proxima_entrada}]")
    print("Pronto pro trade!\n")
    app.run(host='0.0.0.0', port=8080, debug=False)
