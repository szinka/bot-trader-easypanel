# API/gerenciamento.py
import math

class GerenciamentoTorreMK:
    def __init__(self, banca_inicial, config):
        self.config = config
        self.total_wins = 0
        self.level_entries = {}

        entry_lvl_1 = round(banca_inicial * (self.config['entry_percentage'] / 100), 2)
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
            self.total_wins = max(0, self.total_wins - self.config['loss_compensation'])
        
        nivel_novo = self._get_level_from_wins(self.total_wins)

        if nivel_novo < nivel_antigo:
            niveis_a_remover = [lvl for lvl in self.level_entries if lvl > nivel_novo]
            for lvl in niveis_a_remover:
                del self.level_entries[lvl]
        
        if nivel_novo not in self.level_entries:
            percentual = self.config['entry_percentage'] / 100
            nova_entrada = round(banca_atual * percentual, 2)
            self.level_entries[nivel_novo] = max(1.0, nova_entrada)