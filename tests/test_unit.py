
import pytest
from API.gerenciamento import GerenciadorMultiConta

def test_entrada_padrao():
    config = {'entrada_padrao': 10.0, 'limite_maximo': 20.0}
    gerenciador = GerenciadorMultiConta(config)
    banca = 1000
    valor = gerenciador.get_proxima_entrada('PRACTICE', banca)
    assert valor == 100.0  # 10% de 1000

def test_entrada_customizada():
    config = {'entrada_padrao': 10.0, 'limite_maximo': 20.0}
    gerenciador = GerenciadorMultiConta(config)
    banca = 1000
    valor = gerenciador.get_proxima_entrada('PRACTICE', banca, 15)
    assert valor == 150.0  # 15% de 1000

def test_entrada_limite():
    config = {'entrada_padrao': 10.0, 'limite_maximo': 20.0}
    gerenciador = GerenciadorMultiConta(config)
    banca = 1000
    valor = gerenciador.get_proxima_entrada('PRACTICE', banca, 20)
    assert valor == 200.0  # 20% de 1000

def test_entrada_acima_limite():
    config = {'entrada_padrao': 10.0, 'limite_maximo': 20.0}
    gerenciador = GerenciadorMultiConta(config)
    banca = 1000
    valor = gerenciador.get_proxima_entrada('PRACTICE', banca, 50)
    assert valor == 200.0  # Limite de 20% de 1000

def test_entrada_minima():
    config = {'entrada_padrao': 10.0, 'limite_maximo': 20.0}
    gerenciador = GerenciadorMultiConta(config)
    banca = 10
    valor = gerenciador.get_proxima_entrada('PRACTICE', banca)
    assert valor == 2.0  # 10% de 10 seria 1, mas mínimo é 2 