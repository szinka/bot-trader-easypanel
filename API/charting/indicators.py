"""
Indicadores técnicos para análise financeira - Versão Simplificada
"""

import pandas as pd
import numpy as np

class TechnicalIndicators:
    """Classe para cálculo de indicadores técnicos essenciais"""
    
    @staticmethod
    def calculate_sma(df, period):
        """Calcula Média Móvel Simples"""
        return df['Close'].rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(df, period):
        """Calcula Média Móvel Exponencial"""
        return df['Close'].ewm(span=period).mean()
    
    @staticmethod
    def calculate_bollinger_bands(df, period=20, std_dev=2):
        """Calcula Bollinger Bands"""
        sma = df['Close'].rolling(window=period).mean()
        std = df['Close'].rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return sma, upper_band, lower_band
    
    @staticmethod
    def calculate_rsi(df, period=14):
        """Calcula RSI (Relative Strength Index)"""
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def add_essential_indicators(df):
        """Adiciona apenas indicadores essenciais ao DataFrame"""
        # Médias móveis principais
        df['SMA_20'] = TechnicalIndicators.calculate_sma(df, 20)
        df['SMA_50'] = TechnicalIndicators.calculate_sma(df, 50)
        
        # Bollinger Bands
        df['BB_20'], df['BB_upper'], df['BB_lower'] = TechnicalIndicators.calculate_bollinger_bands(df)
        
        # RSI
        df['RSI'] = TechnicalIndicators.calculate_rsi(df)
        
        return df
    
    @staticmethod
    def add_all_indicators(df):
        """Mantém compatibilidade - chama add_essential_indicators"""
        return TechnicalIndicators.add_essential_indicators(df) 