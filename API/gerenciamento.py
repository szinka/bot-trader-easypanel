# API/gerenciamento.py
import math
import logging
import os

class GerenciamentoTorreMK:
    def __init__(self, banca_inicial, config):
        self.config = config
        self.total_wins = 0
        self.level_entries = {}
        
        # Porcentagem do gerenciamento (padrão 5%, mas pode ser configurada via env)
        self.gerenciamento_percent = float(os.getenv('GERENCIAMENTO_PERCENT', 5.0))

        entry_lvl_1 = round(banca_inicial * (self.gerenciamento_percent / 100), 2)
        self.level_entries[1] = max(1.0, entry_lvl_1)

    def _get_level_from_wins(self, wins):
        return math.floor(max(0, wins) / self.config['wins_to_level_up']) + 1

    def get_proxima_entrada(self):
        nivel_atual = self._get_level_from_wins(self.total_wins)
        return self.level_entries.get(nivel_atual, 1.0)

    def processar_resultado(self, resultado, banca_atual):
        nivel_antigo = self._get_level_from_wins(self.total_wins)

        if resultado.lower() == 'win':
            self.total_wins += 1
        else:
            # Verifica se vai cair de nível
            wins_apos_loss_normal = max(0, self.total_wins - self.config['loss_compensation'])
            nivel_apos_loss_normal = self._get_level_from_wins(wins_apos_loss_normal)
            
            # Se vai cair de nível, perde 2 wins ao invés de 1
            if nivel_apos_loss_normal < nivel_antigo:
                self.total_wins = max(0, self.total_wins - 2)
            else:
                self.total_wins = max(0, self.total_wins - self.config['loss_compensation'])
        
        nivel_novo = self._get_level_from_wins(self.total_wins)

        if nivel_novo < nivel_antigo:
            niveis_a_remover = [lvl for lvl in self.level_entries if lvl > nivel_novo]
            for lvl in niveis_a_remover:
                del self.level_entries[lvl]
        
        if nivel_novo not in self.level_entries:
            percentual = self.gerenciamento_percent / 100
            nova_entrada = round(banca_atual * percentual, 2)
            self.level_entries[nivel_novo] = max(1.0, nova_entrada)

class GerenciadorMultiConta:
    """
    Gerencia múltiplos gerenciadores Torre MK, um para cada tipo de conta.
    Isola completamente o estado entre contas REAL e PRACTICE.
    """
    
    def __init__(self, config):
        self.config = config
        self.gerenciadores = {}  # Dicionário: {tipo_conta: GerenciamentoTorreMK}
        self.db_conn = None
    
    def set_db_connection(self, db_conn):
        """Define a conexão com o banco de dados."""
        self.db_conn = db_conn
    
    def _get_gerenciador(self, tipo_conta, banca_atual):
        """
        Obtém ou cria um gerenciador para o tipo de conta especificado.
        """
        if tipo_conta not in self.gerenciadores:
            # Cria novo gerenciador para este tipo de conta
            self.gerenciadores[tipo_conta] = GerenciamentoTorreMK(banca_atual, self.config)
            
            # Tenta carregar estado salvo do banco de dados
            if self.db_conn:
                from . import database
                estado_salvo = database.carregar_estado(self.db_conn, tipo_conta)
                if estado_salvo:
                    self.gerenciadores[tipo_conta].total_wins, self.gerenciadores[tipo_conta].level_entries = estado_salvo
                    logging.info(f"Estado carregado para {tipo_conta}: {self.gerenciadores[tipo_conta].total_wins} wins")
                else:
                    logging.info(f"Novo gerenciador criado para {tipo_conta}")
        
        return self.gerenciadores[tipo_conta]
    
    def get_proxima_entrada(self, tipo_conta, banca_atual):
        """
        Obtém o próximo valor de entrada para o tipo de conta especificado.
        """
        gerenciador = self._get_gerenciador(tipo_conta, banca_atual)
        return gerenciador.get_proxima_entrada()
    
    def processar_resultado(self, tipo_conta, resultado, banca_atual):
        """
        Processa o resultado de uma operação para o tipo de conta especificado.
        """
        gerenciador = self._get_gerenciador(tipo_conta, banca_atual)
        gerenciador.processar_resultado(resultado, banca_atual)
        
        # Salva o estado no banco de dados
        if self.db_conn:
            from . import database
            database.salvar_estado(
                self.db_conn, 
                tipo_conta, 
                gerenciador.total_wins, 
                gerenciador.level_entries
            )
    
    def get_estado_gerenciador(self, tipo_conta):
        """
        Retorna o estado atual do gerenciador para o tipo de conta especificado.
        """
        if tipo_conta in self.gerenciadores:
            gerenciador = self.gerenciadores[tipo_conta]
            return {
                'total_wins': gerenciador.total_wins,
                'level_entries': gerenciador.level_entries,
                'nivel_atual': gerenciador._get_level_from_wins(gerenciador.total_wins)
            }
        return None
    
    def resetar_gerenciador(self, tipo_conta, banca_atual):
        """
        Reseta o gerenciador para o tipo de conta especificado.
        """
        if tipo_conta in self.gerenciadores:
            del self.gerenciadores[tipo_conta]
        
        # Remove do banco de dados
        if self.db_conn:
            from . import database
            database.resetar_estado_gerenciamento(self.db_conn, tipo_conta)
        
        # Recria o gerenciador
        self._get_gerenciador(tipo_conta, banca_atual)
        logging.info(f"Gerenciador resetado para {tipo_conta}")