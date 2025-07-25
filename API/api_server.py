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
    """Executa uma operação de trade. O valor de entrada é sempre calculado como porcentagem do saldo atual, conforme informado no input HTTP."""
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
        logging.info(f"Iniciando trade na conta {tipo_conta} ({moeda}) com saldo de {saldo_anterior} e valor de entrada solicitado: {valor_entrada_req}")
        
        # Validação de saldo
        if saldo_anterior <= 0:
            return jsonify({
                "status": "erro", 
                "mensagem": f"Saldo insuficiente na conta {tipo_conta}. Saldo atual: {moeda} {saldo_anterior}"
            }), 400
        
        # Define valor do investimento
        valor_investido = None
        if isinstance(valor_entrada_req, (int, float)):
            # Interpreta como porcentagem do saldo
            valor_investido = round(saldo_anterior * (float(valor_entrada_req) / 100), 2)
            if valor_investido < 2.0:
                valor_investido = 2.0
            if valor_investido > saldo_anterior:
                logging.warning(f"Valor de entrada calculado ({valor_investido}) excede o saldo disponível ({saldo_anterior})")
                return jsonify({
                    "status": "erro", 
                    "mensagem": f"Valor de entrada calculado ({valor_investido}) excede o saldo disponível ({saldo_anterior})"
                }), 400
        elif valor_entrada_req == 'gen':
            # Por padrão, usa 10% do saldo
            valor_investido = round(saldo_anterior * 0.10, 2)
            if valor_investido < 2.0:
                valor_investido = 2.0
            logging.info(f"Valor de entrada padrão (10% do saldo): {valor_investido}")
        else:
            logging.warning(f"Valor de entrada inválido recebido: {valor_entrada_req}")
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
    """Gera e retorna uma imagem de gráfico de candlestick para um ativo."""
    try:
        import matplotlib
        matplotlib.use('Agg')  # Modo headless
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        import pandas as pd

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
        df.rename(columns=rename_map, inplace=True)
        df['Datetime'] = pd.to_datetime(df['Datetime'], unit='s')
        df.set_index('Datetime', inplace=True)

        # Verifica se todas as colunas necessárias existem
        for col in ['Open', 'High', 'Low', 'Close']:
            if col not in df.columns:
                return jsonify({"status": "erro", "mensagem": f"Coluna '{col}' não encontrada nos dados."}), 500

        # Gera o gráfico
        fig, ax = plt.subplots(figsize=(12, 6), facecolor='#0d1117')
        ax.set_facecolor('#0d1117')
        width = (df.index[1] - df.index[0]).total_seconds() / 60 * 0.6
        width2 = width * 0.1
        up = df[df.Close >= df.Open]
        down = df[df.Close < df.Open]
        up_color = '#26a69a'
        down_color = '#ef5350'
        text_color = '#c9d1d9'
        border_color = '#21262d'
        ax.bar(up.index, up.Close - up.Open, width, bottom=up.Open, color=up_color)
        ax.bar(up.index, up.High - up.Close, width2, bottom=up.Close, color=up_color, align='center')
        ax.bar(up.index, up.Low - up.Open, width2, bottom=up.Open, color=up_color, align='center')
        ax.bar(down.index, down.Close - down.Open, width, bottom=down.Open, color=down_color)
        ax.bar(down.index, down.High - down.Open, width2, bottom=down.Open, color=down_color, align='center')
        ax.bar(down.index, down.Low - down.Close, width2, bottom=down.Close, color=down_color, align='center')
        ax.grid(True, color=border_color, linestyle='--', linewidth=0.5)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.xticks(rotation=30, color=text_color)
        plt.yticks(color=text_color)
        plt.title(f'Gráfico de Candlestick - {ativo.upper()}', color=text_color, fontsize=16)
        plt.ylabel('Preço', color=text_color, fontsize=12)
        plt.xlabel('Horário', color=text_color, fontsize=12)
        for spine in ax.spines.values():
            spine.set_edgecolor(border_color)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor=fig.get_facecolor(), edgecolor='none', dpi=100)
        buf.seek(0)
        plt.close(fig)
        return send_file(buf, mimetype='image/png')
    except Exception as e:
        logging.error(f"Erro ao gerar gráfico: {e}", exc_info=True)
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/grafico_dados', methods=['POST'])
def rota_grafico_dados():
    """
    Recebe dados de candles (JSON ou texto), gera e retorna uma imagem de gráfico de candlestick real (usando mplfinance).
    Adiciona volume, média móvel (SMA 9), MACD, visualizador do preço atual e linhas de SR tocadas 2 vezes.
    Garante que a coluna Volume sempre exista.
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import pandas as pd
        import re
        import mplfinance as mpf
        import numpy as np
        import io

        # --- Processamento dos candles ---
        dados = request.get_json(silent=True)
        if dados and 'candles' in dados:
            candles = dados['candles']
            df = pd.DataFrame(candles)
            df['data'] = pd.to_datetime(df['data'])
            df.rename(columns={
                'abertura': 'Open',
                'fechamento': 'Close',
                'maxima': 'High',
                'minima': 'Low',
                'volume': 'Volume'
            }, inplace=True)
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

        # --- Garante que a coluna Volume sempre exista ---
        if 'Volume' not in df.columns:
            df['Volume'] = 0.0
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]

        # --- Média móvel de 9 períodos ---
        mav = (9,)

        # --- Calcula MACD ---
        exp12 = df['Close'].ewm(span=12, adjust=False).mean()
        exp26 = df['Close'].ewm(span=26, adjust=False).mean()
        macd = exp12 - exp26
        signal = macd.ewm(span=9, adjust=False).mean()
        macd_hist = macd - signal
        macd_df = pd.DataFrame({
            'MACD': macd,
            'Signal': signal,
            'Hist': macd_hist
        }, index=df.index)

        # --- Subplot do MACD (painel 1, não sobrepor o principal) ---
        apds = [
            mpf.make_addplot(macd_df['MACD'], panel=1, color='cyan', secondary_y=False, ylabel='MACD'),
            mpf.make_addplot(macd_df['Signal'], panel=1, color='magenta', secondary_y=False),
            mpf.make_addplot(macd_df['Hist'], panel=1, type='bar', color='dimgray', secondary_y=False)
        ]

        # --- Customização visual ---
        mc = mpf.make_marketcolors(
            up='#26a69a', down='#ef5350',
            edge='inherit', wick='inherit',
            volume='in', ohlc='inherit'
        )
        s = mpf.make_mpf_style(
            base_mpf_style='nightclouds',
            marketcolors=mc,
            facecolor='#181c25',
            edgecolor='#181c25',
            gridcolor='#444',
            gridstyle='--',
            rc={'font.size': 12, 'axes.labelcolor': 'white', 'axes.edgecolor': 'white', 'axes.titlesize': 16, 'axes.titleweight': 'bold', 'xtick.color': 'white', 'ytick.color': 'white'}
        )

        # --- GERA O GRÁFICO E ADICIONA LINHAS EXTRAS ---
        buf = io.BytesIO()
        fig, axes = mpf.plot(
            df,
            type='candle',
            style=s,
            figsize=(12, 8),
            title='Gráfico de Candlestick',
            ylabel='Preço',
            ylabel_lower='',
            xrotation=30,
            mav=mav,
            volume=True,
            addplot=apds,
            panel_ratios=(3,1),
            returnfig=True,
            savefig=dict(fname=buf, format='png', facecolor='#181c25', bbox_inches='tight')
        )
        ax = axes[0]  # painel principal

        # 1. Preço atual (último fechamento)
        preco_atual = df['Close'].iloc[-1]
        ax.axhline(preco_atual, color='deepskyblue', linestyle='--', linewidth=2, alpha=0.8)
        ax.text(df.index[-1], preco_atual, f'{preco_atual:.5f}', color='white', fontsize=12,
                bbox=dict(facecolor='deepskyblue', edgecolor='none', boxstyle='round,pad=0.3'),
                verticalalignment='center', horizontalalignment='left')

        # 2. Suportes/Resistências tocados 2 vezes
        precos_sr = np.concatenate([df['High'].values, df['Low'].values])
        precos_sr = np.round(precos_sr, 5)
        unicos, contagens = np.unique(precos_sr, return_counts=True)
        sr_niveis = unicos[contagens >= 2]
        for nivel in sr_niveis:
            ax.axhline(nivel, color='orange', linestyle=':', linewidth=1, alpha=0.7)

        buf.seek(0)
        return send_file(buf, mimetype='image/png')
    except Exception as e:
        logging.error(f"Erro ao gerar gráfico: {e}", exc_info=True)
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