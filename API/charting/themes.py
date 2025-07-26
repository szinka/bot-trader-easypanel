"""
Temas para gráficos financeiros
"""

class ChartThemes:
    """Temas de cores para gráficos financeiros"""
    
    @staticmethod
    def get_dark_theme():
        """Tema escuro estilo TradingView"""
        return {
            'background': '#1e222d',
            'text': '#ffffff',
            'grid': '#2a2e39',
            'border': '#2a2e39',
            'up': '#26a69a',
            'down': '#ef5350',
            'volume_up': '#26a69a',
            'volume_down': '#ef5350',
            'sma9': '#f39c12',
            'sma20': '#3498db',
            'sma50': '#9b59b6',
            'bb_upper': '#e74c3c',
            'bb_lower': '#e74c3c',
            'bb_middle': '#95a5a6',
            'rsi': '#3498db',
            'macd': '#f39c12',
            'signal': '#e74c3c',
            'histogram_up': '#26a69a',
            'histogram_down': '#ef5350',
            'stoch_k': '#3498db',
            'stoch_d': '#e74c3c'
        }
    
    @staticmethod
    def get_light_theme():
        """Tema claro"""
        return {
            'background': '#ffffff',
            'text': '#000000',
            'grid': '#e0e0e0',
            'border': '#cccccc',
            'up': '#4caf50',
            'down': '#f44336',
            'volume_up': '#4caf50',
            'volume_down': '#f44336',
            'sma9': '#ff9800',
            'sma20': '#2196f3',
            'sma50': '#9c27b0',
            'bb_upper': '#f44336',
            'bb_lower': '#f44336',
            'bb_middle': '#757575',
            'rsi': '#2196f3',
            'macd': '#ff9800',
            'signal': '#f44336',
            'histogram_up': '#4caf50',
            'histogram_down': '#f44336',
            'stoch_k': '#2196f3',
            'stoch_d': '#f44336'
        } 