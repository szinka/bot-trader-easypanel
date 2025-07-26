
import pytest
from API.gerenciamento import GerenciadorMultiConta

def test_entrada_nivel_baixo():
    config = {}
    gerenciador = GerenciadorMultiConta(config)
    banca = 25  # Banca entre 0-30
    valor = gerenciador.get_proxima_entrada('PRACTICE', banca)
    assert valor == 2.0  # Nível 0-30 = R$ 2,00

def test_entrada_nivel_medio():
    config = {}
    gerenciador = GerenciadorMultiConta(config)
    banca = 50  # Banca entre 45-60
    valor = gerenciador.get_proxima_entrada('PRACTICE', banca)
    assert valor == 4.5  # Nível 45-60 = R$ 4,50

def test_entrada_nivel_alto():
    config = {}
    gerenciador = GerenciadorMultiConta(config)
    banca = 150  # Banca entre 120-170
    valor = gerenciador.get_proxima_entrada('PRACTICE', banca)
    assert valor == 12.0  # Nível 120-170 = R$ 12,00

def test_entrada_nivel_muito_alto():
    config = {}
    gerenciador = GerenciadorMultiConta(config)
    banca = 25000  # Banca acima de 23000
    valor = gerenciador.get_proxima_entrada('PRACTICE', banca)
    assert valor == 1500.0  # Nível 23000+ = R$ 1500,00

def test_entrada_limite_inferior():
    config = {}
    gerenciador = GerenciadorMultiConta(config)
    banca = 30  # Banca exatamente no limite inferior do nível 30-45
    valor = gerenciador.get_proxima_entrada('PRACTICE', banca)
    assert valor == 3.0  # Nível 30-45 = R$ 3,00

def test_entrada_limite_superior():
    config = {}
    gerenciador = GerenciadorMultiConta(config)
    banca = 44.99  # Banca logo abaixo do limite superior do nível 30-45
    valor = gerenciador.get_proxima_entrada('PRACTICE', banca)
    assert valor == 3.0  # Nível 30-45 = R$ 3,00

def test_processar_resultado():
    config = {}
    gerenciador = GerenciadorMultiConta(config)
    banca = 100
    gerenciador.processar_resultado('PRACTICE', 'win', banca)
    gerenciador.processar_resultado('PRACTICE', 'lose', banca)
    estado = gerenciador.get_estado_gerenciador('PRACTICE')
    assert estado['wins'] == 1
    assert estado['losses'] == 1
    assert estado['total_trades'] == 2
    assert estado['winrate'] == 50.0

def test_resetar_gerenciador():
    config = {}
    gerenciador = GerenciadorMultiConta(config)
    banca = 100
    gerenciador.processar_resultado('PRACTICE', 'win', banca)
    gerenciador.resetar_gerenciador('PRACTICE', banca)
    estado = gerenciador.get_estado_gerenciador('PRACTICE')
    assert estado['wins'] == 0
    assert estado['losses'] == 0
    assert estado['total_trades'] == 0
    assert estado['winrate'] == 0.0 