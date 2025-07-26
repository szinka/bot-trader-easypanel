"""
Gerador de gráficos financeiros usando matplotlib - Versão Otimizada
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
    
    def _plot_candlesticks(self, ax, df):
        """Plota candlesticks de forma otimizada"""
        # Agrupa dados por cor para melhor performance
        up_data = df[df['Close'] >= df['Open']]
        down_data = df[df['Close'] < df['Open']]
        
        # Plota velas de alta (verde)
        for idx, row in up_data.iterrows():
            # Mecha
            ax.plot([idx, idx], [row['Low'], row['High']], 
                   color=self.colors['up'], linewidth=1)
            
            # Corpo
            body_height = row['Close'] - row['Open']
            if body_height > 0:
                rect = plt.Rectangle((mdates.date2num(idx) - 0.3, row['Open']), 
                                   0.6, body_height, facecolor=self.colors['up'], 
                                   edgecolor=self.colors['up'], alpha=0.8)
                ax.add_patch(rect)
            else:
                # Doji
                ax.plot([mdates.date2num(idx) - 0.3, mdates.date2num(idx) + 0.3], 
                       [row['Open'], row['Open']], color=self.colors['up'], linewidth=2)
        
        # Plota velas de baixa (vermelha)
        for idx, row in down_data.iterrows():
            # Mecha
            ax.plot([idx, idx], [row['Low'], row['High']], 
                   color=self.colors['down'], linewidth=1)
            
            # Corpo
            body_height = row['Open'] - row['Close']
            if body_height > 0:
                rect = plt.Rectangle((mdates.date2num(idx) - 0.3, row['Close']), 
                                   0.6, body_height, facecolor=self.colors['down'], 
                                   edgecolor=self.colors['down'], alpha=0.8)
                ax.add_patch(rect)
            else:
                # Doji
                ax.plot([mdates.date2num(idx) - 0.3, mdates.date2num(idx) + 0.3], 
                       [row['Open'], row['Open']], color=self.colors['down'], linewidth=2)
    
    def _plot_volume(self, ax, df):
        """Plota volume de forma otimizada"""
        # Agrupa dados por cor
        up_data = df[df['Close'] >= df['Open']]
        down_data = df[df['Close'] < df['Open']]
        
        # Volume de alta
        for idx, row in up_data.iterrows():
            if row['Volume'] > 0:
                rect = plt.Rectangle((mdates.date2num(idx) - 0.3, 0), 
                                   0.6, row['Volume'], facecolor=self.colors['volume_up'], 
                                   edgecolor=self.colors['volume_up'], alpha=0.7)
                ax.add_patch(rect)
        
        # Volume de baixa
        for idx, row in down_data.iterrows():
            if row['Volume'] > 0:
                rect = plt.Rectangle((mdates.date2num(idx) - 0.3, 0), 
                                   0.6, row['Volume'], facecolor=self.colors['volume_down'], 
                                   edgecolor=self.colors['volume_down'], alpha=0.7)
                ax.add_patch(rect)
    
    def _configure_axis(self, ax, title=None, ylabel=None, show_legend=False, legend_items=None):
        """Configura eixo de forma padronizada"""
        ax.set_facecolor(self.colors['background'])
        ax.grid(True, color=self.colors['grid'], linestyle='-', linewidth=0.5, alpha=0.3)
        
        if title:
            ax.set_title(title, color=self.colors['text'], fontsize=14, fontweight='bold', pad=20)
        if ylabel:
            ax.set_ylabel(ylabel, color=self.colors['text'], fontsize=12)
        
        # Remove bordas
        for spine in ax.spines.values():
            spine.set_color(self.colors['border'])
            spine.set_linewidth(0.5)
        
        # Configuração dos ticks
        ax.tick_params(colors=self.colors['text'], labelsize=10)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=0)
        
        # Legenda
        if show_legend and legend_items:
            ax.legend(loc='upper left', frameon=False, fontsize=9, ncol=2)
    
    def create_candlestick_chart(self, df, title="Análise Técnica Completa"):
        """
        Cria gráfico de candlestick otimizado com indicadores essenciais
        
        Args:
            df: DataFrame com colunas ['Open', 'High', 'Low', 'Close', 'Volume']
            title: Título do gráfico
            
        Returns:
            bytes: Imagem do gráfico em formato PNG
        """
        # Adiciona indicadores essenciais
        df = TechnicalIndicators.add_essential_indicators(df)
        
        # Configura matplotlib
        plt.style.use('dark_background' if self.theme == 'dark' else 'default')
        
        # Cria figura com subplots otimizados
        fig, axes = plt.subplots(3, 1, figsize=(16, 10), 
                                gridspec_kw={'height_ratios': [6, 2, 2]})
        
        # Painel 1: Candlesticks e indicadores essenciais
        ax1 = axes[0]
        
        # Plota candlesticks
        self._plot_candlesticks(ax1, df)
        
        # Médias móveis essenciais
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
        self._configure_axis(ax1, title=title, ylabel='Preço', show_legend=True)

        # Painel 2: Volume
        ax2 = axes[1]
        self._plot_volume(ax2, df)
        self._configure_axis(ax2, ylabel='Volume')

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

        # Configuração final otimizada
        fig.patch.set_facecolor(self.colors['background'])
        plt.tight_layout()
        plt.subplots_adjust(top=0.95, bottom=0.05, left=0.05, right=0.95)
        
        # Salva a imagem com qualidade otimizada
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', 
                   facecolor=self.colors['background'], edgecolor='none')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer.getvalue()
    
    def create_simple_chart(self, df, title="Gráfico de Candlestick"):
        """
        Cria gráfico simples de candlestick otimizado
        
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
        self._plot_candlesticks(ax1, df)
        self._configure_axis(ax1, title=title, ylabel='Preço')

        # Painel 2: Volume
        self._plot_volume(ax2, df)
        self._configure_axis(ax2, ylabel='Volume')
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