"""
Gerador de gráficos financeiros usando matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import io
from .indicators import TechnicalIndicators
from .themes import ChartThemes

class ChartGenerator:
    """Gerador de gráficos financeiros profissionais usando matplotlib"""
    
    def __init__(self, theme='dark'):
        """Inicializa o gerador com tema especificado"""
        self.theme = theme
        self.colors = ChartThemes.get_dark_theme() if theme == 'dark' else ChartThemes.get_light_theme()
    
    def create_candlestick_chart(self, df, title="Análise Técnica Completa"):
        """
        Cria gráfico de candlestick completo com indicadores usando matplotlib
        
        Args:
            df: DataFrame com colunas ['Open', 'High', 'Low', 'Close', 'Volume']
            title: Título do gráfico
            
        Returns:
            bytes: Imagem do gráfico em formato PNG
        """
        # Adiciona indicadores técnicos
        df = TechnicalIndicators.add_all_indicators(df)
        
        # Configura matplotlib
        plt.style.use('dark_background' if self.theme == 'dark' else 'default')
        
        # Cria figura com subplots
        fig, axes = plt.subplots(3, 1, figsize=(16, 12), 
                                gridspec_kw={'height_ratios': [6, 2, 2]})
        
        # Painel 1: Candlesticks e indicadores
        ax1 = axes[0]
        
        # Plota candlesticks
        for i, (idx, row) in enumerate(df.iterrows()):
            # Determina cor baseada na direção da vela
            if row['Close'] >= row['Open']:
                color = self.colors['up']
            else:
                color = self.colors['down']
            
            # Desenha a linha vertical (mecha)
            ax1.plot([idx, idx], [row['Low'], row['High']], color=color, linewidth=1)
            
            # Desenha o corpo da vela
            body_height = abs(row['Close'] - row['Open'])
            if body_height > 0:
                # Corpo da vela como retângulo
                if row['Close'] >= row['Open']:
                    # Vela de alta (verde)
                    rect = plt.Rectangle((mdates.date2num(idx) - 0.3, row['Open']), 
                                       0.6, body_height, facecolor=color, edgecolor=color, alpha=0.8)
                    ax1.add_patch(rect)
                else:
                    # Vela de baixa (vermelha)
                    rect = plt.Rectangle((mdates.date2num(idx) - 0.3, row['Close']), 
                                       0.6, body_height, facecolor=color, edgecolor=color, alpha=0.8)
                    ax1.add_patch(rect)
            else:
                # Doji - apenas linha horizontal
                ax1.plot([mdates.date2num(idx) - 0.3, mdates.date2num(idx) + 0.3], 
                        [row['Open'], row['Open']], color=color, linewidth=2)
        
        # Médias móveis
        ax1.plot(df.index, df['SMA_9'], color=self.colors['sma9'], linewidth=1.5, 
                label='SMA 9', alpha=0.8)
        ax1.plot(df.index, df['SMA_20'], color=self.colors['sma20'], linewidth=1.5, 
                label='SMA 20', alpha=0.8)
        ax1.plot(df.index, df['SMA_50'], color=self.colors['sma50'], linewidth=1.5, 
                label='SMA 50', alpha=0.8)
        
        # Bollinger Bands
        ax1.plot(df.index, df['BB_upper'], color=self.colors['bb_upper'], linewidth=1, 
                alpha=0.6, linestyle='--', label='BB Upper')
        ax1.plot(df.index, df['BB_lower'], color=self.colors['bb_lower'], linewidth=1, 
                alpha=0.6, linestyle='--', label='BB Lower')
        ax1.plot(df.index, df['BB_20'], color=self.colors['bb_middle'], linewidth=1, 
                alpha=0.6, label='BB Middle')
        
        # Configuração do gráfico principal
        ax1.set_facecolor(self.colors['background'])
        ax1.grid(True, color=self.colors['grid'], linestyle='-', linewidth=0.5, alpha=0.3)
        ax1.set_title(title, color=self.colors['text'], fontsize=14, fontweight='bold', pad=20)
        ax1.set_ylabel('Preço', color=self.colors['text'], fontsize=12)
        ax1.legend(loc='upper left', frameon=False, fontsize=9, ncol=3)
        
        # Remove bordas
        for spine in ax1.spines.values():
            spine.set_color(self.colors['border'])
            spine.set_linewidth(0.5)
        
        # Configuração dos ticks
        ax1.tick_params(colors=self.colors['text'], labelsize=10)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=0)

        # Painel 2: Volume
        ax2 = axes[1]
        
        # Volume como barras
        for i, (idx, row) in enumerate(df.iterrows()):
            if row['Close'] >= row['Open']:
                color = self.colors['volume_up']
            else:
                color = self.colors['volume_down']
            
            if row['Volume'] > 0:
                rect = plt.Rectangle((mdates.date2num(idx) - 0.3, 0), 
                                   0.6, row['Volume'], facecolor=color, edgecolor=color, alpha=0.7)
                ax2.add_patch(rect)
        
        ax2.set_ylabel('Volume', color=self.colors['text'], fontsize=10)
        ax2.set_facecolor(self.colors['background'])
        ax2.grid(True, color=self.colors['grid'], linestyle='-', linewidth=0.5, alpha=0.3)
        
        # Remove bordas do volume
        for spine in ax2.spines.values():
            spine.set_color(self.colors['border'])
            spine.set_linewidth(0.5)
        
        ax2.tick_params(colors=self.colors['text'], labelsize=9)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        # Painel 3: RSI
        ax3 = axes[2]
        
        ax3.plot(df.index, df['RSI'], color=self.colors['rsi'], linewidth=1.5, label='RSI')
        ax3.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='Sobrecomprado')
        ax3.axhline(y=30, color='green', linestyle='--', alpha=0.5, label='Sobrevendido')
        ax3.fill_between(df.index, 70, 100, alpha=0.1, color='red')
        ax3.fill_between(df.index, 0, 30, alpha=0.1, color='green')
        
        ax3.set_ylabel('RSI', color=self.colors['text'], fontsize=10)
        ax3.set_ylim(0, 100)
        ax3.set_facecolor(self.colors['background'])
        ax3.grid(True, color=self.colors['grid'], linestyle='-', linewidth=0.5, alpha=0.3)
        ax3.legend(loc='upper left', frameon=False, fontsize=8)
        
        # Remove bordas do RSI
        for spine in ax3.spines.values():
            spine.set_color(self.colors['border'])
            spine.set_linewidth(0.5)
        
        ax3.tick_params(colors=self.colors['text'], labelsize=9)
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax3.set_xlabel('Horário', color=self.colors['text'], fontsize=12)

        # Configuração final
        fig.patch.set_facecolor(self.colors['background'])
        plt.tight_layout()
        plt.subplots_adjust(top=0.95, bottom=0.05, left=0.05, right=0.95)
        
        # Salva a imagem
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', 
                   facecolor=self.colors['background'], edgecolor='none')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer.getvalue()
    
    def create_simple_chart(self, df, title="Gráfico de Candlestick"):
        """
        Cria gráfico simples de candlestick
        
        Args:
            df: DataFrame com colunas ['Open', 'High', 'Low', 'Close', 'Volume']
            title: Título do gráfico
            
        Returns:
            bytes: Imagem do gráfico em formato PNG
        """
        # Configura matplotlib
        plt.style.use('dark_background' if self.theme == 'dark' else 'default')
        
        # Cria figura
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                       gridspec_kw={'height_ratios': [6, 2]})
        
        # Painel 1: Candlesticks
        for i, (idx, row) in enumerate(df.iterrows()):
            # Determina cor baseada na direção da vela
            if row['Close'] >= row['Open']:
                color = self.colors['up']
            else:
                color = self.colors['down']
            
            # Desenha a linha vertical (mecha)
            ax1.plot([idx, idx], [row['Low'], row['High']], color=color, linewidth=1)
            
            # Desenha o corpo da vela
            body_height = abs(row['Close'] - row['Open'])
            if body_height > 0:
                # Corpo da vela como retângulo
                if row['Close'] >= row['Open']:
                    # Vela de alta (verde)
                    rect = plt.Rectangle((mdates.date2num(idx) - 0.3, row['Open']), 
                                       0.6, body_height, facecolor=color, edgecolor=color, alpha=0.8)
                    ax1.add_patch(rect)
                else:
                    # Vela de baixa (vermelha)
                    rect = plt.Rectangle((mdates.date2num(idx) - 0.3, row['Close']), 
                                       0.6, body_height, facecolor=color, edgecolor=color, alpha=0.8)
                    ax1.add_patch(rect)
            else:
                # Doji - apenas linha horizontal
                ax1.plot([mdates.date2num(idx) - 0.3, mdates.date2num(idx) + 0.3], 
                        [row['Open'], row['Open']], color=color, linewidth=2)
        
        # Configuração do gráfico principal
        ax1.set_facecolor(self.colors['background'])
        ax1.grid(True, color=self.colors['grid'], linestyle='-', linewidth=0.5, alpha=0.3)
        ax1.set_title(title, color=self.colors['text'], fontsize=14, fontweight='bold', pad=20)
        ax1.set_ylabel('Preço', color=self.colors['text'], fontsize=12)
        
        # Remove bordas
        for spine in ax1.spines.values():
            spine.set_color(self.colors['border'])
            spine.set_linewidth(0.5)
        
        # Configuração dos ticks
        ax1.tick_params(colors=self.colors['text'], labelsize=10)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=0)

        # Painel 2: Volume
        for i, (idx, row) in enumerate(df.iterrows()):
            if row['Close'] >= row['Open']:
                color = self.colors['volume_up']
            else:
                color = self.colors['volume_down']
            
            if row['Volume'] > 0:
                rect = plt.Rectangle((mdates.date2num(idx) - 0.3, 0), 
                                   0.6, row['Volume'], facecolor=color, edgecolor=color, alpha=0.7)
                ax2.add_patch(rect)
        
        ax2.set_ylabel('Volume', color=self.colors['text'], fontsize=10)
        ax2.set_facecolor(self.colors['background'])
        ax2.grid(True, color=self.colors['grid'], linestyle='-', linewidth=0.5, alpha=0.3)
        
        # Remove bordas do volume
        for spine in ax2.spines.values():
            spine.set_color(self.colors['border'])
            spine.set_linewidth(0.5)
        
        ax2.tick_params(colors=self.colors['text'], labelsize=9)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax2.set_xlabel('Horário', color=self.colors['text'], fontsize=12)

        # Configuração final
        fig.patch.set_facecolor(self.colors['background'])
        plt.tight_layout()
        
        # Salva a imagem
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', 
                   facecolor=self.colors['background'], edgecolor='none')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer.getvalue() 