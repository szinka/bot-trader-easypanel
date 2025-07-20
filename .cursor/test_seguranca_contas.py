#!/usr/bin/env python3
"""
Teste de segurança - Demonstra que contas REAL e PRACTICE estão separadas
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'API'))

from gerenciamento import GerenciadorMultiConta

def test_seguranca_contas():
    # Configuração de teste
    config = {
        'wins_to_level_up': 5,  # 5 wins para subir de nível
        'loss_compensation': 1   # Perde 1 win por perda normal
    }
    
    # Cria gerenciador multi-conta
    gerenciador = GerenciadorMultiConta(config)
    
    print("=== TESTE DE SEGURANÇA - CONTAS SEPARADAS ===")
    print()
    
    # Simula operações na conta PRACTICE
    print("--- CONTA PRACTICE ---")
    banca_practice = 100
    print(f"Banca PRACTICE: ${banca_practice}")
    
    # 3 wins na PRACTICE
    for i in range(3):
        entrada = gerenciador.get_proxima_entrada('PRACTICE', banca_practice)
        gerenciador.processar_resultado('PRACTICE', 'win', banca_practice)
        estado = gerenciador.get_estado_gerenciador('PRACTICE')
        print(f"Win {i+1} PRACTICE: Entrada ${entrada}, Total wins: {estado['total_wins']}, Nível: {estado['nivel_atual']}")
    
    print()
    
    # Simula operações na conta REAL
    print("--- CONTA REAL ---")
    banca_real = 60
    print(f"Banca REAL: ${banca_real}")
    
    # 7 wins na REAL (vai subir para nível 2)
    for i in range(7):
        entrada = gerenciador.get_proxima_entrada('REAL', banca_real)
        gerenciador.processar_resultado('REAL', 'win', banca_real)
        estado = gerenciador.get_estado_gerenciador('REAL')
        print(f"Win {i+1} REAL: Entrada ${entrada}, Total wins: {estado['total_wins']}, Nível: {estado['nivel_atual']}")
    
    print()
    
    # Verifica estados finais
    print("--- ESTADOS FINAIS ---")
    
    estado_practice = gerenciador.get_estado_gerenciador('PRACTICE')
    estado_real = gerenciador.get_estado_gerenciador('REAL')
    
    print(f"PRACTICE - Total wins: {estado_practice['total_wins']}, Nível: {estado_practice['nivel_atual']}")
    print(f"PRACTICE - Entradas: {estado_practice['level_entries']}")
    print()
    print(f"REAL - Total wins: {estado_real['total_wins']}, Nível: {estado_real['nivel_atual']}")
    print(f"REAL - Entradas: {estado_real['level_entries']}")
    print()
    
    # Teste de isolamento - perda na PRACTICE não afeta REAL
    print("--- TESTE DE ISOLAMENTO ---")
    print("Perdendo na PRACTICE...")
    entrada_practice = gerenciador.get_proxima_entrada('PRACTICE', banca_practice)
    gerenciador.processar_resultado('PRACTICE', 'lose', banca_practice)
    estado_practice_apos = gerenciador.get_estado_gerenciador('PRACTICE')
    
    print(f"PRACTICE após perda - Total wins: {estado_practice_apos['total_wins']}, Nível: {estado_practice_apos['nivel_atual']}")
    print(f"REAL continua igual - Total wins: {estado_real['total_wins']}, Nível: {estado_real['nivel_atual']}")
    
    # Verifica se REAL não foi afetada
    estado_real_verificacao = gerenciador.get_estado_gerenciador('REAL')
    if estado_real['total_wins'] == estado_real_verificacao['total_wins']:
        print("✅ SEGURANÇA GARANTIDA: Conta REAL não foi afetada pela perda na PRACTICE")
    else:
        print("❌ ERRO: Conta REAL foi afetada!")

if __name__ == "__main__":
    test_seguranca_contas() 