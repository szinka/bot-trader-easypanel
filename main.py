#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bot Trader - Sistema de Trading Automatizado
Script principal para inicialização do servidor
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Adiciona o diretório API ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'API'))

# Carrega variáveis de ambiente
load_dotenv()

def main():
    """Função principal para inicializar o servidor."""
    try:
        # Importa o servidor Flask
        import api_server
        app = api_server.app
        
        # Configuração de logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Verifica se as credenciais estão configuradas
        if not os.getenv('IQ_EMAIL') or not os.getenv('IQ_PASSWORD'):
            logging.error("❌ Credenciais IQ Option não configuradas!")
            logging.error("Configure IQ_EMAIL e IQ_PASSWORD no arquivo .env")
            sys.exit(1)
        
        # Sem dependência de banco por padrão
        
        logging.info("🚀 Iniciando Bot Trader...")
        logging.info(f"📊 Modo: {'Desenvolvimento' if os.getenv('FLASK_DEBUG') else 'Produção'}")
        logging.info(f"🌐 Servidor: http://localhost:8080")
        
        # Inicia o servidor
        app.run(
            host='0.0.0.0',
            port=8080,
            debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
        )
        
    except ImportError as e:
        logging.error(f"❌ Erro de importação: {e}")
        logging.error("Verifique se todas as dependências estão instaladas")
        sys.exit(1)
    except Exception as e:
        logging.error(f"❌ Erro crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 