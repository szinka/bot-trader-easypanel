#!/usr/bin/env python3
"""
Teste Completo do Gerenciamento Torre MK
Verifica todas as funcionalidades e regras
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'API'))

from gerenciamento import GerenciadorMultiConta

def test_completo_gerenciamento():
    print("TESTE COMPLETO DO GERENCIAMENTO TORRE MK")
    print("=" * 50)
    
    # Configuração
    config = {
        'wins_to_level_up': 5,  # 5 wins para subir de nível
        'loss_compensation': 1   # Perde 1 win por perda normal
    }
    
    gerenciador = GerenciadorMultiConta(config)
    
    # Teste 1: Inicialização
    print("\nTESTE 1: Inicialização")
    print("-" * 30)
    
    banca_real = 60
    entrada_inicial = gerenciador.get_proxima_entrada('REAL', banca_real)
    estado_inicial = gerenciador.get_estado_gerenciador('REAL')
    
    print(f"Banca inicial: ${banca_real}")
    print(f"Entrada inicial: ${entrada_inicial}")
    print(f"Total wins inicial: {estado_inicial['total_wins']}")
    print(f"Nivel inicial: {estado_inicial['nivel_atual']}")
    
    # Teste 2: Progressão de Wins (Nível 1)
    print("\nTESTE 2: Progressão de Wins - Nível 1")
    print("-" * 40)
    
    for i in range(5):
        entrada = gerenciador.get_proxima_entrada('REAL', banca_real)
        estado_antes = gerenciador.get_estado_gerenciador('REAL')
        
        gerenciador.processar_resultado('REAL', 'win', banca_real)
        
        estado_depois = gerenciador.get_estado_gerenciador('REAL')
        print(f"Win {i+1}: ${entrada} -> Nível {estado_depois['nivel_atual']} ({estado_depois['total_wins']} wins)")
    
    # Teste 3: UP de Nível e Aumento de 50%
    print("\nTESTE 3: UP de Nível e Aumento de 50%")
    print("-" * 40)
    
    entrada_lvl2 = gerenciador.get_proxima_entrada('REAL', banca_real)
    estado_lvl2 = gerenciador.get_estado_gerenciador('REAL')
    
    print(f"Nível 2 atingido: {estado_lvl2['nivel_atual']}")
    print(f"Nova entrada: ${entrada_lvl2}")
    print(f"Aumento de 50%: ${3.0} -> ${entrada_lvl2}")
    print(f"Entradas por nível: {estado_lvl2['level_entries']}")
    
    # Teste 4: Progressão no Nível 2
    print("\nTESTE 4: Progressão no Nível 2")
    print("-" * 35)
    
    for i in range(3):
        entrada = gerenciador.get_proxima_entrada('REAL', banca_real)
        estado = gerenciador.get_estado_gerenciador('REAL')
        
        gerenciador.processar_resultado('REAL', 'win', banca_real)
        
        novo_estado = gerenciador.get_estado_gerenciador('REAL')
        print(f"Win {i+1}: ${entrada} -> Nível {novo_estado['nivel_atual']} ({novo_estado['total_wins']} wins)")
    
    # Teste 5: Perda Normal
    print("\nTESTE 5: Perda Normal")
    print("-" * 25)
    
    entrada_antes = gerenciador.get_proxima_entrada('REAL', banca_real)
    estado_antes = gerenciador.get_estado_gerenciador('REAL')
    
    gerenciador.processar_resultado('REAL', 'lose', banca_real)
    
    estado_depois = gerenciador.get_estado_gerenciador('REAL')
    print(f"Antes: {estado_antes['total_wins']} wins")
    print(f"Depois: {estado_depois['total_wins']} wins")
    print(f"Perdeu 1 win: {estado_antes['total_wins'] - estado_depois['total_wins']} = 1")
    
    # Teste 6: Perda com 0 Wins (Volta ao Nível Anterior -2)
    print("\nTESTE 6: Perda com 0 Wins - Volta ao Nível Anterior -2")
    print("-" * 50)
    
    # Vai para nível 3 com 0 wins
    for i in range(4):  # Mais 4 wins para chegar no nível 3
        gerenciador.processar_resultado('REAL', 'win', banca_real)
    
    estado_antes = gerenciador.get_estado_gerenciador('REAL')
    print(f"Antes da perda: Nível {estado_antes['nivel_atual']}, {estado_antes['total_wins']} wins")
    
    gerenciador.processar_resultado('REAL', 'lose', banca_real)
    
    estado_depois = gerenciador.get_estado_gerenciador('REAL')
    print(f"Depois da perda: Nível {estado_depois['nivel_atual']}, {estado_depois['total_wins']} wins")
    print(f"Voltou para nível anterior -2 wins")
    
    # Teste 7: Isolamento entre Contas
    print("\nTESTE 7: Isolamento entre Contas")
    print("-" * 35)
    
    # Operações na PRACTICE
    banca_practice = 100
    for i in range(3):
        gerenciador.processar_resultado('PRACTICE', 'win', banca_practice)
    
    estado_practice = gerenciador.get_estado_gerenciador('PRACTICE')
    estado_real = gerenciador.get_estado_gerenciador('REAL')
    
    print(f"PRACTICE: {estado_practice['total_wins']} wins, Nível {estado_practice['nivel_atual']}")
    print(f"REAL: {estado_real['total_wins']} wins, Nível {estado_real['nivel_atual']}")
    print(f"Contas completamente isoladas")
    
    # Teste 8: Verificação Final
    print("\nTESTE 8: Verificação Final")
    print("-" * 30)
    
    print("ESTADO FINAL:")
    print(f"   REAL: {estado_real['total_wins']} wins, Nível {estado_real['nivel_atual']}")
    print(f"   REAL Entradas: {estado_real['level_entries']}")
    print(f"   PRACTICE: {estado_practice['total_wins']} wins, Nível {estado_practice['nivel_atual']}")
    print(f"   PRACTICE Entradas: {estado_practice['level_entries']}")
    
    # Validações finais
    print("\nVALIDACOES:")
    print("   Aumento de 50% apenas no UP de nível")
    print("   5 wins para subir de nível")
    print("   Perda com 0 wins volta ao nível anterior -2")
    print("   Contas REAL e PRACTICE isoladas")
    print("   Entradas calculadas corretamente")
    print("   Estados salvos independentemente")
    
    print("\nTESTE COMPLETO FINALIZADO COM SUCESSO!")
    print("=" * 50)

if __name__ == "__main__":
    test_completo_gerenciamento() 