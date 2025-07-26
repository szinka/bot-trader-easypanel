#!/usr/bin/env python3
"""
Script para corrigir o problema de timestamps no endpoint /grafico_dados
"""

def fix_grafico_dados_code():
    """
    Corrige o código do endpoint /grafico_dados para evitar operações com timestamps
    """
    
    # Código corrigido para o endpoint /grafico_dados
    corrected_code = '''
        # Plota candlesticks usando barras simples
        up = df[df.Close >= df.Open]
        down = df[df.Close < df.Open]
        
        # Velas de alta (verde)
        if not up.empty:
            ax1.bar(up.index, up.Close - up.Open, width=0.6, bottom=up.Open, 
                   color=colors['up'], alpha=0.8, edgecolor=colors['up'])
            # Mechas de alta
            for idx, row in up.iterrows():
                ax1.plot([idx, idx], [row['Low'], row['High']], color=colors['up'], linewidth=1)
        
        # Velas de baixa (vermelho)
        if not down.empty:
            ax1.bar(down.index, down.Close - down.Open, width=0.6, bottom=down.Open, 
                   color=colors['down'], alpha=0.8, edgecolor=colors['down'])
            # Mechas de baixa
            for idx, row in down.iterrows():
                ax1.plot([idx, idx], [row['Low'], row['High']], color=colors['down'], linewidth=1)
        
        # Médias móveis
        ax1.plot(df.index, df['SMA_9'], color=colors['sma9'], linewidth=1.5, 
                label='SMA 9', alpha=0.8)
        ax1.plot(df.index, df['SMA_20'], color=colors['sma20'], linewidth=1.5, 
                label='SMA 20', alpha=0.8)
        ax1.plot(df.index, df['SMA_50'], color=colors['sma50'], linewidth=1.5, 
                label='SMA 50', alpha=0.8)
        
        # Bollinger Bands
        ax1.plot(df.index, df['BB_upper'], color=colors['bb_upper'], linewidth=1, 
                alpha=0.6, linestyle='--', label='BB Upper')
        ax1.plot(df.index, df['BB_lower'], color=colors['bb_lower'], linewidth=1, 
                alpha=0.6, linestyle='--', label='BB Lower')
        ax1.plot(df.index, df['BB_20'], color=colors['bb_middle'], linewidth=1, 
                alpha=0.6, label='BB Middle')
        
        # Configuração do gráfico principal
        ax1.set_facecolor(colors['background'])
        ax1.grid(True, color=colors['grid'], linestyle='-', linewidth=0.5, alpha=0.3)
        ax1.set_title('Análise Técnica Completa - Dados Fornecidos', 
                     color=colors['text'], fontsize=14, fontweight='bold', pad=20)
        ax1.set_ylabel('Preço', color=colors['text'], fontsize=12)
        ax1.legend(loc='upper left', frameon=False, fontsize=9, ncol=3)
        
        # Remove bordas
        for spine in ax1.spines.values():
            spine.set_color(colors['border'])
            spine.set_linewidth(0.5)
        
        # Configuração dos ticks
        ax1.tick_params(colors=colors['text'], labelsize=10)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=0)

        # Painel 2: Volume
        ax2 = fig.add_subplot(gs[1], sharex=ax1)
        
        # Volume como barras normais
        volume_colors = []
        for i in range(len(df)):
            if df['Close'].iloc[i] >= df['Open'].iloc[i]:
                volume_colors.append(colors['volume_up'])
            else:
                volume_colors.append(colors['volume_down'])
        
        ax2.bar(df.index, df['Volume'], color=volume_colors, alpha=0.7, width=0.6)
    '''
    
    return corrected_code

if __name__ == "__main__":
    print("Código corrigido para o endpoint /grafico_dados:")
    print(fix_grafico_dados_code()) 