"""
Gerador de gráficos financeiros usando Plotly
"""

import plotly.graph_objects as go
import plotly.subplots as sp
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import io
import base64
from .indicators import TechnicalIndicators
from .themes import ChartThemes

class ChartGenerator:
    """Gerador de gráficos financeiros profissionais"""
    
    def __init__(self, theme='dark'):
        """Inicializa o gerador com tema especificado"""
        self.theme = theme
        self.colors = ChartThemes.get_dark_theme() if theme == 'dark' else ChartThemes.get_light_theme()
    
    def create_candlestick_chart(self, df, title="Análise Técnica Completa"):
        """
        Cria gráfico de candlestick completo com indicadores
        
        Args:
            df: DataFrame com colunas ['Open', 'High', 'Low', 'Close', 'Volume']
            title: Título do gráfico
            
        Returns:
            bytes: Imagem do gráfico em formato PNG
        """
        # Adiciona indicadores técnicos
        df = TechnicalIndicators.add_all_indicators(df)
        
        # Cria subplots
        fig = make_subplots(
            rows=5, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Preço', 'Volume', 'RSI', 'MACD', 'Stochastic'),
            row_heights=[0.4, 0.15, 0.15, 0.15, 0.15]
        )
        
        # 1. Candlesticks e indicadores principais
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Preço',
                increasing_line_color=self.colors['up'],
                decreasing_line_color=self.colors['down']
            ),
            row=1, col=1
        )
        
        # Médias móveis
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['SMA_9'],
                mode='lines',
                name='SMA 9',
                line=dict(color=self.colors['sma9'], width=1.5)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['SMA_20'],
                mode='lines',
                name='SMA 20',
                line=dict(color=self.colors['sma20'], width=1.5)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['SMA_50'],
                mode='lines',
                name='SMA 50',
                line=dict(color=self.colors['sma50'], width=1.5)
            ),
            row=1, col=1
        )
        
        # Bollinger Bands
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['BB_upper'],
                mode='lines',
                name='BB Upper',
                line=dict(color=self.colors['bb_upper'], width=1, dash='dash'),
                opacity=0.6
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['BB_lower'],
                mode='lines',
                name='BB Lower',
                line=dict(color=self.colors['bb_lower'], width=1, dash='dash'),
                opacity=0.6,
                fill='tonexty',
                fillcolor='rgba(231, 76, 60, 0.1)'
            ),
            row=1, col=1
        )
        
        # 2. Volume
        colors_volume = [self.colors['volume_up'] if close >= open else self.colors['volume_down'] 
                        for close, open in zip(df['Close'], df['Open'])]
        
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                name='Volume',
                marker_color=colors_volume,
                opacity=0.7
            ),
            row=2, col=1
        )
        
        # 3. RSI
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['RSI'],
                mode='lines',
                name='RSI',
                line=dict(color=self.colors['rsi'], width=1.5)
            ),
            row=3, col=1
        )
        
        # Linhas de referência RSI
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=3, col=1)
        
        # 4. MACD
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['MACD'],
                mode='lines',
                name='MACD',
                line=dict(color=self.colors['macd'], width=1.5)
            ),
            row=4, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['Signal'],
                mode='lines',
                name='Signal',
                line=dict(color=self.colors['signal'], width=1.5)
            ),
            row=4, col=1
        )
        
        # Histograma MACD
        colors_hist = [self.colors['histogram_up'] if h >= 0 else self.colors['histogram_down'] 
                      for h in df['MACD_Hist']]
        
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['MACD_Hist'],
                name='MACD Hist',
                marker_color=colors_hist,
                opacity=0.7
            ),
            row=4, col=1
        )
        
        # 5. Stochastic
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['Stoch_K'],
                mode='lines',
                name='%K',
                line=dict(color=self.colors['stoch_k'], width=1.5)
            ),
            row=5, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['Stoch_D'],
                mode='lines',
                name='%D',
                line=dict(color=self.colors['stoch_d'], width=1.5)
            ),
            row=5, col=1
        )
        
        # Linhas de referência Stochastic
        fig.add_hline(y=80, line_dash="dash", line_color="red", opacity=0.5, row=5, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="green", opacity=0.5, row=5, col=1)
        
        # Configuração do layout
        fig.update_layout(
            title=title,
            template='plotly_dark' if self.theme == 'dark' else 'plotly_white',
            height=800,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis_rangeslider_visible=False
        )
        
        # Configuração dos eixos
        fig.update_xaxes(
            title_text="Horário",
            row=5, col=1
        )
        
        fig.update_yaxes(title_text="Preço", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])
        fig.update_yaxes(title_text="MACD", row=4, col=1)
        fig.update_yaxes(title_text="Stoch", row=5, col=1, range=[0, 100])
        
        # Converte para imagem
        img_bytes = fig.to_image(format="png", width=1200, height=800)
        return img_bytes
    
    def create_simple_chart(self, df, title="Gráfico de Candlestick"):
        """
        Cria gráfico simples de candlestick
        
        Args:
            df: DataFrame com colunas ['Open', 'High', 'Low', 'Close', 'Volume']
            title: Título do gráfico
            
        Returns:
            bytes: Imagem do gráfico em formato PNG
        """
        fig = go.Figure()
        
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Preço',
                increasing_line_color=self.colors['up'],
                decreasing_line_color=self.colors['down']
            )
        )
        
        fig.update_layout(
            title=title,
            template='plotly_dark' if self.theme == 'dark' else 'plotly_white',
            height=600,
            xaxis_title="Horário",
            yaxis_title="Preço",
            xaxis_rangeslider_visible=False
        )
        
        img_bytes = fig.to_image(format="png", width=1000, height=600)
        return img_bytes 