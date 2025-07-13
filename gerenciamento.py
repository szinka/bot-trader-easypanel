# gerenciamento.py (Versão Final - Spec-Compliant)
import math

class GerenciamentoTorreMK:
    def __init__(self, banca_inicial, config):
        """
        Inicializa o gerenciador com base na especificação.
        """
        self.config = {
            'entry_percentage': config.get('entry_percentage', 10.0),
            'wins_to_level_up': config.get('wins_to_level_up', 5),
            'loss_compensation': config.get('loss_compensation', 1)
        }
        self.total_wins = 0
        self.level_entries = {} # Dicionário para armazenar as entradas de cada nível

        # Inicializa a entrada para o Nível 1, como manda a especificação
        entry_lvl_1 = round(banca_inicial * (self.config['entry_percentage'] / 100), 2)
        self.level_entries[1] = max(1.0, entry_lvl_1) # Garante que a entrada mínima seja $1

    def _get_level_from_wins(self, wins):
        """Calcula o nível com base em um número de vitórias."""
        return math.floor(max(0, wins) / self.config['wins_to_level_up']) + 1

    def get_proxima_entrada(self):
        """Retorna o valor da entrada para a operação atual."""
        nivel_atual = self._get_level_from_wins(self.total_wins)
        return self.level_entries.get(nivel_atual, 1.0) # Retorna $1 como padrão de segurança

    def processar_resultado(self, resultado, banca_atual):
        """
        Processa o resultado de um trade (win/loss) e atualiza o estado
        do gerenciamento para a próxima operação.
        """
        nivel_antigo = self._get_level_from_wins(self.total_wins)

        if resultado.lower() == 'win':
            self.total_wins += 1
        else: # loss ou empate
            self.total_wins = max(0, self.total_wins - self.config['loss_compensation'])
        
        nivel_novo = self._get_level_from_wins(self.total_wins)

        # Regra: Se houve queda de nível, apaga as entradas dos níveis superiores
        if nivel_novo < nivel_antigo:
            niveis_a_remover = [lvl for lvl in self.level_entries if lvl > nivel_novo]
            for lvl in niveis_a_remover:
                del self.level_entries[lvl]
        
        # Regra: Se o novo nível ainda não tem uma entrada definida, calcula e armazena
        if nivel_novo not in self.level_entries:
            percentual = self.config['entry_percentage'] / 100
            nova_entrada = round(banca_atual * percentual, 2)
            self.level_entries[nivel_novo] = max(1.0, nova_entrada)