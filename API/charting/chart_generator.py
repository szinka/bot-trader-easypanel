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
        Cria gráfico de candlestick usando mplfinance com indicadores
        
        Args:
            df: DataFrame com colunas ['Open', 'High', 'Low', 'Close', 'Volume']
            title: Título do gráfico
            
        Returns:
            bytes: Imagem do gráfico em formato PNG
        """
        # Prepara DataFrame
        df_clean = self._prepare_dataframe(df)
        
        # Adiciona indicadores essenciais
        df_with_indicators = TechnicalIndicators.add_essential_indicators(df_clean)
        
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
        
        # Configura indicadores adicionais
        add_plots = []
        
        # Médias móveis
        if 'SMA_20' in df_with_indicators.columns:
            add_plots.append(
                mpf.make_addplot(df_with_indicators['SMA_20'], color=self.colors['sma20'], width=1.5, label='SMA 20')
            )
        if 'SMA_50' in df_with_indicators.columns:
            add_plots.append(
                mpf.make_addplot(df_with_indicators['SMA_50'], color=self.colors['sma50'], width=1.5, label='SMA 50')
            )
        
        # Bollinger Bands
        if 'BB_upper' in df_with_indicators.columns:
            add_plots.append(
                mpf.make_addplot(df_with_indicators['BB_upper'], color=self.colors['bb_upper'], 
                               linestyle='--', width=1, label='BB Upper')
            )
        if 'BB_lower' in df_with_indicators.columns:
            add_plots.append(
                mpf.make_addplot(df_with_indicators['BB_lower'], color=self.colors['bb_lower'], 
                               linestyle='--', width=1, label='BB Lower')
            )
        
        # Cria figura com 3 painéis
        fig, axes = mpf.plot(
            df_with_indicators,
            type='candle',
            volume=True,
            style=style,
            addplot=add_plots,
            title=title,
            figsize=(16, 12),
            panel_ratios=(6, 2, 2),  # Preço, Volume, RSI
            returnfig=True
        )
        
        # Configura eixos
        ax1 = axes[0]  # Gráfico principal (Preço + Indicadores)
        ax2 = axes[2]  # Volume
        ax3 = axes[4]  # RSI (novo painel)
        
        # Configurações do gráfico principal
        ax1.set_ylabel('Preço', color=self.colors['text'], fontsize=12)
        ax1.tick_params(colors=self.colors['text'])
        ax1.legend(loc='upper left', frameon=False, fontsize=9, ncol=2)
        
        # Configurações do volume
        ax2.set_ylabel('Volume', color=self.colors['text'], fontsize=10)
        ax2.tick_params(colors=self.colors['text'])
        
        # Adiciona RSI no terceiro painel
        if 'RSI' in df_with_indicators.columns:
            ax3.plot(df_with_indicators.index, df_with_indicators['RSI'], 
                    color=self.colors['rsi'], linewidth=1.5, label='RSI')
            ax3.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='Sobrecomprado')
            ax3.axhline(y=30, color='green', linestyle='--', alpha=0.5, label='Sobrevendido')
            ax3.fill_between(df_with_indicators.index, 70, 100, alpha=0.1, color='red')
            ax3.fill_between(df_with_indicators.index, 0, 30, alpha=0.1, color='green')
            
            ax3.set_ylabel('RSI', color=self.colors['text'], fontsize=10)
            ax3.set_ylim(0, 100)
            ax3.set_facecolor(self.colors['background'])
            ax3.grid(True, color=self.colors['grid'], linestyle='-', linewidth=0.5, alpha=0.3)
            ax3.legend(loc='upper left', frameon=False, fontsize=8)
            ax3.tick_params(colors=self.colors['text'])
        
        # Configurações do eixo X (tempo)
        ax3.set_xlabel('Horário', color=self.colors['text'], fontsize=12)
        
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