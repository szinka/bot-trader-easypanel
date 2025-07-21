# Exemplo de Uso do Endpoint de Reset de Gerenciamento

## Endpoint

```
POST /resetar_gerenciamento
Content-Type: application/json

{
  "tipo_conta": "PRACTICE"
}
```

## O que o reset faz:
1. **Seleciona a conta** especificada (PRACTICE ou REAL)
2. **Pega o saldo atual** da conta
3. **Calcula nova entrada** como 10% da banca atual (mínimo R$ 2,00)
4. **Reseta o gerenciamento**:
   - Zera total_wins
   - Remove entradas de níveis superiores
   - Define nova entrada inicial
5. **Salva no banco** o novo estado

## Exemplo de resposta
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
      "level_entries": {"1": 10.0},
      "nivel_atual": 1
    }
  }
}
```

## Observações
- O valor da entrada nunca será menor que R$ 2,00, mesmo com bancas pequenas.
- O reset não afeta o histórico de trades, apenas o gerenciamento Torre MK. 