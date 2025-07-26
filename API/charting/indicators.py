"""
Indicadores técnicos para análise financeira
"""

import pandas as pd
import numpy as np

class TechnicalIndicators:
    """Classe para cálculo de indicadores técnicos"""
    
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
    def calculate_macd(df, fast=12, slow=26, signal=9):
        """Calcula MACD"""
        ema_fast = df['Close'].ewm(span=fast).mean()
        ema_slow = df['Close'].ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_stochastic(df, k_period=14, d_period=3):
        """Calcula Stochastic Oscillator"""
        lowest_low = df['Low'].rolling(window=k_period).min()
        highest_high = df['High'].rolling(window=k_period).max()
        k_percent = 100 * ((df['Close'] - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        return k_percent, d_percent
    
    @staticmethod
    def calculate_atr(df, period=14):
        """Calcula ATR (Average True Range)"""
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        return atr
    
    @staticmethod
    def add_all_indicators(df):
        """Adiciona todos os indicadores ao DataFrame"""
        # Médias móveis
        df['SMA_9'] = TechnicalIndicators.calculate_sma(df, 9)
        df['SMA_20'] = TechnicalIndicators.calculate_sma(df, 20)
        df['SMA_50'] = TechnicalIndicators.calculate_sma(df, 50)
        
        # Bollinger Bands
        df['BB_20'], df['BB_upper'], df['BB_lower'] = TechnicalIndicators.calculate_bollinger_bands(df)
        
        # RSI
        df['RSI'] = TechnicalIndicators.calculate_rsi(df)
        
        # MACD
        df['MACD'], df['Signal'], df['MACD_Hist'] = TechnicalIndicators.calculate_macd(df)
        
        # Stochastic
        df['Stoch_K'], df['Stoch_D'] = TechnicalIndicators.calculate_stochastic(df)
        
        # ATR
        df['ATR'] = TechnicalIndicators.calculate_atr(df)
        
        return df 