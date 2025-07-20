#!/usr/bin/env python3
"""
Teste da lógica corrigida do gerenciamento Torre MK
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'API'))

from gerenciamento import GerenciamentoTorreMK

def test_gerenciamento_corrigido():
    # Configuração de teste
    config = {
        'wins_to_level_up': 3,  # 3 wins para subir de nível
        'loss_compensation': 1   # Perde 1 win por perda normal
    }
    
    banca_inicial = 60
    gerenciador = GerenciamentoTorreMK(banca_inicial, config)
    
    print("=== TESTE DO GERENCIAMENTO CORRIGIDO ===")
    print(f"Banca inicial: ${banca_inicial}")
    print(f"Entrada nível 1: ${gerenciador.get_proxima_entrada()}")
    print()
    
    # Simulação de sequência de resultados
    resultados = ['win', 'win', 'win', 'win', 'win', 'win', 'lose', 'win', 'lose']
    
    for i, resultado in enumerate(resultados, 1):
        entrada_atual = gerenciador.get_proxima_entrada()
        nivel_atual = gerenciador._get_level_from_wins(gerenciador.total_wins)
        wins_no_nivel = gerenciador.total_wins % config['wins_to_level_up']
        
        print(f"Operação {i}: {resultado.upper()}")
        print(f"  Nível atual: {nivel_atual}")
        print(f"  Wins no nível: {wins_no_nivel}")
        print(f"  Entrada atual: ${entrada_atual}")
        print(f"  Total wins: {gerenciador.total_wins}")
        
        gerenciador.processar_resultado(resultado, banca_inicial)
        
        nova_entrada = gerenciador.get_proxima_entrada()
        novo_nivel = gerenciador._get_level_from_wins(gerenciador.total_wins)
        
        print(f"  → Nova entrada: ${nova_entrada}")
        print(f"  → Novo nível: {novo_nivel}")
        print(f"  → Total wins após: {gerenciador.total_wins}")
        print(f"  → Entradas por nível: {gerenciador.level_entries}")
        print()

if __name__ == "__main__":
    test_gerenciamento_corrigido() 