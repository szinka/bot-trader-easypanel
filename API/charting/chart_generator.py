"""
Gerador de gráficos financeiros usando mplfinance
Versão limpa e básica
"""

import mplfinance as mpf
import pandas as pd
import io
from .indicators import TechnicalIndicators
from .themes import ChartThemes

class ChartGenerator:
    """Gerador de gráficos financeiros usando mplfinance"""
    
    def __init__(self, theme='dark'):
        """Inicializa o gerador com tema especificado"""
        self.theme = theme
        self.colors = ChartThemes.get_dark_theme() if theme == 'dark' else ChartThemes.get_light_theme()
    
    def _prepare_dataframe(self, df):
        """Prepara DataFrame para mplfinance"""
        # Garante que as colunas estão no formato correto
        df_clean = df.copy()
        
        # Renomeia colunas se necessário
        column_mapping = {
            'abertura': 'Open',
            'fechamento': 'Close', 
            'maxima': 'High',
            'minima': 'Low',
            'volume': 'Volume'
        }
        
        for old_name, new_name in column_mapping.items():
            if old_name in df_clean.columns:
                df_clean[new_name] = df_clean[old_name]
        
        # Garante que temos as colunas necessárias
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_columns:
            if col not in df_clean.columns:
                raise ValueError(f"Coluna '{col}' não encontrada no DataFrame")
        
        # Converte para float
        for col in required_columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Remove linhas com valores NaN
        df_clean = df_clean.dropna(subset=required_columns)
        
        return df_clean[required_columns]
    
    def create_candlestick_chart(self, df, title="Análise Técnica Completa"):
        """
        Cria gráfico de candlestick usando mplfinance
        
        Args:
            df: DataFrame com colunas ['Open', 'High', 'Low', 'Close', 'Volume']
            title: Título do gráfico
            
        Returns:
            bytes: Imagem do gráfico em formato PNG
        """
        # Prepara DataFrame
        df_clean = self._prepare_dataframe(df)
        
        # Configura estilo
        style = mpf.make_mpf_style(
            marketcolors=mpf.make_marketcolors(
                up=self.colors['up'],
                down=self.colors['down'],
                edge='inherit',
                wick='inherit',
                volume=self.colors['volume_up']
            ),
            gridstyle='',
            gridaxis='both',
            gridcolor=self.colors['grid'],
            rc={'axes.facecolor': self.colors['background']}
        )
        
        # Cria figura
        fig, axes = mpf.plot(
            df_clean,
            type='candle',
            volume=True,
            style=style,
            title=title,
            figsize=(16, 10),
            panel_ratios=(6, 2),
            returnfig=True
        )
        
        # Configura eixos
        ax1 = axes[0]  # Gráfico principal
        ax2 = axes[2]  # Volume
        
        # Configurações do gráfico principal
        ax1.set_ylabel('Preço', color=self.colors['text'])
        ax1.tick_params(colors=self.colors['text'])
        
        # Configurações do volume
        ax2.set_ylabel('Volume', color=self.colors['text'])
        ax2.tick_params(colors=self.colors['text'])
        
        # Salva a imagem
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', 
                   facecolor=self.colors['background'])
        img_buffer.seek(0)
        
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
        # Prepara DataFrame
        df_clean = self._prepare_dataframe(df)
        
        # Configura estilo
        style = mpf.make_mpf_style(
            marketcolors=mpf.make_marketcolors(
                up=self.colors['up'],
                down=self.colors['down'],
                edge='inherit',
                wick='inherit',
                volume=self.colors['volume_up']
            ),
            gridstyle='',
            gridaxis='both',
            gridcolor=self.colors['grid'],
            rc={'axes.facecolor': self.colors['background']}
        )
        
        # Cria figura
        fig, axes = mpf.plot(
            df_clean,
            type='candle',
            volume=True,
            style=style,
            title=title,
            figsize=(12, 8),
            panel_ratios=(6, 2),
            returnfig=True
        )
        
        # Configura eixos
        ax1 = axes[0]  # Gráfico principal
        ax2 = axes[2]  # Volume
        
        # Configurações do gráfico principal
        ax1.set_ylabel('Preço', color=self.colors['text'])
        ax1.tick_params(colors=self.colors['text'])
        
        # Configurações do volume
        ax2.set_ylabel('Volume', color=self.colors['text'])
        ax2.tick_params(colors=self.colors['text'])
        
        # Salva a imagem
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', 
                   facecolor=self.colors['background'])
        img_buffer.seek(0)
        
        return img_buffer.getvalue() 