# szinka/bot-trader-easypanel/bot-trader-easypanel-7b08e2b809dd38380d631d984c10ad6c7132fcde/API/api_server.py

import os
import sys
import logging
from flask import Flask, request, jsonify, send_file
from dotenv import load_dotenv
import psycopg2
from psycopg2 import pool
import io
import matplotlib
matplotlib.use('Agg')  # Modo "headless" para não precisar de interface gráfica
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

# Adiciona a pasta raiz ao path para encontrar o módulo Trader
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Bot.trader import Trader  # noqa: E402

# --- Configuração Inicial ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuração do Flask ---
app = Flask(__name__)

# --- Conexão com o Banco de Dados (PostgreSQL) ---
try:
    db_pool = psycopg2.pool.SimpleConnectionPool(
        1, 10,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )
    logging.info("Pool de conexões com o PostgreSQL criado com sucesso.")
except Exception as e:
    logging.error(f"Não foi possível conectar ao PostgreSQL: {e}")
    db_pool = None

# --- Instância do Trader ---
try:
    trader = Trader()
    trader.connect()
    logging.info("Instância do Trader criada e conectada com sucesso.")
except Exception as e:
    logging.error(f"Falha ao instanciar ou conectar o Trader: {e}")
    trader = None

# --- Endpoints da API ---

@app.route('/status', methods=['GET'])
def get_status():
    """Verifica o status da API, da conexão com a IQ Option e com o banco de dados."""
    db_status = "conectado" if db_pool else "desconectado"
    iq_status = "conectado" if trader and trader.is_connected() else "desconectado"
    
    return jsonify({
        "status_api": "online",
        "status_iq_option": iq_status,
        "status_database": db_status
    })

@app.route('/profile', methods=['GET'])
def get_profile():
    """Retorna as informações do perfil do usuário da IQ Option."""
    if trader and trader.is_connected():
        return jsonify({
            "status": "sucesso",
            "data": trader.get_profile()
        })
    return jsonify({"status": "erro", "mensagem": "Trader não conectado"}), 503

@app.route('/balance', methods=['GET'])
def get_balance():
    """Retorna o saldo da conta."""
    if trader and trader.is_connected():
        return jsonify({
            "status": "sucesso",
            "balance": trader.get_balance()
        })
    return jsonify({"status": "erro", "mensagem": "Trader não conectado"}), 503

@app.route('/get_candles', methods=['GET'])
def get_candles_route():
    """Busca velas (candles) para um ativo específico."""
    ativo = request.args.get('ativo', 'EURUSD-OTC')
    timeframe = int(request.args.get('timeframe', 1))
    quantidade = int(request.args.get('quantidade', 10))
    
    if trader and trader.is_connected():
        velas = trader.get_candles(ativo, timeframe, quantidade)
        return jsonify({
            "status": "sucesso",
            "ativo": ativo,
            "data": velas
        })
    return jsonify({"status": "erro", "mensagem": "Trader não conectado"}), 503

# --- NOVO ENDPOINT PARA GERAR GRÁFICO ---
@app.route('/grafico', methods=['GET'])
def rota_get_grafico():
    """Gera e retorna uma imagem de gráfico de candlestick para um ativo."""
    if not (trader and trader.is_connected()):
        return jsonify({"status": "erro", "mensagem": "Trader não conectado"}), 503

    try:
        # 1. Obter parâmetros da requisição
        ativo = request.args.get('ativo', 'EURUSD-OTC')
        timeframe = int(request.args.get('timeframe', 1))  # Em minutos
        quantidade = int(request.args.get('quantidade', 100))  # Número de velas

        logging.info(f"Gerando gráfico para {ativo}, timeframe {timeframe}m, quantidade {quantidade}")

        # 2. Buscar os dados dos candles
        velas_raw = trader.get_candles(ativo, timeframe, quantidade)
        if not velas_raw:
            return jsonify({"status": "erro", "mensagem": "Não foi possível obter os dados das velas."}), 404

        # 3. Processar os dados com Pandas
        df = pd.DataFrame(velas_raw)
        df['from'] = pd.to_datetime(df['from'], unit='s')
        df.rename(columns={
            'from': 'Datetime', 'open': 'Open', 'high': 'High',
            'low': 'Low', 'close': 'Close'
        }, inplace=True)
        df.set_index('Datetime', inplace=True)

        # 4. Gerar o gráfico com Matplotlib
        fig, ax = plt.subplots(figsize=(12, 6), facecolor='#0d1117')
        ax.set_facecolor('#0d1117')

        # Ajusta a largura do candle com base no timeframe para melhor visualização
        width = (df.index[1] - df.index[0]) * 0.6
        width2 = width * 0.1

        up = df[df.Close >= df.Open]
        down = df[df.Close < df.Open]

        # Cores para tema escuro
        up_color = '#26a69a'
        down_color = '#ef5350'
        text_color = '#c9d1d9'
        border_color = '#21262d'

        # Plotar velas de alta e baixa
        ax.bar(up.index, up.Close - up.Open, width, bottom=up.Open, color=up_color)
        ax.bar(up.index, up.High - up.Close, width2, bottom=up.Close, color=up_color, align='center')
        ax.bar(up.index, up.Low - up.Open, width2, bottom=up.Open, color=up_color, align='center')
        ax.bar(down.index, down.Close - down.Open, width, bottom=down.Open, color=down_color)
        ax.bar(down.index, down.High - down.Open, width2, bottom=down.Open, color=down_color, align='center')
        ax.bar(down.index, down.Low - down.Close, width2, bottom=down.Close, color=down_color, align='center')

        # Formatação e estilo
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

        # 5. Salvar a imagem em um buffer de memória
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor=fig.get_facecolor(), edgecolor='none', dpi=100)
        buf.seek(0)
        plt.close(fig)

        # 6. Enviar a imagem como resposta
        return send_file(buf, mimetype='image/png')

    except Exception as e:
        logging.error(f"Erro ao gerar gráfico: {e}", exc_info=True)
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

# --- Execução do Servidor ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)