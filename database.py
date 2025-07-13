# database.py
import psycopg2
import logging
import json

# URL de conexão que você forneceu
DATABASE_URL = "postgres://teste:dbfafd3ad79f44b4da88@chatwoot_teste:5432/teste?sslmode=disable"

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        logging.error(f"ERRO CRÍTICO AO CONECTAR AO DB: {e}")
        return None

def setup_database(conn):
    """Cria as tabelas 'trades' и 'estado_gerenciamento' se elas não existirem."""
    if not conn: return
    
    commands = (
        """
        CREATE TABLE IF NOT EXISTS estado_gerenciamento (
            id INT PRIMARY KEY DEFAULT 1,
            total_wins INTEGER NOT NULL,
            level_entries_json TEXT NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS trades (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
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

def carregar_estado(conn):
    """Carrega o último estado do gerenciador a partir do banco de dados."""
    if not conn: return None
    
    sql = "SELECT total_wins, level_entries_json FROM estado_gerenciamento WHERE id = 1;"
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            estado = cur.fetchone()
            if estado:
                total_wins, level_entries_json = estado
                level_entries = {int(k): v for k, v in json.loads(level_entries_json).items()}
                logging.info(f"Estado do gerenciamento carregado do DB. total_wins: {total_wins}")
                return total_wins, level_entries
    except Exception as e:
        logging.error(f"Erro ao carregar estado do DB: {e}")
    
    logging.info("Nenhum estado salvo encontrado. Começando um novo.")
    return None

def salvar_estado(conn, total_wins, level_entries):
    """Salva (ou atualiza) o estado atual do gerenciador no banco de dados."""
    if not conn: return
    level_entries_json = json.dumps(level_entries)
    
    sql = """
        INSERT INTO estado_gerenciamento (id, total_wins, level_entries_json)
        VALUES (1, %s, %s)
        ON CONFLICT (id) DO UPDATE 
        SET total_wins = EXCLUDED.total_wins,
            level_entries_json = EXCLUDED.level_entries_json;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (total_wins, level_entries_json))
        conn.commit()
        logging.info(f"Estado do gerenciamento salvo no DB. total_wins: {total_wins}")
    except Exception as e:
        logging.error(f"Erro ao salvar estado no DB: {e}")
        conn.rollback()

def salvar_trade(conn, trade_info):
    """Salva os detalhes de um trade concluído no banco de dados."""
    if not conn: return
    
    sql = """
        INSERT INTO trades (ativo, acao, resultado, lucro, valor_investido, saldo_final)
        VALUES (%(ativo)s, %(acao)s, %(resultado)s, %(lucro)s, %(valor_investido)s, %(saldo_final)s);
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, trade_info)
        conn.commit()
        logging.info(f"Trade salvo no DB: {trade_info['resultado']}")
    except Exception as e:
        logging.error(f"Erro ao salvar trade no DB: {e}")
        conn.rollback()