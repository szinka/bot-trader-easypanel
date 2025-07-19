# 🔧 CONFIGURAÇÃO DO .ENV

## 📝 **Arquivo .env que você deve usar:**

```env
# Configurações do Bot Trader

# Credenciais IQ Option
IQ_EMAIL=szinkamiza@gmail.com
IQ_PASSWORD=123lucas123

# Configurações do Banco de Dados
DATABASE_URL=postgres://teste:dbfafd3ad79f44b4da88@chatwoot_teste:5432/teste?sslmode=disable

# Configurações do Gerenciamento
ENTRY_PERCENTAGE=5.0
GERENCIAMENTO_PERCENT=5.0
WINS_TO_LEVEL_UP=5
LOSS_COMPENSATION=1

# Configurações da API
API_HOST=0.0.0.0
API_PORT=8080
```

## 🎯 **Principais Mudanças:**

### **GERENCIAMENTO_PERCENT=5.0**
- ✅ **Padrão**: Gerenciamento usa 5% da banca
- ✅ **Configurável**: Pode alterar via variável de ambiente
- ✅ **Consistente**: Mesmo padrão do ENTRY_PERCENTAGE

### **ENTRY_PERCENTAGE=5.0**
- ✅ **Entrada manual**: Limitada a 5% da banca
- ✅ **Entrada automática**: Usa GERENCIAMENTO_PERCENT (5%)

## 💰 **Como funciona agora:**

### **Trade Manual (Limitado a 5%):**
```json
{
    "tipo_conta": "REAL",
    "ativo": "EURUSD-OTC",
    "acao": "call",
    "duracao": 1,
    "valor_entrada": 50  # Máximo 5% da banca
}
```

### **Trade Automático (Usa 5%):**
```json
{
    "tipo_conta": "REAL",
    "ativo": "EURUSD-OTC",
    "acao": "call",
    "duracao": 1,
    "valor_entrada": "gen"  # Usa 5% da banca
}
```

## 🔄 **Para mudar a porcentagem:**

1. **No .env local**: Mude `GERENCIAMENTO_PERCENT=5.0` para o valor desejado
2. **No EasyPanel**: Mude a variável `GERENCIAMENTO_PERCENT` para o valor desejado
3. **Reinicie** o sistema

## ✅ **Pronto para usar!**

Agora você tem **controle total** da porcentagem do gerenciamento! 🎉 