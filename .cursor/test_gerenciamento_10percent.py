#!/usr/bin/env python3
"""
Teste do gerenciamento com 10% da banca
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'API'))

from gerenciamento import GerenciamentoTorreMK

def test_gerenciamento_10percent():
    # Configuração de teste
    config = {
        'wins_to_level_up': 5,  # 5 wins para subir de nível
        'loss_compensation': 1   # Perde 1 win por perda normal
    }
    
    banca_inicial = 60
    gerenciador = GerenciamentoTorreMK(banca_inicial, config)
    
    print("TESTE DO GERENCIAMENTO COM 10% DA BANCA")
    print("=" * 50)
    
    # Teste 1: Verificar entrada inicial
    print("\nTESTE 1: Entrada inicial com 10%")
    print("-" * 40)
    
    entrada_inicial = gerenciador.get_proxima_entrada()
    print(f"Banca inicial: ${banca_inicial}")
    print(f"Entrada inicial: ${entrada_inicial}")
    print(f"Porcentagem calculada: {(entrada_inicial/banca_inicial)*100:.1f}%")
    
    # Verificar se está correto (10% de 60 = 6)
    if entrada_inicial == 6.0:
        print("✅ Entrada inicial correta: 10% da banca")
    else:
        print(f"❌ Entrada inicial incorreta: esperado $6.00, obtido ${entrada_inicial}")
    
    # Teste 2: Progressão de níveis
    print("\nTESTE 2: Progressão de níveis")
    print("-" * 30)
    
    # Simula 5 wins para subir para nível 2
    for i in range(5):
        gerenciador.processar_resultado('win', banca_inicial)
    
    entrada_lvl2 = gerenciador.get_proxima_entrada()
    nivel_atual = gerenciador._get_level_from_wins(gerenciador.total_wins)
    
    print(f"Após 5 wins:")
    print(f"  Nível atual: {nivel_atual}")
    print(f"  Entrada nível 2: ${entrada_lvl2}")
    print(f"  Aumento de 50%: ${6.0} → ${entrada_lvl2}")
    
    # Verificar se o aumento de 50% está correto
    if entrada_lvl2 == 9.0:  # 6.0 * 1.5 = 9.0
        print("✅ Aumento de 50% correto")
    else:
        print(f"❌ Aumento incorreto: esperado $9.00, obtido ${entrada_lvl2}")
    
    # Teste 3: Mais 5 wins para nível 3
    print("\nTESTE 3: Subir para nível 3")
    print("-" * 30)
    
    for i in range(5):
        gerenciador.processar_resultado('win', banca_inicial)
    
    entrada_lvl3 = gerenciador.get_proxima_entrada()
    nivel_atual = gerenciador._get_level_from_wins(gerenciador.total_wins)
    
    print(f"Após mais 5 wins:")
    print(f"  Nível atual: {nivel_atual}")
    print(f"  Entrada nível 3: ${entrada_lvl3}")
    print(f"  Aumento de 50%: ${9.0} → ${entrada_lvl3}")
    
    # Verificar se o aumento de 50% está correto
    if entrada_lvl3 == 13.5:  # 9.0 * 1.5 = 13.5
        print("✅ Aumento de 50% correto")
    else:
        print(f"❌ Aumento incorreto: esperado $13.50, obtido ${entrada_lvl3}")
    
    # Teste 4: Verificar todas as entradas
    print("\nTESTE 4: Verificar todas as entradas")
    print("-" * 40)
    
    print("Entradas por nível:")
    for nivel, entrada in gerenciador.level_entries.items():
        print(f"  Nível {nivel}: ${entrada}")
    
    # Verificação final
    print("\nVERIFICAÇÃO FINAL:")
    print(f"  Banca inicial: ${banca_inicial}")
    print(f"  Entrada nível 1: ${gerenciador.level_entries.get(1, 'N/A')}")
    print(f"  Entrada nível 2: ${gerenciador.level_entries.get(2, 'N/A')}")
    print(f"  Entrada nível 3: ${gerenciador.level_entries.get(3, 'N/A')}")
    
    # Verificar se a progressão está correta
    entrada_lvl1 = gerenciador.level_entries.get(1, 0)
    entrada_lvl2 = gerenciador.level_entries.get(2, 0)
    entrada_lvl3 = gerenciador.level_entries.get(3, 0)
    
    if entrada_lvl1 == 6.0 and entrada_lvl2 == 9.0 and entrada_lvl3 == 13.5:
        print("✅ Progressão correta: 10% → +50% → +50%")
    else:
        print("❌ Progressão incorreta")

if __name__ == "__main__":
    test_gerenciamento_10percent() 