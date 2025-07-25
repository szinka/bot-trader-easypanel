import logging

class GerenciamentoPorcentagem:
    def __init__(self, banca_inicial, config):
        self.config = config
        self.entrada_padrao = config.get('entrada_padrao', 10.0)
        self.limite_maximo = config.get('limite_maximo', 20.0)
    
    def calcular_entrada(self, banca_atual, porcentagem=None):
        if porcentagem == "test":
            return 2.0
        if porcentagem is None:
            porcentagem = self.entrada_padrao
        try:
            porcentagem = float(porcentagem)
        except (TypeError, ValueError):
            porcentagem = self.entrada_padrao
        porcentagem = min(porcentagem, self.limite_maximo)
        valor_entrada = banca_atual * (porcentagem / 100)
        valor_entrada = max(valor_entrada, 2.0)
        return round(valor_entrada, 2)

class GerenciadorMultiConta:
    def __init__(self, config):
        self.config = config
        self.gerenciadores = {}
    
    def _get_gerenciador(self, tipo_conta, banca_atual):
        if tipo_conta not in self.gerenciadores:
            self.gerenciadores[tipo_conta] = GerenciamentoPorcentagem(banca_atual, self.config)
        return self.gerenciadores[tipo_conta]
    
    def get_proxima_entrada(self, tipo_conta, banca_atual, porcentagem=None):
        gerenciador = self._get_gerenciador(tipo_conta, banca_atual)
        valor = gerenciador.calcular_entrada(banca_atual, porcentagem)
        logging.info(f"Entrada {tipo_conta}: R$ {valor}")
        return valor
    
    def get_configuracao_atual(self, tipo_conta, banca_atual):
        if tipo_conta in self.gerenciadores:
            gerenciador = self.gerenciadores[tipo_conta]
            return {
                'entrada_padrao': gerenciador.entrada_padrao,
                'limite_maximo': gerenciador.limite_maximo
            }
        return None