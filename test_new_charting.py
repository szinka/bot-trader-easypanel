#!/usr/bin/env python3
"""
Script de teste para o novo sistema de charting com mplfinance
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from API.charting import ChartGenerator

def create_test_data():
    """Cria dados de teste para o gráfico"""
    # Gera dados de teste
    dates = pd.date_range(start='2025-07-25 00:00:00', periods=100, freq='5min')
    
    # Preços simulados
    np.random.seed(42)
    base_price = 1.1750
    prices = []
    for i in range(100):
        change = np.random.normal(0, 0.0005)
        base_price += change
        prices.append(base_price)
    
    # Cria DataFrame
    df = pd.DataFrame({
        'Open': [p + np.random.normal(0, 0.0001) for p in prices],
        'High': [p + abs(np.random.normal(0, 0.0002)) for p in prices],
        'Low': [p - abs(np.random.normal(0, 0.0002)) for p in prices],
        'Close': prices,
        'Volume': np.random.randint(1000, 5000, 100)
    }, index=dates)
    
    # Garante que High >= max(Open, Close) e Low <= min(Open, Close)
    for i in range(len(df)):
        df.loc[df.index[i], 'High'] = max(df.loc[df.index[i], 'Open'], 
                                          df.loc[df.index[i], 'Close'], 
                                          df.loc[df.index[i], 'High'])
        df.loc[df.index[i], 'Low'] = min(df.loc[df.index[i], 'Open'], 
                                         df.loc[df.index[i], 'Close'], 
                                         df.loc[df.index[i], 'Low'])
    
    return df

def test_chart_generator():
    """Testa o gerador de gráficos"""
    print("🧪 Testando novo sistema de charting...")
    
    # Cria dados de teste
    df = create_test_data()
    print(f"✅ Dados de teste criados: {len(df)} candles")
    
    # Testa o gerador
    try:
        chart_generator = ChartGenerator(theme='dark')
        print("✅ ChartGenerator criado com sucesso")
        
        # Testa gráfico completo
        img_bytes = chart_generator.create_candlestick_chart(
            df, 
            title="Teste - Análise Técnica Completa"
        )
        print(f"✅ Gráfico completo gerado: {len(img_bytes)} bytes")
        
        # Salva o gráfico
        with open('teste_grafico_completo.png', 'wb') as f:
            f.write(img_bytes)
        print("✅ Gráfico salvo como 'teste_grafico_completo.png'")
        
        # Testa gráfico simples
        img_bytes_simple = chart_generator.create_simple_chart(
            df, 
            title="Teste - Gráfico Simples"
        )
        print(f"✅ Gráfico simples gerado: {len(img_bytes_simple)} bytes")
        
        # Salva o gráfico simples
        with open('teste_grafico_simples.png', 'wb') as f:
            f.write(img_bytes_simple)
        print("✅ Gráfico simples salvo como 'teste_grafico_simples.png'")
        
        print("\n🎉 Todos os testes passaram!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chart_generator()
    if success:
        print("\n✅ Sistema de charting funcionando corretamente!")
    else:
        print("\n❌ Problemas encontrados no sistema de charting!") 