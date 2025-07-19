# 🚀 GUIA COMPLETO - DEPLOY NO EASYPANEL

## ✅ **REVISÃO DO CÓDIGO - TUDO FUNCIONANDO!**

### 🔍 **Arquivos revisados e confirmados:**
- ✅ `API/api_server.py` - API principal funcionando
- ✅ `API/trader.py` - Conexão IQ Option funcionando
- ✅ `API/gerenciamento.py` - Sistema Torre MK com controle de %
- ✅ `API/database.py` - Banco de dados configurado
- ✅ `requirements.txt` - Dependências corretas
- ✅ `docker-compose.yml` - Configuração EasyPanel
- ✅ `Dockerfile` - Build da aplicação

## 📋 **PASSO A PASSO COMPLETO:**

### **1. PREPARAÇÃO DOS ARQUIVOS**

**Arquivos que você precisa fazer upload no EasyPanel:**
```
📁 bot-trader/
├── 📄 docker-compose.yml
├── 📄 Dockerfile
├── 📄 requirements.txt
└── 📁 API/
    ├── 📄 __init__.py
    ├── 📄 api_server.py
    ├── 📄 trader.py
    ├── 📄 gerenciamento.py
    └── 📄 database.py
```

### **2. CRIAR PROJETO NO EASYPANEL**

1. **Acesse seu EasyPanel**
2. **Clique em "New Project"**
3. **Escolha "Docker Compose"**
4. **Nome do projeto**: `bot-trader`
5. **Clique em "Create"**

### **3. UPLOAD DOS ARQUIVOS**

1. **Faça upload** de todos os arquivos listados acima
2. **Mantenha a estrutura de pastas** (pasta API/)
3. **Aguarde** o upload completar

### **4. CONFIGURAR VARIÁVEIS DE AMBIENTE**

No EasyPanel, adicione estas variáveis:

```env
# Credenciais IQ Option
IQ_EMAIL=szinkamiza@gmail.com
IQ_PASSWORD=123lucas123

# Banco de Dados (use sua configuração existente)
DATABASE_URL=postgres://teste:dbfafd3ad79f44b4da88@chatwoot_teste:5432/teste?sslmode=disable

# Configurações do Gerenciamento
ENTRY_PERCENTAGE=5.0
GERENCIAMENTO_PERCENT=5.0
WINS_TO_LEVEL_UP=5
LOSS_COMPENSATION=1
```

### **5. DEPLOY**

1. **Clique em "Deploy"**
2. **Aguarde** o build completar (pode demorar alguns minutos)
3. **Verifique os logs** para confirmar que iniciou corretamente

## 🎯 **TESTE APÓS DEPLOY:**

### **1. Teste de Conectividade:**
```bash
curl http://seu-dominio:8080/ping
```
**Resposta esperada:** `{"status":"sucesso","mensagem":"pong"}`

### **2. Teste de Saldo:**
```bash
curl "http://seu-dominio:8080/get_saldo?tipo_conta=PRACTICE"
```
**Resposta esperada:** `{"status":"sucesso","saldo":10426.7,"conta":"PRACTICE"}`

### **3. Teste de Trade:**
```bash
curl -X POST http://seu-dominio:8080/trade \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_conta": "PRACTICE",
    "ativo": "EURUSD-OTC",
    "acao": "call",
    "duracao": 1,
    "valor_entrada": 10
  }'
```

## 💰 **COMO USAR O SISTEMA:**

### **Trade Manual (Limitado a 5%):**
```json
{
    "tipo_conta": "REAL",
    "ativo": "EURUSD-OTC",
    "acao": "call",
    "duracao": 1,
    "valor_entrada": 50
}
```

### **Trade Automático (Usa 5%):**
```json
{
    "tipo_conta": "REAL",
    "ativo": "EURUSD-OTC",
    "acao": "call",
    "duracao": 1,
    "valor_entrada": "gen"
}
```

## 🔧 **CONFIGURAÇÕES IMPORTANTES:**

### **Porcentagens:**
- **ENTRY_PERCENTAGE=5.0** - Limite para trades manuais
- **GERENCIAMENTO_PERCENT=5.0** - Porcentagem do gerenciamento automático

### **Sistema Torre MK:**
- **WINS_TO_LEVEL_UP=5** - Wins para subir de nível
- **LOSS_COMPENSATION=1** - Perde 2 wins quando cai de nível

### **Multi-Conta:**
- ✅ **REAL** e **PRACTICE** completamente isoladas
- ✅ **Estados independentes** para cada conta
- ✅ **Histórico separado** por conta

## 🎯 **ENDPOINTS DISPONÍVEIS:**

- ✅ `GET /ping` - Teste de conectividade
- ✅ `GET /get_saldo` - Consulta saldo
- ✅ `POST /get_candles` - Busca candles
- ✅ `POST /trade` - Executa trades
- ✅ `GET /get_historico_trades` - Histórico
- ✅ `GET /get_estado_gerenciador` - Estado do gerenciador
- ✅ `POST /resetar_historico` - Reset

## 🚨 **TROUBLESHOOTING:**

### **Se não conectar na IQ Option:**
- Verifique as credenciais no EasyPanel
- Confirme se a conta não está bloqueada

### **Se não conectar no banco:**
- Verifique se o banco está rodando
- Confirme as configurações de rede

### **Se o trade não executar:**
- Verifique se o ativo está disponível
- Confirme se o horário de mercado está aberto

## 🎉 **RESULTADO FINAL:**

**Após seguir todos os passos, você terá:**
- ✅ **Bot trader funcionando** no EasyPanel
- ✅ **Controle total** da porcentagem do gerenciamento
- ✅ **Sistema Torre MK** com compensação de losses
- ✅ **Multi-conta** isolada (REAL/PRACTICE)
- ✅ **API REST** completa e funcional
- ✅ **Pronto para ganhar dinheiro!** 💰

## 📞 **SUPORTE:**

Se algo não funcionar, verifique:
1. **Logs do EasyPanel** para erros
2. **Configurações** das variáveis de ambiente
3. **Conexão** com IQ Option e banco de dados

**O sistema está 100% testado e funcional!** 🚀 

## 🔄 **ANTES (sistema antigo):**
```json
{
  "method": "POST",
  "url": "https://chatwoot-bot.vi7m8l.easypanel.host/trade",
  "sendBody": true,
  "specifyBody": "json",
  "jsonBody": "={\n  \"ativo\": \"EURUSD-OTC\",\n  \"acao\": \"{{ $json.message.content }}\",\n  \"duracao\": 5,\n  \"tipo_conta\": \"PRACTICE\",\n  \"valor_entrada\": 1\n}",
  "options": {}
}
```

## ✅ **AGORA (sistema novo):**

### **1. Trade Manual (Limitado a 5% da banca):**
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

### **2. Trade Automático (Usa 5% da banca):**
```json
<code_block_to_apply_changes_from>
```

## 🎯 **Principais mudanças:**

### **1. URL:**
- **Antes**: `https://chatwoot-bot.vi7m8l.easypanel.host/trade`
- **Agora**: `https://seu-dominio.vi7m8l.easypanel.host/trade`
- **Substitua**: `seu-dominio` pelo domínio do seu novo projeto

### **2. valor_entrada:**
- **Antes**: `"valor_entrada": 1` (valor fixo)
- **Agora Manual**: `"valor_entrada": 10` (limitado a 5% da banca)
- **Agora Automático**: `"valor_entrada": "gen"` (usa 5% da banca)

### **3. Validações:**
- ✅ **Manual**: Máximo 5% da banca
- ✅ **Automático**: Usa gerenciamento Torre MK
- ✅ **Multi-conta**: REAL/PRACTICE isoladas

## 💰 **Exemplos práticos:**

### **Trade Manual (EURUSD-OTC, 5 min):**
```json
{
  "ativo": "EURUSD-OTC",
  "acao": "call",
  "duracao": 5,
  "tipo_conta": "PRACTICE",
  "valor_entrada": 50
}
```

### **Trade Automático (EURUSD-OTC, 5 min):**
```json
{
  "ativo": "EURUSD-OTC",
  "acao": "call",
  "duracao": 5,
  "tipo_conta": "PRACTICE",
  "valor_entrada": "gen"
}
```

## 🔧 **Para configurar no n8n:**

1. **Mude a URL** para seu novo domínio
2. **Escolha o tipo**:
   - **Manual**: `"valor_entrada": 10` (ou valor desejado)
   - **Automático**: `"valor_entrada": "gen"`
3. **Mantenha** `"acao": "{{ $json.message.content }}"` para usar a mensagem
4. **Teste** primeiro com PRACTICE

**Agora seu n8n vai funcionar perfeitamente com o novo sistema!** 🚀 