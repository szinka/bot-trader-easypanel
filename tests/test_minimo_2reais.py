#!/usr/bin/env python3
"""
Teste do mínimo de R$ 2,00 no gerenciamento
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'API'))

from gerenciamento import GerenciamentoTorreMK

def test_minimo_2reais():
    # Configuração de teste
    config = {
        'wins_to_level_up': 5,  # 5 wins para subir de nível
        'loss_compensation': 1   # Perde 1 win por perda normal
    }
    
    print("TESTE DO MÍNIMO DE R$ 2,00 NO GERENCIAMENTO")
    print("=" * 50)
    
    # Teste 1: Banca pequena (deve resultar em R$ 2,00 mínimo)
    print("\nTESTE 1: Banca pequena - deve resultar em R$ 2,00 mínimo")
    print("-" * 55)
    
    banca_pequena = 10  # 10% de 10 = 1, mas deve ser 2
    gerenciador_pequeno = GerenciamentoTorreMK(banca_pequena, config)
    
    entrada_pequena = gerenciador_pequeno.get_proxima_entrada()
    print(f"Banca: ${banca_pequena}")
    print(f"10% da banca: ${banca_pequena * 0.10}")
    print(f"Entrada calculada: ${entrada_pequena}")
    
    if entrada_pequena >= 2.0:
        print("✅ Mínimo de R$ 2,00 respeitado")
    else:
        print(f"❌ Mínimo não respeitado: ${entrada_pequena}")
    
    # Teste 2: Banca média (deve resultar em valor maior que R$ 2,00)
    print("\nTESTE 2: Banca média - deve resultar em valor maior que R$ 2,00")
    print("-" * 55)
    
    banca_media = 30  # 10% de 30 = 3
    gerenciador_medio = GerenciamentoTorreMK(banca_media, config)
    
    entrada_media = gerenciador_medio.get_proxima_entrada()
    print(f"Banca: ${banca_media}")
    print(f"10% da banca: ${banca_media * 0.10}")
    print(f"Entrada calculada: ${entrada_media}")
    
    if entrada_media >= 2.0:
        print("✅ Mínimo de R$ 2,00 respeitado")
    else:
        print(f"❌ Mínimo não respeitado: ${entrada_media}")
    
    # Teste 3: Progressão com banca pequena
    print("\nTESTE 3: Progressão com banca pequena")
    print("-" * 40)
    
    # Simula 5 wins para subir para nível 2
    for i in range(5):
        gerenciador_pequeno.processar_resultado('win', banca_pequena)
    
    entrada_lvl2 = gerenciador_pequeno.get_proxima_entrada()
    nivel_atual = gerenciador_pequeno._get_level_from_wins(gerenciador_pequeno.total_wins)
    
    print(f"Após 5 wins:")
    print(f"  Nível atual: {nivel_atual}")
    print(f"  Entrada nível 2: ${entrada_lvl2}")
    print(f"  Aumento de 50%: ${2.0} → ${entrada_lvl2}")
    
    # Verificar se o aumento de 50% está correto e respeita o mínimo
    if entrada_lvl2 == 3.0:  # 2.0 * 1.5 = 3.0
        print("✅ Aumento de 50% correto e respeita mínimo")
    else:
        print(f"❌ Aumento incorreto: esperado $3.00, obtido ${entrada_lvl2}")
    
    # Teste 4: Mais 5 wins para nível 3
    print("\nTESTE 4: Subir para nível 3")
    print("-" * 30)
    
    for i in range(5):
        gerenciador_pequeno.processar_resultado('win', banca_pequena)
    
    entrada_lvl3 = gerenciador_pequeno.get_proxima_entrada()
    nivel_atual = gerenciador_pequeno._get_level_from_wins(gerenciador_pequeno.total_wins)
    
    print(f"Após mais 5 wins:")
    print(f"  Nível atual: {nivel_atual}")
    print(f"  Entrada nível 3: ${entrada_lvl3}")
    print(f"  Aumento de 50%: ${3.0} → ${entrada_lvl3}")
    
    # Verificar se o aumento de 50% está correto
    if entrada_lvl3 == 4.5:  # 3.0 * 1.5 = 4.5
        print("✅ Aumento de 50% correto")
    else:
        print(f"❌ Aumento incorreto: esperado $4.50, obtido ${entrada_lvl3}")
    
    # Teste 5: Verificar todas as entradas
    print("\nTESTE 5: Verificar todas as entradas")
    print("-" * 40)
    
    print("Entradas por nível:")
    for nivel, entrada in gerenciador_pequeno.level_entries.items():
        print(f"  Nível {nivel}: ${entrada}")
        if entrada < 2.0:
            print(f"    ❌ ERRO: Entrada ${entrada} abaixo do mínimo R$ 2,00")
        else:
            print(f"    ✅ Entrada ${entrada} respeita mínimo R$ 2,00")
    
    # Verificação final
    print("\nVERIFICAÇÃO FINAL:")
    print(f"  Banca inicial: ${banca_pequena}")
    print(f"  Entrada nível 1: ${gerenciador_pequeno.level_entries.get(1, 'N/A')}")
    print(f"  Entrada nível 2: ${gerenciador_pequeno.level_entries.get(2, 'N/A')}")
    print(f"  Entrada nível 3: ${gerenciador_pequeno.level_entries.get(3, 'N/A')}")
    
    # Verificar se todas as entradas respeitam o mínimo
    todas_respeitam = True
    for nivel, entrada in gerenciador_pequeno.level_entries.items():
        if entrada < 2.0:
            todas_respeitam = False
            break
    
    if todas_respeitam:
        print("✅ Todas as entradas respeitam o mínimo de R$ 2,00")
    else:
        print("❌ Algumas entradas não respeitam o mínimo de R$ 2,00")

if __name__ == "__main__":
    test_minimo_2reais() 