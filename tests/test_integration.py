import subprocess
import time
import requests
import sys
import json

def test_all_endpoints():
    """Testa todos os endpoints da API automaticamente."""
    
    # Inicia o servidor Flask em background
    print("🚀 Iniciando o servidor Flask...")
    server = subprocess.Popen([sys.executable, "main.py"])
    
    try:
        # Aguarda o servidor subir
        print("⏳ Aguardando o servidor iniciar...")
        time.sleep(8)
        
        base_url = "http://localhost:8080"
        results = []
        
        # Teste 1: Status da API
        print("\n📊 Testando endpoint /status...")
        try:
            resp = requests.get(f"{base_url}/status")
            results.append({
                "endpoint": "/status",
                "status_code": resp.status_code,
                "success": resp.status_code == 200,
                "response": resp.json() if resp.status_code == 200 else resp.text
            })
            print(f"✅ Status: {resp.status_code}")
        except Exception as e:
            results.append({"endpoint": "/status", "error": str(e)})
            print(f"❌ Erro: {e}")
        
        # Teste 2: Saldo
        print("\n💰 Testando endpoint /balance...")
        try:
            resp = requests.get(f"{base_url}/balance?tipo_conta=PRACTICE")
            results.append({
                "endpoint": "/balance",
                "status_code": resp.status_code,
                "success": resp.status_code == 200,
                "response": resp.json() if resp.status_code == 200 else resp.text
            })
            print(f"✅ Status: {resp.status_code}")
        except Exception as e:
            results.append({"endpoint": "/balance", "error": str(e)})
            print(f"❌ Erro: {e}")
        
        # Teste 3: Get Candles
        print("\n📈 Testando endpoint /get_candles...")
        try:
            payload = {
                "ativo": "EURUSD-OTC",
                "timeframe": 5,
                "quantidade": 10
            }
            resp = requests.post(f"{base_url}/get_candles", json=payload)
            results.append({
                "endpoint": "/get_candles",
                "status_code": resp.status_code,
                "success": resp.status_code == 200,
                "response": resp.json() if resp.status_code == 200 else resp.text
            })
            print(f"✅ Status: {resp.status_code}")
        except Exception as e:
            results.append({"endpoint": "/get_candles", "error": str(e)})
            print(f"❌ Erro: {e}")
        
        # Teste 4: Trade
        print("\n🎯 Testando endpoint /trade...")
        try:
            payload = {
                "ativo": "EURUSD-OTC",
                "acao": "call",
                "duracao": 5,
                "tipo_conta": "PRACTICE"
            }
            resp = requests.post(f"{base_url}/trade", json=payload)
            results.append({
                "endpoint": "/trade",
                "status_code": resp.status_code,
                "success": resp.status_code == 200,
                "response": resp.json() if resp.status_code == 200 else resp.text
            })
            print(f"✅ Status: {resp.status_code}")
        except Exception as e:
            results.append({"endpoint": "/trade", "error": str(e)})
            print(f"❌ Erro: {e}")
        
        # Teste 5: Histórico
        print("\n📋 Testando endpoint /history...")
        try:
            resp = requests.get(f"{base_url}/history?tipo_conta=PRACTICE")
            results.append({
                "endpoint": "/history",
                "status_code": resp.status_code,
                "success": resp.status_code == 200,
                "response": resp.json() if resp.status_code == 200 else resp.text
            })
            print(f"✅ Status: {resp.status_code}")
        except Exception as e:
            results.append({"endpoint": "/history", "error": str(e)})
            print(f"❌ Erro: {e}")
        
        # Teste 6: Gerenciamento
        print("\n⚙️ Testando endpoint /management...")
        try:
            resp = requests.get(f"{base_url}/management?tipo_conta=PRACTICE")
            results.append({
                "endpoint": "/management",
                "status_code": resp.status_code,
                "success": resp.status_code == 200,
                "response": resp.json() if resp.status_code == 200 else resp.text
            })
            print(f"✅ Status: {resp.status_code}")
        except Exception as e:
            results.append({"endpoint": "/management", "error": str(e)})
            print(f"❌ Erro: {e}")
        
        # Resumo dos resultados
        print("\n" + "="*50)
        print("📊 RESUMO DOS TESTES")
        print("="*50)
        
        successful_tests = 0
        total_tests = len(results)
        
        for result in results:
            endpoint = result["endpoint"]
            if "error" in result:
                print(f"❌ {endpoint}: ERRO - {result['error']}")
            elif result.get("success"):
                print(f"✅ {endpoint}: OK")
                successful_tests += 1
            else:
                print(f"⚠️ {endpoint}: FALHOU - Status {result.get('status_code', 'N/A')}")
        
        print(f"\n🎯 Resultado: {successful_tests}/{total_tests} endpoints funcionando")
        
        if successful_tests == total_tests:
            print("🎉 TODOS OS ENDPOINTS ESTÃO FUNCIONANDO!")
        else:
            print("⚠️ Alguns endpoints precisam de atenção.")
        
        return results
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return []
    finally:
        # Encerra o servidor Flask
        print("\n🛑 Encerrando o servidor Flask...")
        server.terminate()
        server.wait()

if __name__ == "__main__":
    test_all_endpoints() 