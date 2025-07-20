
import sys
import os
import pytest

# Adiciona a raiz do projeto ao path para encontrar o módulo API
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from API.gerenciamento import GerenciadorMultiConta

# Configurações padrão para os testes
CONFIG = {
    'entry_percentage': 5.0,
    'wins_to_level_up': 2, # Usar 2 para facilitar o teste
    'loss_compensation': 1
}

@pytest.fixture
def gerenciador():
    """Cria uma instância fresca do gerenciador para cada teste."""
    return GerenciadorMultiConta(CONFIG)

def test_calculo_entrada_inicial(gerenciador):
    """Testa se o valor da primeira entrada é calculado corretamente."""
    banca = 1000
    tipo_conta = "PRACTICE"
    valor_esperado = banca * (CONFIG['entry_percentage'] / 100)
    
    valor_calculado = gerenciador.get_proxima_entrada(tipo_conta, banca)
    
    assert valor_calculado == valor_esperado
    
def test_subida_de_nivel_apos_wins(gerenciador):
    """Testa se o gerenciador sobe de nível após o número correto de wins."""
    banca = 1000
    tipo_conta = "PRACTICE"
    g = gerenciador._get_gerenciador(tipo_conta, banca)
    # Simula dois wins
    g.processar_resultado('win', banca)
    assert g._get_level_from_wins(g.total_wins) == 1
    g.processar_resultado('win', banca)
    assert g._get_level_from_wins(g.total_wins) == 2

def test_compensacao_de_loss(gerenciador):
    """Testa se uma perda compensa corretamente uma vitória."""
    banca = 1000
    tipo_conta = "PRACTICE"
    g = gerenciador._get_gerenciador(tipo_conta, banca)
    g.processar_resultado('win', banca)
    assert g.total_wins == 1
    g.processar_resultado('loss', banca)
    assert g.total_wins == 0

def test_nao_sobe_de_nivel_com_loss_intermediario(gerenciador):
    """Testa se o ciclo de wins é quebrado por um loss."""
    banca = 1000
    tipo_conta = "PRACTICE"
    g = gerenciador._get_gerenciador(tipo_conta, banca)
    g.processar_resultado('win', banca) # 1 win
    g.processar_resultado('loss', banca) # 0 win
    g.processar_resultado('win', banca) # 1 win
    assert g._get_level_from_wins(g.total_wins) == 1
    assert g.total_wins == 1 