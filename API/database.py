# API/database.py
import psycopg2
import logging
import json
import os

def get_db_connection():
    # Tenta usar DATABASE_URL primeiro, depois configurações individuais
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        try:
            conn = psycopg2.connect(database_url)
            return conn
        except psycopg2.OperationalError as e:
            logging.critical(f"ERRO CRÍTICO AO CONECTAR AO DB: {e}")
            return None
    
    # Configurações individuais do banco
    db_config = {
        'host': os.getenv('DB_HOST', 'easypanel.allkimy.academy'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_NAME', 'teste'),
        'user': os.getenv('DB_USER', 'teste'),
        'password': os.getenv('DB_PASSWORD', 'dbfafd3ad79f44b4da88')
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        return conn
    except psycopg2.OperationalError as e:
        logging.critical(f"ERRO CRÍTICO AO CONECTAR AO DB: {e}")
        return None

def setup_database(conn):
    if not conn: return
    commands = (
        """
        CREATE TABLE IF NOT EXISTS estado_gerenciamento (
            id SERIAL PRIMARY KEY,
            tipo_conta VARCHAR(10) NOT NULL UNIQUE,
            total_wins INTEGER NOT NULL DEFAULT 0,
            level_entries_json TEXT NOT NULL DEFAULT '{}',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS trades (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            tipo_conta VARCHAR(10) NOT NULL,
            ativo VARCHAR(255) NOT NULL,
            acao VARCHAR(10) NOT NULL,
            resultado VARCHAR(10) NOT NULL,
            lucro NUMERIC(12, 2) NOT NULL,
            valor_investido NUMERIC(12, 2) NOT NULL,
            saldo_final NUMERIC(12, 2) NOT NULL
        );
        """
    )
    try:
        with conn.cursor() as cur:
            for command in commands:
                cur.execute(command)
        conn.commit()
        logging.info("Tabelas do banco de dados prontas.")
    except Exception as e:
        logging.error(f"Erro ao configurar tabelas: {e}")
        conn.rollback()

def carregar_estado(conn, tipo_conta):
    if not conn: return None
    sql = "SELECT total_wins, level_entries_json FROM estado_gerenciamento WHERE tipo_conta = %s;"
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (tipo_conta,))
            estado = cur.fetchone()
            if estado:
                total_wins, level_entries_json = estado
                level_entries = {int(k): v for k, v in json.loads(level_entries_json).items()}
                logging.info(f"Estado do gerenciamento carregado do DB para {tipo_conta}. total_wins: {total_wins}")
                return total_wins, level_entries
    except Exception as e:
        logging.error(f"Erro ao carregar estado do DB para {tipo_conta}: {e}")
    logging.info(f"Nenhum estado salvo encontrado para {tipo_conta}. Começando um novo.")
    return None

def salvar_estado(conn, tipo_conta, total_wins, level_entries):
    if not conn: return
    level_entries_json = json.dumps(level_entries)
    sql = """
        INSERT INTO estado_gerenciamento (tipo_conta, total_wins, level_entries_json, updated_at)
        VALUES (%s, %s, %s, NOW())
        ON CONFLICT (tipo_conta) DO UPDATE 
        SET total_wins = EXCLUDED.total_wins,
            level_entries_json = EXCLUDED.level_entries_json,
            updated_at = NOW();
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (tipo_conta, total_wins, level_entries_json))
        conn.commit()
        logging.info(f"Estado do gerenciamento salvo no DB para {tipo_conta}. total_wins: {total_wins}")
    except Exception as e:
        logging.error(f"Erro ao salvar estado no DB para {tipo_conta}: {e}")
        conn.rollback()

def salvar_trade(conn, trade_info):
    if not conn: return
    sql = """
        INSERT INTO trades (tipo_conta, ativo, acao, resultado, lucro, valor_investido, saldo_final)
        VALUES (%(tipo_conta)s, %(ativo)s, %(acao)s, %(resultado)s, %(lucro)s, %(valor_investido)s, %(saldo_final)s);
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, trade_info)
        conn.commit()
        logging.info(f"Trade salvo no DB para {trade_info['tipo_conta']}: {trade_info['resultado']}")
    except Exception as e:
        logging.error(f"Erro ao salvar trade no DB: {e}")
        conn.rollback()

def get_historico_trades(conn, tipo_conta=None):
    """Busca todos os trades registrados no banco de dados, opcionalmente filtrado por tipo de conta."""
    if not conn: return []
    
    if tipo_conta:
        sql = "SELECT id, timestamp, tipo_conta, ativo, acao, resultado, lucro, valor_investido, saldo_final FROM trades WHERE tipo_conta = %s ORDER BY timestamp DESC;"
        params = (tipo_conta,)
    else:
        sql = "SELECT id, timestamp, tipo_conta, ativo, acao, resultado, lucro, valor_investido, saldo_final FROM trades ORDER BY timestamp DESC;"
        params = ()
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            trades = cur.fetchall()
            # Converte os resultados para uma lista de dicionários para facilitar o uso na API
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in trades]
    except Exception as e:
        logging.error(f"Erro ao buscar histórico de trades: {e}")
        return []

def resetar_historico_trades(conn, tipo_conta=None):
    """Apaga todos os registros da tabela de trades, opcionalmente filtrado por tipo de conta."""
    if not conn: return
    
    if tipo_conta:
        sql = "DELETE FROM trades WHERE tipo_conta = %s;"
        params = (tipo_conta,)
    else:
        sql = "TRUNCATE TABLE trades RESTART IDENTITY;"
        params = ()
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
        conn.commit()
        logging.info(f"Histórico de trades foi resetado para {tipo_conta if tipo_conta else 'todas as contas'}.")
    except Exception as e:
        logging.error(f"Erro ao resetar histórico de trades: {e}")
        conn.rollback()

def resetar_estado_gerenciamento(conn, tipo_conta=None):
    """Apaga o estado de gerenciamento salvo, opcionalmente filtrado por tipo de conta."""
    if not conn: return
    
    if tipo_conta:
        sql = "DELETE FROM estado_gerenciamento WHERE tipo_conta = %s;"
        params = (tipo_conta,)
    else:
        sql = "DELETE FROM estado_gerenciamento;"
        params = ()
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
        conn.commit()
        logging.info(f"Estado de gerenciamento foi resetado para {tipo_conta if tipo_conta else 'todas as contas'}.")
    except Exception as e:
        logging.error(f"Erro ao resetar estado de gerenciamento: {e}")
        conn.rollback()