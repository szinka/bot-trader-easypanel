# API/gerenciamento.py
import math
import logging

class GerenciamentoTorreMK:
    def __init__(self, banca_inicial, config):
        self.config = config
        self.total_wins = 0
        self.level_entries = {}
        
        # Entrada inicial baseada na banca inicial
        entry_lvl_1 = round(banca_inicial * 0.10, 2)  # 10% da banca inicial
        self.level_entries[1] = max(2.0, entry_lvl_1)  # Mínimo de R$ 2,00

    def _get_level_from_wins(self, wins):
        return math.floor(max(0, wins) / self.config['wins_to_level_up']) + 1

    def get_proxima_entrada(self):
        nivel_atual = self._get_level_from_wins(self.total_wins)
        entrada = self.level_entries.get(nivel_atual, 2.0)
        return max(2.0, entrada)  # Garante mínimo de R$ 2,00

    def processar_resultado(self, resultado, banca_atual):
        nivel_antigo = self._get_level_from_wins(self.total_wins)
        wins_no_nivel_atual = self.total_wins % self.config['wins_to_level_up']

        if resultado.lower() == 'win':
            self.total_wins += 1
            nivel_novo = self._get_level_from_wins(self.total_wins)
            
            # Se subiu de nível, calcula nova entrada com 50% de aumento
            if nivel_novo > nivel_antigo:
                entrada_anterior = self.level_entries.get(nivel_antigo, 2.0)
                nova_entrada = round(entrada_anterior * 1.5, 2)  # 50% de aumento
                nova_entrada = max(2.0, nova_entrada)  # Garante mínimo de R$ 2,00
                self.level_entries[nivel_novo] = nova_entrada
                logging.info(f"Subiu para nível {nivel_novo}, nova entrada: ${nova_entrada}")
        else:
            # Lógica de perda
            if wins_no_nivel_atual == 0:
                # Perdeu com 0 wins no nível atual, volta ao nível anterior -2 wins
                nivel_anterior = max(1, nivel_antigo - 1)
                wins_necessarios = (nivel_anterior - 1) * self.config['wins_to_level_up']
                self.total_wins = max(0, wins_necessarios - 2)
                logging.info(f"Perdeu com 0 wins no nível {nivel_antigo}, voltou para nível {nivel_anterior} -2 wins")
            else:
                # Perda normal, perde 1 win
                self.total_wins = max(0, self.total_wins - self.config['loss_compensation'])
        
        nivel_novo = self._get_level_from_wins(self.total_wins)

        # Remove entradas de níveis superiores se caiu de nível
        if nivel_novo < nivel_antigo:
            niveis_a_remover = [lvl for lvl in self.level_entries if lvl > nivel_novo]
            for lvl in niveis_a_remover:
                del self.level_entries[lvl]
            logging.info(f"Caiu para nível {nivel_novo}, removidas entradas dos níveis superiores")

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
                import database
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
            import database
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
            import database
            database.resetar_estado_gerenciamento(self.db_conn, tipo_conta)
        
        # Recria o gerenciador
        self._get_gerenciador(tipo_conta, banca_atual)
        logging.info(f"Gerenciador resetado para {tipo_conta}")