#!/usr/bin/env python3
# test_iq.py - Teste simples de conexão IQ Option

import os
from dotenv import load_dotenv
from iqoptionapi.api import IQOptionAPI

# Carrega variáveis de ambiente
load_dotenv()

def test_iq_connection():
    email = os.getenv('IQ_EMAIL')
    senha = os.getenv('IQ_PASSWORD')
    
    print(f"Email: {email}")
    print(f"Senha: {senha}")
    
    try:
        # Tenta conectar
        api = IQOptionAPI(username=email, password=senha, host="iqoption.com")
        check, reason = api.connect()
        
        if check:
            print("✅ Conexão bem-sucedida!")
            
            # Lista métodos disponíveis
            print("📋 Métodos disponíveis:")
            methods = [method for method in dir(api) if not method.startswith('_')]
            for method in methods[:10]:  # Primeiros 10 métodos
                print(f"  - {method}")
            
            # Testa saldo
            try:
                saldo = api.get_balance()
                print(f"💰 Saldo: ${saldo}")
            except Exception as e:
                print(f"❌ Erro ao pegar saldo: {e}")
            
        else:
            print(f"❌ Falha na conexão: {reason}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_iq_connection() 