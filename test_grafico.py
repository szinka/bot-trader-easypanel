#!/usr/bin/env python3
"""
Script de teste para verificar o funcionamento do gráfico
"""

import requests
import json
import time

def test_grafico():
    """Testa o endpoint de gráfico"""
    base_url = "http://localhost:8080"
    
    print("🎯 Testando endpoint de gráfico...")
    
    try:
        # Teste 1: Gráfico básico
        print("\n📊 Testando /grafico...")
        params = {
            'ativo': 'EURUSD-OTC',
            'timeframe': 1,
            'quantidade': 50
        }
        
        response = requests.get(f"{base_url}/grafico", params=params)
        
        if response.status_code == 200:
            print("✅ Gráfico gerado com sucesso!")
            
            # Salva a imagem para verificar
            with open('test_grafico.png', 'wb') as f:
                f.write(response.content)
            print("💾 Imagem salva como 'test_grafico.png'")
        else:
            print(f"❌ Erro no gráfico: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar gráfico: {e}")

def test_get_candles():
    """Testa o endpoint de candles"""
    base_url = "http://localhost:8080"
    
    print("\n🕯️ Testando /get_candles...")
    
    try:
        payload = {
            "ativo": "EURUSD-OTC",
            "timeframe": 1,
            "quantidade": 10
        }
        
        response = requests.post(f"{base_url}/get_candles", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            candles = data.get('velas', [])
            print(f"✅ {len(candles)} candles retornados")
            
            if candles:
                # Verifica se tem volume
                first_candle = candles[0]
                has_volume = 'volume' in first_candle or 'Volume' in first_candle
                print(f"📊 Volume presente: {has_volume}")
                
                # Mostra estrutura do primeiro candle
                print(f"📋 Estrutura do candle: {list(first_candle.keys())}")
        else:
            print(f"❌ Erro nos candles: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar candles: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando testes do gráfico...")
    test_get_candles()
    test_grafico()
    print("\n✅ Testes concluídos!") 