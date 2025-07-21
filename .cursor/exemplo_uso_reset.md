# Endpoint de Reset do Gerenciamento

## Descrição
Endpoint para resetar apenas o gerenciamento Torre MK, pegando 5% da banca atual como nova entrada inicial.

## URLs Disponíveis
- `POST /resetar_gerenciamento`
- `POST /management/reset_gerenciamento`

## Parâmetros
```json
{
    "tipo_conta": "PRACTICE"  // ou "REAL"
}
```

## Exemplo de Uso

### 1. Reset do Gerenciamento PRACTICE
```bash
curl -X POST http://localhost:8080/resetar_gerenciamento \
  -H "Content-Type: application/json" \
  -d '{"tipo_conta": "PRACTICE"}'
```

### 2. Reset do Gerenciamento REAL
```bash
curl -X POST http://localhost:8080/resetar_gerenciamento \
  -H "Content-Type: application/json" \
  -d '{"tipo_conta": "REAL"}'
```

### 3. Usando Python requests
```python
import requests

# Reset PRACTICE
response = requests.post(
    "http://localhost:8080/resetar_gerenciamento",
    json={"tipo_conta": "PRACTICE"}
)

if response.status_code == 200:
    data = response.json()
    print(f"Status: {data['status']}")
    print(f"Mensagem: {data['mensagem']}")
    print(f"Nova entrada: ${data['dados']['nova_entrada']}")
```

## Resposta de Sucesso
```json
{
    "status": "sucesso",
    "mensagem": "Gerenciamento resetado para PRACTICE. Nova entrada: $10.00 (10% de $100.00)",
    "dados": {
        "tipo_conta": "PRACTICE",
        "banca_atual": 100.0,
        "nova_entrada": 10.0,
        "estado_apos_reset": {
            "total_wins": 0,
            "level_entries": {1: 10.0},
            "nivel_atual": 1
        }
    }
}
```

## O que o endpoint faz:

1. **Seleciona a conta** especificada (PRACTICE ou REAL)
2. **Pega o saldo atual** da conta
3. **Calcula nova entrada** como 10% da banca atual
4. **Reseta o gerenciamento**:
   - Zera total_wins
   - Remove todas as entradas de níveis superiores
   - Define nova entrada inicial baseada na banca atual
5. **Salva no banco** o novo estado
6. **Retorna informações** sobre o reset

## Diferença do endpoint `/resetar_historico`:
- `/resetar_historico`: Reseta TUDO (histórico + gerenciamento)
- `/resetar_gerenciamento`: Reseta APENAS o gerenciamento, mantendo histórico de trades

## Segurança:
- ✅ Contas REAL e PRACTICE isoladas
- ✅ Nova entrada calculada automaticamente
- ✅ Estado salvo no banco de dados
- ✅ Logs detalhados para auditoria 