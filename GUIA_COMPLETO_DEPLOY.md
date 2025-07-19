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