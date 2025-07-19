# 🚀 CONFIGURAÇÃO NO EASYPANEL

## 📋 **Passo a Passo:**

### 1. **Criar Novo Projeto**
- Acesse seu EasyPanel
- Clique em **"New Project"**
- Escolha **"Docker Compose"**
- Nome: `bot-trader`

### 2. **Upload dos Arquivos**
Faça upload destes arquivos para o projeto:
- ✅ `docker-compose.yml`
- ✅ `Dockerfile`
- ✅ `requirements.txt`
- ✅ Pasta `API/` completa

### 3. **Configurar Variáveis de Ambiente**
No EasyPanel, adicione estas variáveis:

```
# Credenciais IQ Option
IQ_EMAIL=seu_email_iqoption@exemplo.com
IQ_PASSWORD=sua_senha_iqoption

# Banco de Dados (use o que já tem configurado)
DATABASE_URL=postgres://teste:dbfafd3ad79f44b4da88@chatwoot_teste:5432/teste?sslmode=disable

# Configurações do Gerenciamento
ENTRY_PERCENTAGE=5.0
GERENCIAMENTO_PERCENT=5.0
WINS_TO_LEVEL_UP=5
LOSS_COMPENSATION=1
```

### 4. **Configurar Banco de Dados**
- Use o banco PostgreSQL que já está criado
- Host: `easypanel.allkimy.academy`
- Porta: `5432`
- Database: `teste`
- User: `teste`
- Password: `dbfafd3ad79f44b4da88`

### 5. **Deploy**
- Clique em **"Deploy"**
- Aguarde o build completar
- Verifique os logs

## 🔧 **Configurações Importantes:**

### **Porta:**
- Interna: `8080`
- Externa: `8080`

### **Volumes:**
- `/app/logs` - Para logs da aplicação

### **Restart Policy:**
- `unless-stopped` - Reinicia automaticamente

## 📊 **Teste Após Deploy:**

### **1. Teste de Conectividade:**
```bash
curl http://seu-dominio:8080/ping
```
Resposta esperada: `{"status":"sucesso","mensagem":"pong"}`

### **2. Teste de Saldo:**
```bash
curl "http://seu-dominio:8080/get_saldo?tipo_conta=PRACTICE"
```

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

## 🎯 **Endpoints Disponíveis:**

- ✅ `GET /ping` - Teste de conectividade
- ✅ `GET /get_saldo` - Consulta saldo
- ✅ `POST /get_candles` - Busca candles
- ✅ `POST /trade` - Executa trades
- ✅ `GET /get_historico_trades` - Histórico
- ✅ `GET /get_estado_gerenciador` - Estado do gerenciador
- ✅ `POST /resetar_historico` - Reset

## 💰 **Como Usar:**

### **Trade Manual (Limitado a 10%):**
```json
{
    "tipo_conta": "REAL",
    "ativo": "EURUSD-OTC",
    "acao": "call",
    "duracao": 1,
    "valor_entrada": 50
}
```

### **Trade Automático (Sem limite):**
```json
{
    "tipo_conta": "REAL",
    "ativo": "EURUSD-OTC",
    "acao": "call",
    "duracao": 1,
    "valor_entrada": "gen"
}
```

## 🚨 **Troubleshooting:**

### **Se não conectar na IQ Option:**
- Verifique as credenciais no EasyPanel
- Confirme se a conta não está bloqueada

### **Se não conectar no banco:**
- Verifique se o banco está rodando
- Confirme as configurações de rede

### **Se o trade não executar:**
- Verifique se o ativo está disponível
- Confirme se o horário de mercado está aberto

## 🎉 **Pronto!**

Após o deploy, seu bot trader estará rodando no EasyPanel e pronto para ganhar dinheiro! 💰 