# bot_auditor.py
from iqoptionapi.stable_api import IQ_Option
import logging
import time

# Configuração básica
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

# --- CONEXÃO ---
# Use sua nova senha!
email = "szinkamiza@gmail.com"
senha = "123lucas123" 

print("Conectando à IQ Option...")
Iq = IQ_Option(email, senha)
Iq.connect()

if Iq.check_connect():
    print(">>> Conexão bem-sucedida! <<<")
    Iq.change_balance("PRACTICE") 
    print(f"Saldo inicial: ${Iq.get_balance()}")
else:
    print("Erro na conexão. Saindo...")
    exit()

# --- LOOP DE ORDENS MANUAIS ---
print("\n--- Painel de Controle 'Auditor' ---")
print("Digite 'sair' a qualquer momento para fechar.")

while True:
    ativo = input("Digite o ativo (ex: EURUSD-OTC): ").upper()
    if ativo.lower() == 'sair': break

    valor_investido = float(input("Digite o valor para investir (ex: 10): "))
    if str(valor_investido).lower() == 'sair': break

    acao = input("Digite a ação (call ou put): ").lower()
    if acao.lower() == 'sair': break

    duracao = int(input("Digite a duração em minutos (ex: 1): "))
    if str(duracao).lower() == 'sair': break

    # --- ### LÓGICA DO AUDITOR (SUA IDEIA) ### ---
    
    print("\n" + "="*40)
    # 1. Pega o saldo ANTES da operação
    saldo_anterior = Iq.get_balance()
    print(f"Saldo ANTES da ordem: ${saldo_anterior}")
    
    print(f"Enviando ordem: {acao.upper()} em {ativo} | Valor ${valor_investido} | Duração {duracao} min...")
    
    check, order_id = Iq.buy(valor_investido, ativo, acao, duracao)

    if check:
        print(f">>> SUCESSO! Ordem enviada. ID: {order_id}")
        
        print(f"Aguardando {duracao} minuto(s) para auditar o resultado...")
        time.sleep(duracao * 60 + 5) # Espera a operação terminar + 5s de margem
        
        # 2. Pega o saldo DEPOIS da operação
        saldo_posterior = Iq.get_balance()
        print(f"Saldo DEPOIS da ordem: ${saldo_posterior}")
        
        # 3. Compara os saldos para deduzir o resultado
        diferenca = round(saldo_posterior - saldo_anterior, 2)

        print("\n--- RESULTADO DA AUDITORIA ---")
        if diferenca > 0:
            print(f"Resultado: WIN (Lucro: +${diferenca})")
        elif diferenca < 0:
            print(f"Resultado: LOSS (Perda: ${diferenca})")
        else:
            print("Resultado: EMPATE ($0.00)")
        print("="*40 + "\n")

    else:
        print(">>> FALHA! A ordem não pôde ser enviada.")
    
    print("-" * 30)

print("\n--- Painel de Controle Finalizado ---")
input("Pressione Enter para fechar...")