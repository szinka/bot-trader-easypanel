"""
Temas de cores para gráficos financeiros
"""

class ChartThemes:
    """Temas de cores para gráficos financeiros"""
    
    @staticmethod
    def get_dark_theme():
        """Retorna tema dark melhorado"""
        return {
            'background': '#1a1a1a',
            'text': '#ffffff',
            'grid': '#333333',
            'border': '#444444',
            
            # Candlesticks
            'up': '#00ff88',      # Verde mais vibrante
            'down': '#ff4444',    # Vermelho mais vibrante
            
            # Volume
            'volume_up': '#00cc66',    # Verde volume
            'volume_down': '#cc3333',  # Vermelho volume
            
            # Indicadores
            'sma20': '#ffaa00',       # Laranja para SMA 20
            'sma50': '#00aaff',       # Azul para SMA 50
            'bb_upper': '#ff66ff',    # Rosa para BB Upper
            'bb_lower': '#66ffff',    # Ciano para BB Lower
            'bb_middle': '#ffff66',   # Amarelo para BB Middle
            'rsi': '#ff88ff',         # Rosa claro para RSI
        }
    
    @staticmethod
    def get_light_theme():
        """Retorna tema light"""
        return {
            'background': '#ffffff',
            'text': '#000000',
            'grid': '#cccccc',
            'border': '#999999',
            
            # Candlesticks
            'up': '#00aa44',
            'down': '#aa0000',
            
            # Volume
            'volume_up': '#00aa44',
            'volume_down': '#aa0000',
            
            # Indicadores
            'sma20': '#ff8800',
            'sma50': '#0088ff',
            'bb_upper': '#ff0088',
            'bb_lower': '#0088ff',
            'bb_middle': '#ffaa00',
            'rsi': '#ff0088',
        } 