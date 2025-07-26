import logging

class GerenciamentoNiveis:
    def __init__(self, banca_inicial, config):
        self.config = config
        # Sistema de níveis baseado na banca
        self.niveis_entrada = {
            (0, 30): 2.0,
            (30, 45): 3.0,
            (45, 60): 4.5,
            (60, 90): 6.0,
            (90, 120): 9.0,
            (120, 170): 12.0,
            (170, 230): 17.0,
            (230, 300): 23.0,
            (300, 450): 30.0,
            (450, 600): 45.0,
            (600, 900): 60.0,
            (900, 1200): 90.0,
            (1200, 1700): 120.0,
            (1700, 2300): 170.0,
            (2300, 3000): 230.0,
            (3000, 4500): 300.0,
            (4500, 6000): 300.0,
            (6000, 9000): 400.0,
            (9000, 12000): 600.0,
            (12000, 17000): 900.0,
            (17000, 23000): 1200.0,
            (23000, float('inf')): 1500.0
        }
        # Contadores para estatísticas
        self.wins = 0
        self.losses = 0
        self.banca_inicial = banca_inicial
    
    def calcular_entrada(self, banca_atual):
        # Encontra o nível correspondente à banca atual
        for (min_banca, max_banca), valor_entrada in self.niveis_entrada.items():
            if min_banca <= banca_atual < max_banca:
        return round(valor_entrada, 2)
        
        # Fallback para valores muito altos
        return 1500.0
    
    def processar_resultado(self, resultado, banca_atual):
        """Processa o resultado de um trade (win/lose)"""
        if resultado == 'win':
            self.wins += 1
        elif resultado == 'lose':
            self.losses += 1
        logging.info(f"Resultado processado: {resultado} - Wins: {self.wins}, Losses: {self.losses}")
    
    def get_estado(self):
        """Retorna o estado atual do gerenciador"""
        total_trades = self.wins + self.losses
        winrate = (self.wins / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'wins': self.wins,
            'losses': self.losses,
            'total_trades': total_trades,
            'winrate': round(winrate, 2),
            'sistema_niveis': True,
            'niveis_entrada': self.niveis_entrada
        }
    
    def resetar(self, banca_atual):
        """Reseta as estatísticas do gerenciador"""
        self.wins = 0
        self.losses = 0
        self.banca_inicial = banca_atual
        logging.info(f"Gerenciador resetado - Nova banca inicial: {banca_atual}")

class GerenciadorMultiConta:
    def __init__(self, config):
        self.config = config
        self.gerenciadores = {}
    
    def _get_gerenciador(self, tipo_conta, banca_atual):
        if tipo_conta not in self.gerenciadores:
            self.gerenciadores[tipo_conta] = GerenciamentoNiveis(banca_atual, self.config)
        return self.gerenciadores[tipo_conta]
    
    def get_proxima_entrada(self, tipo_conta, banca_atual):
        gerenciador = self._get_gerenciador(tipo_conta, banca_atual)
        valor = gerenciador.calcular_entrada(banca_atual)
        logging.info(f"Entrada {tipo_conta}: R$ {valor}")
        return valor
    
    def processar_resultado(self, tipo_conta, resultado, banca_atual):
        """Processa o resultado de um trade para uma conta específica"""
        gerenciador = self._get_gerenciador(tipo_conta, banca_atual)
        gerenciador.processar_resultado(resultado, banca_atual)
    
    def get_estado_gerenciador(self, tipo_conta):
        """Retorna o estado do gerenciador para uma conta específica"""
        if tipo_conta in self.gerenciadores:
            return self.gerenciadores[tipo_conta].get_estado()
        return None
    
    def resetar_gerenciador(self, tipo_conta, banca_atual):
        """Reseta o gerenciador para uma conta específica"""
        if tipo_conta in self.gerenciadores:
            self.gerenciadores[tipo_conta].resetar(banca_atual)
        else:
            self.gerenciadores[tipo_conta] = GerenciamentoNiveis(banca_atual, self.config)
    
    def get_configuracao_atual(self, tipo_conta, banca_atual):
        if tipo_conta in self.gerenciadores:
            gerenciador = self.gerenciadores[tipo_conta]
            return {
                'sistema_niveis': True,
                'niveis_entrada': gerenciador.niveis_entrada,
                'entrada_atual': gerenciador.calcular_entrada(banca_atual)
            }
        return None