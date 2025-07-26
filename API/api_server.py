# szinka/bot-trader-easypanel/bot-trader-easypanel-7b08e2b809dd38380d631d984c10ad6c7132fcde/API/api_server.py

from flask import Flask, request, jsonify
import logging
import os
import time
import decimal
from dotenv import load_dotenv
from flask import send_file  # Adiciona importação para envio de arquivos
import io  # Para buffer de imagem

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
    """Executa uma operação de trade. O valor de entrada é calculado automaticamente pelo sistema de níveis baseado na banca atual."""
    try:
        sinal = request.get_json()
        
        # Validações básicas
        if not sinal or 'ativo' not in sinal or ('acao' not in sinal and 'call' not in sinal and 'put' not in sinal) or 'duracao' not in sinal:
            return jsonify({"status": "erro", "mensagem": "Campos obrigatórios: ativo, acao/call/put, duracao"}), 400
        
        tipo_conta = sinal.get('tipo_conta', 'PRACTICE')

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
        
        # Calcula valor do investimento usando o sistema de níveis
        valor_investido = gerenciador_multi.get_proxima_entrada(tipo_conta, saldo_anterior)
        logging.info(f"Valor de entrada calculado pelo sistema de níveis: {valor_investido}")

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

        # Atualiza gerenciamento após trade
        if acao in ['call', 'put']:
            resultado = sinal.get('resultado')
            if resultado in ['win', 'lose']:
                gerenciador_multi.processar_resultado(tipo_conta, resultado, saldo_anterior)
                estado = gerenciador_multi.get_estado_gerenciador(tipo_conta)
                winrate = estado.get('winrate', 0)
                logging.info(f"[{tipo_conta.upper()}] {resultado.capitalize()}! Winrate: {winrate:.2f}%")
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
    """Consulta estado do gerenciador (apenas wins/losses e winrate, sem entradas por nível)."""
    try:
        tipo_conta = request.args.get('tipo_conta', 'PRACTICE')
        trader.selecionar_conta(tipo_conta)
        banca_atual = trader.get_saldo()
        gerenciador_multi._get_gerenciador(tipo_conta, banca_atual)  # Garante que existe
        estado = gerenciador_multi.get_estado_gerenciador(tipo_conta)
        if estado:
            return jsonify({"status": "sucesso", "estado": estado})
        else:
            return jsonify({
                "status": "sucesso", 
                "estado": {
                    "total_wins": 0,
                    "total_losses": 0,
                    "nivel_atual": 1,
                    "winrate": 0.0
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
    """Reseta apenas o gerenciamento (tracking de wins/losses)."""
    try:
        dados = request.get_json() or {}
        tipo_conta = dados.get('tipo_conta', 'PRACTICE')
        trader.selecionar_conta(tipo_conta)
        banca_atual = trader.get_saldo()
        database.resetar_estado_gerenciamento(db_conn, tipo_conta)
        gerenciador_multi.resetar_gerenciador(tipo_conta, banca_atual)
        estado_apos_reset = gerenciador_multi.get_estado_gerenciador(tipo_conta)
        mensagem = f"Gerenciamento resetado para {tipo_conta}. Tracking de wins/losses zerado."
        return jsonify({
            "status": "sucesso", 
            "mensagem": mensagem,
            "dados": {
                "tipo_conta": tipo_conta,
                "banca_atual": banca_atual,
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

# --- Endpoint para gerar gráfico de candlestick ---
@app.route('/grafico', methods=['GET'])
def rota_get_grafico():
    """Gera e retorna uma imagem de gráfico de candlestick para um ativo com visual TradingView profissional."""
    try:
        import matplotlib
        matplotlib.use('Agg')  # Modo headless
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        import pandas as pd
        import numpy as np
        import io

        # Parâmetros da requisição
        ativo = request.args.get('ativo', 'EURUSD-OTC')
        timeframe = int(request.args.get('timeframe', 1))
        quantidade = int(request.args.get('quantidade', 100))

        # Busca os candles
        velas = trader.get_candles(ativo, timeframe, quantidade)
        if not velas:
            return jsonify({"status": "erro", "mensagem": "Não foi possível obter os dados das velas."}), 404

        # Processa os dados
        df = pd.DataFrame(velas)
        
        # Força o rename para garantir as colunas corretas
        rename_map = {}
        for col in df.columns:
            if col.lower() == 'from':
                rename_map[col] = 'Datetime'
            elif col.lower() == 'open':
                rename_map[col] = 'Open'
            elif col.lower() == 'high':
                rename_map[col] = 'High'
            elif col.lower() == 'low':
                rename_map[col] = 'Low'
            elif col.lower() == 'close':
                rename_map[col] = 'Close'
            elif col.lower() == 'volume':
                rename_map[col] = 'Volume'
        df.rename(columns=rename_map, inplace=True)
        df['Datetime'] = pd.to_datetime(df['Datetime'], unit='s')
        df.set_index('Datetime', inplace=True)

        # Garante que Volume existe
        if 'Volume' not in df.columns:
            df['Volume'] = 0.0

        # Verifica se todas as colunas necessárias existem
        for col in ['Open', 'High', 'Low', 'Close']:
            if col not in df.columns:
                return jsonify({"status": "erro", "mensagem": f"Coluna '{col}' não encontrada nos dados."}), 500

        # Converte colunas para float para garantir compatibilidade
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove linhas com dados inválidos
        df = df.dropna(subset=['Open', 'High', 'Low', 'Close'])
        
        if df.empty:
            return jsonify({"status": "erro", "mensagem": "Não há dados válidos para gerar o gráfico."}), 500

        # Calcula indicadores técnicos avançados
        df['SMA_9'] = df['Close'].rolling(window=9).mean()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # Bollinger Bands
        df['BB_20'] = df['Close'].rolling(window=20).mean()
        df['BB_upper'] = df['BB_20'] + (df['Close'].rolling(window=20).std() * 2)
        df['BB_lower'] = df['BB_20'] - (df['Close'].rolling(window=20).std() * 2)
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp12 = df['Close'].ewm(span=12, adjust=False).mean()
        exp26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp12 - exp26
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['Signal']
        
        # Stochastic
        df['Stoch_K'] = ((df['Close'] - df['Low'].rolling(window=14).min()) / 
                         (df['High'].rolling(window=14).max() - df['Low'].rolling(window=14).min())) * 100
        df['Stoch_D'] = df['Stoch_K'].rolling(window=3).mean()
        
        # ATR (Average True Range)
        df['TR'] = np.maximum(
            df['High'] - df['Low'],
            np.maximum(
                abs(df['High'] - df['Close'].shift(1)),
                abs(df['Low'] - df['Close'].shift(1))
            )
        )
        df['ATR'] = df['TR'].rolling(window=14).mean()

        # Cria figura com layout profissional
        fig = plt.figure(figsize=(16, 12), facecolor='#0d1117')
        
        # Define cores TradingView profissionais
        colors = {
            'background': '#0d1117',
            'grid': '#1f2937',
            'text': '#e5e7eb',
            'border': '#374151',
            'up': '#00c853',
            'down': '#ff5252',
            'sma9': '#ff9800',
            'sma20': '#2196f3',
            'sma50': '#9c27b0',
            'bb_upper': '#ff5722',
            'bb_lower': '#ff5722',
            'bb_middle': '#ff9800',
            'rsi': '#00bcd4',
            'macd': '#00bcd4',
            'signal': '#ff5722',
            'stoch': '#ff9800',
            'volume_up': '#00c853',
            'volume_down': '#ff5252'
        }

        # Configuração geral
        plt.rcParams['font.size'] = 10
        plt.rcParams['font.family'] = 'DejaVu Sans'

        # Layout: 5 painéis organizados
        gs = fig.add_gridspec(5, 1, height_ratios=[3, 1, 1, 1, 1], hspace=0.05)

        # Painel 1: Candlesticks e indicadores principais
        ax1 = fig.add_subplot(gs[0])
        
        # Plota candlesticks usando linhas verticais e horizontais
        for i, (idx, row) in enumerate(df.iterrows()):
            # Determina cor baseada na direção da vela
            if row['Close'] >= row['Open']:
                color = colors['up']
            else:
                color = colors['down']
            
            # Desenha a linha vertical (mecha)
            ax1.plot([idx, idx], [row['Low'], row['High']], color=color, linewidth=1)
            
            # Desenha o corpo da vela
            body_height = abs(row['Close'] - row['Open'])
            if body_height > 0:
                # Corpo da vela como retângulo
                if row['Close'] >= row['Open']:
                    # Vela de alta (verde)
                    ax1.add_patch(plt.Rectangle(
                        (idx - width/2, row['Open']), 
                        width, body_height,
                        facecolor=color, edgecolor=color, alpha=0.8
                    ))
                else:
                    # Vela de baixa (vermelha)
                    ax1.add_patch(plt.Rectangle(
                        (idx - width/2, row['Close']), 
                        width, body_height,
                        facecolor=color, edgecolor=color, alpha=0.8
                    ))
            else:
                # Doji - apenas linha horizontal
                ax1.plot([idx - width/2, idx + width/2], [row['Open'], row['Open']], 
                        color=color, linewidth=2)
        
        # Médias móveis
        ax1.plot(df.index, df['SMA_9'], color=colors['sma9'], linewidth=1.5, 
                label='SMA 9', alpha=0.8)
        ax1.plot(df.index, df['SMA_20'], color=colors['sma20'], linewidth=1.5, 
                label='SMA 20', alpha=0.8)
        ax1.plot(df.index, df['SMA_50'], color=colors['sma50'], linewidth=1.5, 
                label='SMA 50', alpha=0.8)
        
        # Bollinger Bands
        ax1.plot(df.index, df['BB_upper'], color=colors['bb_upper'], linewidth=1, 
                alpha=0.6, linestyle='--', label='BB Upper')
        ax1.plot(df.index, df['BB_lower'], color=colors['bb_lower'], linewidth=1, 
                alpha=0.6, linestyle='--', label='BB Lower')
        ax1.plot(df.index, df['BB_20'], color=colors['bb_middle'], linewidth=1, 
                alpha=0.6, label='BB Middle')
        
        # Configuração do gráfico principal
        ax1.set_facecolor(colors['background'])
        ax1.grid(True, color=colors['grid'], linestyle='-', linewidth=0.5, alpha=0.3)
        ax1.set_title(f'{ativo.upper()} - {timeframe}min - Análise Técnica Completa', 
                     color=colors['text'], fontsize=14, fontweight='bold', pad=20)
        ax1.set_ylabel('Preço', color=colors['text'], fontsize=12)
        ax1.legend(loc='upper left', frameon=False, fontsize=9, ncol=3)
        
        # Remove bordas
        for spine in ax1.spines.values():
            spine.set_color(colors['border'])
            spine.set_linewidth(0.5)
        
        # Configuração dos ticks
        ax1.tick_params(colors=colors['text'], labelsize=10)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=0)

        # Painel 2: Volume
        ax2 = fig.add_subplot(gs[1], sharex=ax1)
        
        # Volume como barras normais
        for i, (idx, row) in enumerate(df.iterrows()):
            # Determina cor baseada na direção do preço
            if row['Close'] >= row['Open']:
                color = colors['volume_up']
            else:
                color = colors['volume_down']
            
            # Desenha barra de volume
            if row['Volume'] > 0:
                ax2.add_patch(plt.Rectangle(
                    (idx - 0.3, 0), 
                    0.6, row['Volume'],
                    facecolor=color, edgecolor=color, alpha=0.7
                ))
        
        ax2.set_ylabel('Volume', color=colors['text'], fontsize=10)
        ax2.set_facecolor(colors['background'])
        ax2.grid(True, color=colors['grid'], linestyle='-', linewidth=0.5, alpha=0.3)
        
        # Remove bordas do volume
        for spine in ax2.spines.values():
            spine.set_color(colors['border'])
            spine.set_linewidth(0.5)
        
        ax2.tick_params(colors=colors['text'], labelsize=9)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        # Painel 3: RSI
        ax3 = fig.add_subplot(gs[2], sharex=ax1)
        
        ax3.plot(df.index, df['RSI'], color=colors['rsi'], linewidth=1.5, label='RSI')
        ax3.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='Sobrecomprado')
        ax3.axhline(y=30, color='green', linestyle='--', alpha=0.5, label='Sobrevendido')
        ax3.fill_between(df.index, 70, 100, alpha=0.1, color='red')
        ax3.fill_between(df.index, 0, 30, alpha=0.1, color='green')
        
        ax3.set_ylabel('RSI', color=colors['text'], fontsize=10)
        ax3.set_ylim(0, 100)
        ax3.set_facecolor(colors['background'])
        ax3.grid(True, color=colors['grid'], linestyle='-', linewidth=0.5, alpha=0.3)
        ax3.legend(loc='upper left', frameon=False, fontsize=8)
        
        # Remove bordas do RSI
        for spine in ax3.spines.values():
            spine.set_color(colors['border'])
            spine.set_linewidth(0.5)
        
        ax3.tick_params(colors=colors['text'], labelsize=9)
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        # Painel 4: MACD
        ax4 = fig.add_subplot(gs[3], sharex=ax1)
        
        ax4.plot(df.index, df['MACD'], color=colors['macd'], linewidth=1.5, label='MACD')
        ax4.plot(df.index, df['Signal'], color=colors['signal'], linewidth=1.5, label='Signal')
        
        # Histograma MACD
        macd_colors = []
        for i in range(len(df)):
            if df['MACD_Hist'].iloc[i] >= 0:
                macd_colors.append(colors['up'])
            else:
                macd_colors.append(colors['down'])
        
        ax4.bar(df.index, df['MACD_Hist'], color=macd_colors, alpha=0.6, width=0.8)
        
        # Linha zero
        ax4.axhline(y=0, color=colors['text'], linestyle='-', linewidth=0.5, alpha=0.5)
        
        ax4.set_ylabel('MACD', color=colors['text'], fontsize=10)
        ax4.set_facecolor(colors['background'])
        ax4.grid(True, color=colors['grid'], linestyle='-', linewidth=0.5, alpha=0.3)
        ax4.legend(loc='upper left', frameon=False, fontsize=8)
        
        # Remove bordas do MACD
        for spine in ax4.spines.values():
            spine.set_color(colors['border'])
            spine.set_linewidth(0.5)
        
        ax4.tick_params(colors=colors['text'], labelsize=9)
        ax4.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        # Painel 5: Stochastic
        ax5 = fig.add_subplot(gs[4], sharex=ax1)
        
        ax5.plot(df.index, df['Stoch_K'], color=colors['stoch'], linewidth=1.5, label='%K')
        ax5.plot(df.index, df['Stoch_D'], color=colors['signal'], linewidth=1.5, label='%D')
        ax5.axhline(y=80, color='red', linestyle='--', alpha=0.5, label='Sobrecomprado')
        ax5.axhline(y=20, color='green', linestyle='--', alpha=0.5, label='Sobrevendido')
        ax5.fill_between(df.index, 80, 100, alpha=0.1, color='red')
        ax5.fill_between(df.index, 0, 20, alpha=0.1, color='green')
        
        ax5.set_ylabel('Stoch', color=colors['text'], fontsize=10)
        ax5.set_xlabel('Horário', color=colors['text'], fontsize=10)
        ax5.set_ylim(0, 100)
        ax5.set_facecolor(colors['background'])
        ax5.grid(True, color=colors['grid'], linestyle='-', linewidth=0.5, alpha=0.3)
        ax5.legend(loc='upper left', frameon=False, fontsize=8)
        
        # Remove bordas do Stochastic
        for spine in ax5.spines.values():
            spine.set_color(colors['border'])
            spine.set_linewidth(0.5)
        
        ax5.tick_params(colors=colors['text'], labelsize=9)
        ax5.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        # Ajusta layout
        plt.tight_layout()
        plt.subplots_adjust(hspace=0.1)
        
        # Salva a imagem
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor=colors['background'], 
                   edgecolor='none', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        return send_file(buf, mimetype='image/png')
        
    except Exception as e:
        logging.error(f"Erro ao gerar gráfico: {e}", exc_info=True)
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/grafico_dados', methods=['POST'])
def rota_grafico_dados():
    """
    Recebe dados de candles (JSON ou texto) e gera gráfico com visual TradingView profissional.
    Inclui 5 painéis: candlesticks, volume, RSI, MACD, Stochastic.
    """
    try:
        import matplotlib
        matplotlib.use('Agg')  # Modo headless
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        import pandas as pd
        import numpy as np
        import io
        import re

        # --- Processamento dos candles ---
        dados = request.get_json(silent=True)
        if dados and 'candles' in dados:
            candles = dados['candles']
            # Ordena do mais antigo para o mais recente
            candles.sort(key=lambda c: pd.to_datetime(c['data']))
            df = pd.DataFrame(candles)
            
            # Converte timestamp para datetime
            df['data'] = pd.to_datetime(df['data'])
            
            # Renomeia colunas
            df.rename(columns={
                'abertura': 'Open',
                'fechamento': 'Close',
                'maxima': 'High',
                'minima': 'Low',
                'volume': 'Volume'
            }, inplace=True)
            
            # Converte colunas numéricas para float ANTES de setar o índice
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Garante que Volume existe
            if 'Volume' not in df.columns:
                df['Volume'] = 0.0
            
            # Remove linhas com dados inválidos ANTES de setar o índice
            df = df.dropna(subset=['Open', 'High', 'Low', 'Close'])
            
            if df.empty:
                return jsonify({"status": "erro", "mensagem": "Não há dados válidos para gerar o gráfico."}), 500
            
            # Seta o índice por último
            df.set_index('data', inplace=True)
        else:
            texto = request.data.decode('utf-8')
            padrao = r"Data: ([^,]+), Abertura: ([^,]+), Fechamento: ([^,]+), Máxima: ([^,]+), Mínima: ([^,]+)(?:, Volume: ([^\n]+))?"
            matches = re.findall(padrao, texto)
            if not matches:
                return jsonify({"status": "erro", "mensagem": "Formato de dados inválido."}), 400
            if len(matches[0]) == 6:
                df = pd.DataFrame(matches, columns=['data', 'Open', 'Close', 'High', 'Low', 'Volume'])
                df['Volume'] = df['Volume'].replace('', '0').astype(float)
            else:
                df = pd.DataFrame(matches, columns=['data', 'Open', 'Close', 'High', 'Low'])
                df['Volume'] = 0.0
            df['data'] = pd.to_datetime(df['data'])
            for col in ['Open', 'Close', 'High', 'Low']:
                df[col] = df[col].astype(float)
            df.set_index('data', inplace=True)

        # --- Garante que a coluna Volume sempre exista (apenas para o else) ---
        if 'Volume' not in df.columns:
            df['Volume'] = 0.0
        
        # Converte colunas para float para garantir compatibilidade (apenas para o else)
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove linhas com dados inválidos (apenas para o else)
        df = df.dropna(subset=['Open', 'High', 'Low', 'Close'])
        
        if df.empty:
            return jsonify({"status": "erro", "mensagem": "Não há dados válidos para gerar o gráfico."}), 500

        # Calcula indicadores técnicos avançados
        df['SMA_9'] = df['Close'].rolling(window=9).mean()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # Bollinger Bands
        df['BB_20'] = df['Close'].rolling(window=20).mean()
        df['BB_upper'] = df['BB_20'] + (df['Close'].rolling(window=20).std() * 2)
        df['BB_lower'] = df['BB_20'] - (df['Close'].rolling(window=20).std() * 2)
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp12 = df['Close'].ewm(span=12, adjust=False).mean()
        exp26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp12 - exp26
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['Signal']
        
        # Stochastic
        df['Stoch_K'] = ((df['Close'] - df['Low'].rolling(window=14).min()) / 
                         (df['High'].rolling(window=14).max() - df['Low'].rolling(window=14).min())) * 100
        df['Stoch_D'] = df['Stoch_K'].rolling(window=3).mean()
        
        # ATR (Average True Range)
        df['TR'] = np.maximum(
            df['High'] - df['Low'],
            np.maximum(
                abs(df['High'] - df['Close'].shift(1)),
                abs(df['Low'] - df['Close'].shift(1))
            )
        )
        df['ATR'] = df['TR'].rolling(window=14).mean()

        # Cria figura com layout profissional
        fig = plt.figure(figsize=(16, 12), facecolor='#0d1117')
        
        # Define cores TradingView profissionais
        colors = {
            'background': '#0d1117',
            'grid': '#1f2937',
            'text': '#e5e7eb',
            'border': '#374151',
            'up': '#00c853',
            'down': '#ff5252',
            'sma9': '#ff9800',
            'sma20': '#2196f3',
            'sma50': '#9c27b0',
            'bb_upper': '#ff5722',
            'bb_lower': '#ff5722',
            'bb_middle': '#ff9800',
            'rsi': '#00bcd4',
            'macd': '#00bcd4',
            'signal': '#ff5722',
            'stoch': '#ff9800',
            'volume_up': '#00c853',
            'volume_down': '#ff5252'
        }

        # Configuração geral
        plt.rcParams['font.size'] = 10
        plt.rcParams['font.family'] = 'DejaVu Sans'

        # Layout: 5 painéis organizados
        gs = fig.add_gridspec(5, 1, height_ratios=[3, 1, 1, 1, 1], hspace=0.05)

        # Define largura das velas
        width = 0.6

        # Painel 1: Candlesticks e indicadores principais
        ax1 = fig.add_subplot(gs[0])
        
        # Plota candlesticks usando barras simples
        up = df[df.Close >= df.Open]
        down = df[df.Close < df.Open]
        
        # Velas de alta (verde)
        if not up.empty:
            ax1.bar(up.index, up.Close - up.Open, width=0.6, bottom=up.Open, 
                   color=colors['up'], alpha=0.8, edgecolor=colors['up'])
            # Mechas de alta
            for idx, row in up.iterrows():
                ax1.plot([idx, idx], [row['Low'], row['High']], color=colors['up'], linewidth=1)
        
        # Velas de baixa (vermelho)
        if not down.empty:
            ax1.bar(down.index, down.Close - down.Open, width=0.6, bottom=down.Open, 
                   color=colors['down'], alpha=0.8, edgecolor=colors['down'])
            # Mechas de baixa
            for idx, row in down.iterrows():
                ax1.plot([idx, idx], [row['Low'], row['High']], color=colors['down'], linewidth=1)
        
        # Médias móveis
        ax1.plot(df.index, df['SMA_9'], color=colors['sma9'], linewidth=1.5, 
                label='SMA 9', alpha=0.8)
        ax1.plot(df.index, df['SMA_20'], color=colors['sma20'], linewidth=1.5, 
                label='SMA 20', alpha=0.8)
        ax1.plot(df.index, df['SMA_50'], color=colors['sma50'], linewidth=1.5, 
                label='SMA 50', alpha=0.8)
        
        # Bollinger Bands
        ax1.plot(df.index, df['BB_upper'], color=colors['bb_upper'], linewidth=1, 
                alpha=0.6, linestyle='--', label='BB Upper')
        ax1.plot(df.index, df['BB_lower'], color=colors['bb_lower'], linewidth=1, 
                alpha=0.6, linestyle='--', label='BB Lower')
        ax1.plot(df.index, df['BB_20'], color=colors['bb_middle'], linewidth=1, 
                alpha=0.6, label='BB Middle')
        
        # Configuração do gráfico principal
        ax1.set_facecolor(colors['background'])
        ax1.grid(True, color=colors['grid'], linestyle='-', linewidth=0.5, alpha=0.3)
        ax1.set_title('Análise Técnica Completa - Dados Fornecidos', 
                     color=colors['text'], fontsize=14, fontweight='bold', pad=20)
        ax1.set_ylabel('Preço', color=colors['text'], fontsize=12)
        ax1.legend(loc='upper left', frameon=False, fontsize=9, ncol=3)
        
        # Remove bordas
        for spine in ax1.spines.values():
            spine.set_color(colors['border'])
            spine.set_linewidth(0.5)
        
        # Configuração dos ticks
        ax1.tick_params(colors=colors['text'], labelsize=10)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=0)

        # Painel 2: Volume
        ax2 = fig.add_subplot(gs[1], sharex=ax1)
        
        # Volume como barras normais
        volume_colors = []
        for i in range(len(df)):
            if df['Close'].iloc[i] >= df['Open'].iloc[i]:
                volume_colors.append(colors['volume_up'])
            else:
                volume_colors.append(colors['volume_down'])
        
        ax2.bar(df.index, df['Volume'], color=volume_colors, alpha=0.7, width=0.6)
        ax2.set_ylabel('Volume', color=colors['text'], fontsize=10)
        ax2.set_facecolor(colors['background'])
        ax2.grid(True, color=colors['grid'], linestyle='-', linewidth=0.5, alpha=0.3)
        
        # Remove bordas do volume
        for spine in ax2.spines.values():
            spine.set_color(colors['border'])
            spine.set_linewidth(0.5)
        
        ax2.tick_params(colors=colors['text'], labelsize=9)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        # Painel 3: RSI
        ax3 = fig.add_subplot(gs[2], sharex=ax1)
        
        ax3.plot(df.index, df['RSI'], color=colors['rsi'], linewidth=1.5, label='RSI')
        ax3.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='Sobrecomprado')
        ax3.axhline(y=30, color='green', linestyle='--', alpha=0.5, label='Sobrevendido')
        ax3.fill_between(df.index, 70, 100, alpha=0.1, color='red')
        ax3.fill_between(df.index, 0, 30, alpha=0.1, color='green')
        
        ax3.set_ylabel('RSI', color=colors['text'], fontsize=10)
        ax3.set_ylim(0, 100)
        ax3.set_facecolor(colors['background'])
        ax3.grid(True, color=colors['grid'], linestyle='-', linewidth=0.5, alpha=0.3)
        ax3.legend(loc='upper left', frameon=False, fontsize=8)
        
        # Remove bordas do RSI
        for spine in ax3.spines.values():
            spine.set_color(colors['border'])
            spine.set_linewidth(0.5)
        
        ax3.tick_params(colors=colors['text'], labelsize=9)
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        # Painel 4: MACD
        ax4 = fig.add_subplot(gs[3], sharex=ax1)
        
        ax4.plot(df.index, df['MACD'], color=colors['macd'], linewidth=1.5, label='MACD')
        ax4.plot(df.index, df['Signal'], color=colors['signal'], linewidth=1.5, label='Signal')
        
        # Histograma MACD
        macd_colors = []
        for i in range(len(df)):
            if df['MACD_Hist'].iloc[i] >= 0:
                macd_colors.append(colors['up'])
            else:
                macd_colors.append(colors['down'])
        
        ax4.bar(df.index, df['MACD_Hist'], color=macd_colors, alpha=0.6, width=0.8)
        
        # Linha zero
        ax4.axhline(y=0, color=colors['text'], linestyle='-', linewidth=0.5, alpha=0.5)
        
        ax4.set_ylabel('MACD', color=colors['text'], fontsize=10)
        ax4.set_facecolor(colors['background'])
        ax4.grid(True, color=colors['grid'], linestyle='-', linewidth=0.5, alpha=0.3)
        ax4.legend(loc='upper left', frameon=False, fontsize=8)
        
        # Remove bordas do MACD
        for spine in ax4.spines.values():
            spine.set_color(colors['border'])
            spine.set_linewidth(0.5)
        
        ax4.tick_params(colors=colors['text'], labelsize=9)
        ax4.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        # Painel 5: Stochastic
        ax5 = fig.add_subplot(gs[4], sharex=ax1)
        
        ax5.plot(df.index, df['Stoch_K'], color=colors['stoch'], linewidth=1.5, label='%K')
        ax5.plot(df.index, df['Stoch_D'], color=colors['signal'], linewidth=1.5, label='%D')
        ax5.axhline(y=80, color='red', linestyle='--', alpha=0.5, label='Sobrecomprado')
        ax5.axhline(y=20, color='green', linestyle='--', alpha=0.5, label='Sobrevendido')
        ax5.fill_between(df.index, 80, 100, alpha=0.1, color='red')
        ax5.fill_between(df.index, 0, 20, alpha=0.1, color='green')
        
        ax5.set_ylabel('Stoch', color=colors['text'], fontsize=10)
        ax5.set_xlabel('Horário', color=colors['text'], fontsize=10)
        ax5.set_ylim(0, 100)
        ax5.set_facecolor(colors['background'])
        ax5.grid(True, color=colors['grid'], linestyle='-', linewidth=0.5, alpha=0.3)
        ax5.legend(loc='upper left', frameon=False, fontsize=8)
        
        # Remove bordas do Stochastic
        for spine in ax5.spines.values():
            spine.set_color(colors['border'])
            spine.set_linewidth(0.5)
        
        ax5.tick_params(colors=colors['text'], labelsize=9)
        ax5.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        # Ajusta layout
        plt.tight_layout()
        plt.subplots_adjust(hspace=0.1)
        
        # Salva a imagem
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor=colors['background'], 
                   edgecolor='none', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        return send_file(buf, mimetype='image/png')
        
    except Exception as e:
        logging.error(f"Erro ao gerar gráfico de dados: {e}", exc_info=True)
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
    # Logar status inicial da conta REAL (apenas uma vez)
    trader.selecionar_conta('REAL')
    banca_real = trader.get_saldo()
    estado_real = gerenciador_multi.get_estado_gerenciador('REAL')
    
    print("\n✅ Server ligado com sucesso")
    print(f"[Conta: REAL | Banca: ${banca_real} | Wins: {estado_real['total_wins']} | Próxima entrada MK: ${proxima_entrada}]")
    print("Pronto pro trade!\n")
    app.run(host='0.0.0.0', port=8080, debug=False)