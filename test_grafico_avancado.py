#!/usr/bin/env python3
"""
Script de teste para verificar o endpoint /grafico com as melhorias
"""

import requests
import json
import time

def test_grafico_endpoint():
    """Testa o endpoint /grafico com diferentes parâmetros"""
    
    base_url = "http://localhost:5000"
    
    # Teste 1: Gráfico básico
    print("=== Teste 1: Gráfico básico ===")
    try:
        response = requests.get(f"{base_url}/grafico?ativo=EURUSD-OTC&timeframe=1&quantidade=50")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            print("✅ Gráfico gerado com sucesso!")
            # Salva a imagem para verificar
            with open("teste_grafico_avancado.png", "wb") as f:
                f.write(response.content)
            print("📁 Imagem salva como 'teste_grafico_avancado.png'")
        else:
            print(f"❌ Erro: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Servidor não está rodando! Execute: python main.py")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Teste 2: Verificar se há outros endpoints de gráfico
    print("=== Teste 2: Verificar endpoints disponíveis ===")
    try:
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Servidor está rodando")
        else:
            print(f"❌ Erro no servidor: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Servidor não está rodando!")
    except Exception as e:
        print(f"❌ Erro: {e}")

def test_get_candles():
    """Testa o endpoint /get_candles para verificar os dados"""
    
    base_url = "http://localhost:5000"
    
    print("=== Teste 3: Verificar dados dos candles ===")
    try:
        data = {
            "ativo": "EURUSD-OTC",
            "timeframe": 1,
            "quantidade": 50
        }
        
        response = requests.post(f"{base_url}/get_candles", json=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "sucesso":
                velas = result.get("velas", [])
                print(f"✅ {len(velas)} candles obtidos")
                
                if velas:
                    # Verifica a estrutura dos dados
                    primeiro_candle = velas[0]
                    print(f"📊 Estrutura do primeiro candle:")
                    for key, value in primeiro_candle.items():
                        print(f"  {key}: {value}")
                    
                    # Verifica se há volume
                    volumes = [v.get('volume', 0) for v in velas]
                    volumes_nao_zero = [v for v in volumes if v > 0]
                    print(f"📈 Volume: {len(volumes_nao_zero)}/{len(volumes)} candles com volume > 0")
                    
                    # Verifica high/low
                    highs = [v.get('high', 0) for v in velas]
                    lows = [v.get('low', 0) for v in velas]
                    highs_nao_zero = [h for h in highs if h > 0]
                    lows_nao_zero = [l for l in lows if l > 0]
                    print(f"📊 High/Low válidos: {len(highs_nao_zero)}/{len(highs)} highs, {len(lows_nao_zero)}/{len(lows)} lows")
                    
            else:
                print(f"❌ Erro na API: {result.get('mensagem')}")
        else:
            print(f"❌ Erro HTTP: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Servidor não está rodando!")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("🔍 Testando endpoint /grafico com melhorias avançadas...")
    print("="*50)
    
    test_grafico_endpoint()
    test_get_candles()
    
    print("\n🎯 Resumo:")
    print("- Se o servidor não estiver rodando, execute: python main.py")
    print("- Se houver erros nos dados, verifique o endpoint /get_candles")
    print("- Se o gráfico não mostrar os 5 painéis, verifique o código do endpoint /grafico") 