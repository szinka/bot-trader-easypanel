# Exemplo de Uso do Endpoint de Reset de Gerenciamento

## Endpoint

```
POST /management/reset
Content-Type: application/json

{
  "tipo_conta": "PRACTICE"
}
```

## O que o reset faz:
1. **Seleciona a conta** especificada (PRACTICE ou REAL)
2. **Pega o saldo atual** da conta
3. Stub sem efeito prático (apenas resposta de sucesso)

## Exemplo de resposta
```json
{
  "status": "sucesso",
  "mensagem": "Gerenciamento resetado para PRACTICE.",
  "dados": {
    "tipo_conta": "PRACTICE",
    
  }
}
```

## Observações
- O valor da entrada nunca será menor que R$ 2,00, mesmo com bancas pequenas.
- O reset não afeta o histórico de trades, apenas o gerenciamento Torre MK. 