#!/usr/bin/env python3
"""
Teste específico da lógica do gerenciamento Torre MK
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'API'))

from gerenciamento import GerenciamentoTorreMK

def test_gerenciamento_especifico():
    # Configuração de teste
    config = {
        'wins_to_level_up': 3,  # 3 wins para subir de nível
        'loss_compensation': 1   # Perde 1 win por perda normal
    }
    
    banca_inicial = 60
    gerenciador = GerenciamentoTorreMK(banca_inicial, config)
    
    print("=== TESTE ESPECÍFICO DO GERENCIAMENTO ===")
    print(f"Banca inicial: ${banca_inicial}")
    print(f"Entrada nível 1: ${gerenciador.get_proxima_entrada()}")
    print()
    
    # Teste 1: Subir para nível 2
    print("--- TESTE 1: Subir para nível 2 ---")
    for i in range(3):
        entrada = gerenciador.get_proxima_entrada()
        nivel = gerenciador._get_level_from_wins(gerenciador.total_wins)
        print(f"Win {i+1}: Entrada ${entrada}, Nível {nivel}")
        gerenciador.processar_resultado('win', banca_inicial)
    
    entrada_lvl2 = gerenciador.get_proxima_entrada()
    nivel_atual = gerenciador._get_level_from_wins(gerenciador.total_wins)
    print(f"Após 3 wins: Entrada ${entrada_lvl2}, Nível {nivel_atual}")
    print()
    
    # Teste 2: Subir para nível 3
    print("--- TESTE 2: Subir para nível 3 ---")
    for i in range(3):
        entrada = gerenciador.get_proxima_entrada()
        nivel = gerenciador._get_level_from_wins(gerenciador.total_wins)
        print(f"Win {i+1}: Entrada ${entrada}, Nível {nivel}")
        gerenciador.processar_resultado('win', banca_inicial)
    
    entrada_lvl3 = gerenciador.get_proxima_entrada()
    nivel_atual = gerenciador._get_level_from_wins(gerenciador.total_wins)
    print(f"Após mais 3 wins: Entrada ${entrada_lvl3}, Nível {nivel_atual}")
    print()
    
    # Teste 3: Perder com 0 wins no nível 3
    print("--- TESTE 3: Perder com 0 wins no nível 3 ---")
    entrada_antes = gerenciador.get_proxima_entrada()
    nivel_antes = gerenciador._get_level_from_wins(gerenciador.total_wins)
    wins_no_nivel = gerenciador.total_wins % config['wins_to_level_up']
    print(f"Antes da perda: Entrada ${entrada_antes}, Nível {nivel_antes}, Wins no nível: {wins_no_nivel}")
    
    gerenciador.processar_resultado('lose', banca_inicial)
    
    entrada_depois = gerenciador.get_proxima_entrada()
    nivel_depois = gerenciador._get_level_from_wins(gerenciador.total_wins)
    print(f"Após perda: Entrada ${entrada_depois}, Nível {nivel_depois}, Total wins: {gerenciador.total_wins}")
    print()
    
    # Verificação final
    print("--- VERIFICAÇÃO FINAL ---")
    print(f"Entrada nível 1: ${gerenciador.level_entries.get(1, 'N/A')}")
    print(f"Entrada nível 2: ${gerenciador.level_entries.get(2, 'N/A')}")
    print(f"Entrada nível 3: ${gerenciador.level_entries.get(3, 'N/A')}")
    print(f"Todas as entradas: {gerenciador.level_entries}")

if __name__ == "__main__":
    test_gerenciamento_especifico() 