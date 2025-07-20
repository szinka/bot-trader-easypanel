#!/usr/bin/env python3
"""
Teste do endpoint de reset do gerenciamento
"""

import requests
import json

def test_endpoint_reset():
    base_url = "http://localhost:8080"
    
    print("TESTE DO ENDPOINT DE RESET DO GERENCIAMENTO")
    print("=" * 50)
    
    # Teste 1: Reset do gerenciamento PRACTICE
    print("\nTESTE 1: Reset do gerenciamento PRACTICE")
    print("-" * 40)
    
    try:
        response = requests.post(
            f"{base_url}/resetar_gerenciamento",
            json={"tipo_conta": "PRACTICE"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data['status']}")
            print(f"Mensagem: {data['mensagem']}")
            print(f"Dados: {json.dumps(data['dados'], indent=2)}")
        else:
            print(f"Erro: {response.status_code}")
            print(f"Resposta: {response.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")
    
    # Teste 2: Reset do gerenciamento REAL
    print("\nTESTE 2: Reset do gerenciamento REAL")
    print("-" * 40)
    
    try:
        response = requests.post(
            f"{base_url}/resetar_gerenciamento",
            json={"tipo_conta": "REAL"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data['status']}")
            print(f"Mensagem: {data['mensagem']}")
            print(f"Dados: {json.dumps(data['dados'], indent=2)}")
        else:
            print(f"Erro: {response.status_code}")
            print(f"Resposta: {response.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")
    
    # Teste 3: Verificar estado após reset
    print("\nTESTE 3: Verificar estado após reset")
    print("-" * 40)
    
    try:
        response = requests.get(
            f"{base_url}/management?tipo_conta=PRACTICE"
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Estado do gerenciamento PRACTICE:")
            print(f"  Total wins: {data['estado']['total_wins']}")
            print(f"  Nível atual: {data['estado']['nivel_atual']}")
            print(f"  Entradas: {data['estado']['level_entries']}")
        else:
            print(f"Erro ao verificar estado: {response.status_code}")
    except Exception as e:
        print(f"Erro na requisição: {e}")

if __name__ == "__main__":
    test_endpoint_reset() 