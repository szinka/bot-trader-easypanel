# 🚀 EXEMPLOS DE USO - RESPOSTA INSTANTÂNEA

## ✅ **MELHORIAS IMPLEMENTADAS:**

### **1. Resposta Instantânea**
- ✅ **Não espera** mais o resultado do trade
- ✅ **Retorna imediatamente** após executar a ordem
- ✅ **Mostra saldo** e informações do trade

### **2. Validação de Saldo**
- ✅ **Verifica saldo** antes de executar
- ✅ **Mensagem clara** se não tiver saldo
- ✅ **Evita erros** de saldo insuficiente

## 🎯 **NOVOS ENDPOINTS:**

### **1. Verificar Saldo de Uma Conta:**
```bash
GET /get_saldo?tipo_conta=PRACTICE
```

**Resposta:**
```json
{
  "status": "sucesso",
  "saldo": 10870.65,
  "conta": "PRACTICE",
  "mensagem": "Saldo atual na conta PRACTICE: $10870.65"
}
```

### **2. Verificar Saldo de Ambas as Contas:**
```bash
GET /get_saldos
```

**Resposta:**
```json
{
  "status": "sucesso",
  "saldos": {
    "PRACTICE": {
      "saldo": 10870.65,
      "disponivel": true
    },
    "REAL": {
      "saldo": 0.0,
      "disponivel": false
    }
  },
  "mensagem": "PRACTICE: $10870.65 | REAL: $0.0"
}
```

### **3. Trade com Resposta Instantânea:**
```bash
POST /trade
{
  "ativo": "EURUSD-OTC",
  "acao": "call",
  "duracao": 5,
  "tipo_conta": "PRACTICE",
  "valor_entrada": 10
}
```

**Resposta Instantânea:**
```json
{
  "status": "sucesso",
  "mensagem": "Trade executado com sucesso!",
  "trade_info": {
    "ativo": "EURUSD-OTC",
    "acao": "call",
    "duracao": 5,
    "tipo_conta": "PRACTICE",
    "valor_investido": 10,
    "saldo_anterior": 10870.65,
    "order_id": "12345"
  },
  "saldo_atual": 10870.65,
  "conta": "PRACTICE"
}
```

## 🚨 **EXEMPLOS DE ERRO:**

### **1. Saldo Insuficiente:**
```bash
POST /trade
{
  "ativo": "EURUSD-OTC",
  "acao": "call",
  "duracao": 5,
  "tipo_conta": "REAL",
  "valor_entrada": 10
}
```

**Resposta de Erro:**
```json
{
  "status": "erro",
  "mensagem": "Saldo insuficiente na conta REAL. Saldo atual: $0.00"
}
```

### **2. Valor Excede 5% da Banca:**
```bash
POST /trade
{
  "ativo": "EURUSD-OTC",
  "acao": "call",
  "duracao": 5,
  "tipo_conta": "PRACTICE",
  "valor_entrada": 1000
}
```

**Resposta de Erro:**
```json
{
  "status": "erro",
  "mensagem": "Valor de entrada (1000) excede 5% da banca (543.53)"
}
```

## 🔧 **CONFIGURAÇÃO NO N8N:**

### **1. Verificar Saldo Primeiro:**
```json
{
  "method": "GET",
  "url": "https://seu-dominio.vi7m8l.easypanel.host/get_saldos",
  "options": {}
}
```

### **2. Trade com Resposta Instantânea:**
```json
{
  "method": "POST",
  "url": "https://seu-dominio.vi7m8l.easypanel.host/trade",
  "sendBody": true,
  "specifyBody": "json",
  "jsonBody": "={\n  \"ativo\": \"EURUSD-OTC\",\n  \"acao\": \"{{ $json.message.content }}\",\n  \"duracao\": 5,\n  \"tipo_conta\": \"PRACTICE\",\n  \"valor_entrada\": 10\n}",
  "options": {}
}
```

## 💰 **VANTAGENS:**

### **1. Resposta Instantânea:**
- ✅ **Não trava** o n8n
- ✅ **Feedback imediato** para o usuário
- ✅ **Pode executar** múltiplos trades rapidamente

### **2. Validação Clara:**
- ✅ **Mostra saldo** antes de executar
- ✅ **Evita erros** de saldo insuficiente
- ✅ **Mensagens claras** de erro

### **3. Informações Completas:**
- ✅ **Saldo atual** na resposta
- ✅ **Detalhes do trade** executado
- ✅ **Order ID** para rastreamento

## 🎉 **RESULTADO:**

**Agora você tem:**
- ✅ **Resposta instantânea** sem esperar resultado
- ✅ **Validação de saldo** clara
- ✅ **Feedback imediato** para o usuário
- ✅ **Sistema mais rápido** e responsivo

**Perfeito para uso em n8n e automações!** 🚀 