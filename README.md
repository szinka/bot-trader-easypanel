# 🤖 Bot Trader - API de Trading Automatizado

> **Sistema completo de trading automatizado integrado com IQ Option**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![EasyPanel](https://img.shields.io/badge/EasyPanel-Deploy-orange.svg)](https://easypanel.io)

## 🚀 Visão Geral

Bot Trader é uma API REST completa para execução automatizada de trades na IQ Option. O sistema inclui gerenciamento de risco Torre MK, histórico de operações, múltiplas contas (Real/Practice) e interface de monitoramento.

### ✨ Características

- 🔐 **Autenticação IQ Option** - Conexão segura com a plataforma
- 💰 **Gerenciamento Torre MK** - Controle automático de entradas
- 📊 **Múltiplas Contas** - Suporte para conta Real e Practice
- 🗄️ **Banco PostgreSQL** - Histórico completo de trades
- 📈 **Monitoramento** - Logs detalhados e métricas
- 🐳 **Docker Ready** - Deploy simplificado
- 🌐 **API REST** - Endpoints padronizados

## 📋 Pré-requisitos

- Python 3.8+
- PostgreSQL
- Conta IQ Option
- Docker (opcional)

## 🛠️ Instalação

### Método 1: Local

```bash
# Clone o repositório
git clone https://github.com/szinka/bot-trader-easypanel.git
cd bot-trader-easypanel

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp env.example .env
# Edite o arquivo .env com suas credenciais
```

### Método 2: Docker

```bash
# Clone e execute com Docker Compose
git clone https://github.com/szinka/bot-trader-easypanel.git
cd bot-trader-easypanel

# Configure o .env
cp env.example .env

# Execute
docker-compose up -d
```

## ⚙️ Configuração

### Variáveis de Ambiente

```env
# IQ Option Credentials (OBRIGATÓRIO)
IQ_EMAIL=seu_email@exemplo.com
IQ_PASSWORD=sua_senha

# Database (OPCIONAL - usa SQLite se não configurado)
DATABASE_URL=postgres://user:password@host:5432/database?sslmode=disable

# Trading Configuration
ENTRY_PERCENTAGE=5.0          # % da banca por entrada
GERENCIAMENTO_PERCENT=5.0     # % para gerenciamento
WINS_TO_LEVEL_UP=5            # Wins para subir nível
LOSS_COMPENSATION=1           # Compensação de perdas
```

### Configurações de Trading

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `ENTRY_PERCENTAGE` | % da banca por entrada | 5.0% |
| `GERENCIAMENTO_PERCENT` | % para gerenciamento | 5.0% |
| `WINS_TO_LEVEL_UP` | Wins para subir nível | 5 |
| `LOSS_COMPENSATION` | Compensação de perdas | 1 |

## 🚀 Execução

```bash
# Inicie o servidor para desenvolvimento
python main.py

# Ou para produção (recomendado)
gunicorn -b 0.0.0.0:8080 API.api_server:app

# Ou com Docker
docker-compose up -d
```

O servidor estará disponível em: `http://localhost:8080`

## 📡 API Endpoints

### 🔍 Status da API
```http
GET /
```
**Resposta:**
```json
{
  "status": "sucesso",
  "mensagem": "Bot Trader API funcionando",
  "endpoints": {
    "trade": "/trade",
    "balance": "/balance",
    "history": "/history",
    "management": "/management",
    "status": "/status"
  }
}
```

### 👤 Consultar Perfil (Moeda da Conta)
```http
GET /profile?tipo_conta=PRACTICE
```
**Resposta:**
```json
{
  "status": "sucesso",
  "conta": "PRACTICE",
  "moeda": "USD"
}
```

### 💰 Consultar Saldo
```http
GET /balance?tipo_conta=PRACTICE
```
**Resposta:**
```json
{
  "status": "sucesso",
  "saldo": 10860.65,
  "conta": "PRACTICE",
  "moeda": "USD",
  "mensagem": "Saldo atual na conta PRACTICE: USD 10860.65"
}
```

### 🎯 Executar Trade
```http
POST /trade
Content-Type: application/json

{
  "ativo": "EURUSD-OTC",
  "acao": "call",
  "duracao": 5,
  "tipo_conta": "PRACTICE",
  "valor_entrada": 10
}
```
**Resposta:**
```json
{
  "status": "sucesso",
  "mensagem": "Trade executado com sucesso!",
  "trade_info": {
    "ativo": "EURUSD-OTC",
    "acao": "call",
    "duracao": 5,
    "tipo_conta": "PRACTICE",
    "valor_investido": 10.0,
    "saldo_anterior": 10870.65,
    "order_id": "12866120951"
  },
  "saldo_atual": 10870.65,
  "conta": "PRACTICE"
}
```

### 📊 Histórico de Trades
```http
GET /history?tipo_conta=PRACTICE
```
**Resposta:**
```json
{
  "status": "sucesso",
  "historico": [
    {
      "id": 1,
      "ativo": "EURUSD-OTC",
      "acao": "call",
      "valor_investido": 10.0,
      "resultado": "win",
      "lucro": 9.0,
      "data": "2025-07-19T10:30:00"
    }
  ]
}
```

### ⚙️ Gerenciamento
```http
GET /management?tipo_conta=PRACTICE
```
**Resposta:**
```json
{
  "status": "sucesso",
  "estado": {
    "total_wins": 0,
    "level_entries": {"1": 543.03},
    "nivel_atual": 1
  }
}
```

### 🔄 Resetar Histórico
```http
POST /management/reset
Content-Type: application/json

{
  "tipo_conta": "PRACTICE"
}
```

### 📈 Status Geral
```http
GET /status
```
**Resposta:**
```json
{
  "status": "sucesso",
  "mensagem": "pong"
}
```

## 🧪 Testes Automáticos

### Teste Completo da API
```bash
# Testa todos os endpoints automaticamente
python API/test_all_endpoints.py
```

Este script testa:
- ✅ Status da API (`/status`)
- ✅ Consulta de saldo (`/balance`)
- ✅ Busca de candles (`/get_candles`)
- ✅ Execução de trades (`/trade`)
- ✅ Histórico de trades (`/history`)
- ✅ Gerenciamento (`/management`)

---

## 🎯 Como Usar o Bot

### 1. **Configuração Inicial**
```bash
# Configure suas credenciais
IQ_EMAIL=seu_email@iqoption.com
IQ_PASSWORD=sua_senha

# Inicie o servidor
python main.py
```

### 2. **Teste de Conexão**
```bash
# Teste se está funcionando
curl http://localhost:8080/status

# Verifique o saldo
curl http://localhost:8080/balance?tipo_conta=PRACTICE
```

### 3. **Executar Trade Manual**
```bash
curl -X POST http://localhost:8080/trade \
  -H "Content-Type: application/json" \
  -d '{
    "ativo": "EURUSD-OTC",
    "acao": "call",
    "duracao": 5,
    "tipo_conta": "PRACTICE",
    "valor_entrada": 10
  }'
```

### 4. **Receber Sinais Automáticos**
O bot está pronto para receber sinais via API. Envie POST para `/trade` com:
- `ativo`: EURUSD-OTC, GBPUSD, etc.
- `acao`: "call" ou "put"
- `duracao`: 1, 5, 15 minutos
- `tipo_conta`: "PRACTICE" ou "REAL"
- `valor_entrada`: valor específico ou "gen" para gerenciamento automático

## 💰 Gerenciamento de Risco

### Torre MK
- **Nível 1**: 5% da banca
- **Subida de Nível**: A cada 5 wins consecutivos
- **Compensação**: -1 win por loss, -2 wins se vai cair de nível

### Exemplo de Progressão
```
Nível 1: $543.03 (5% de $10,860)
Nível 2: $1,086.07 (10% de $10,860)
Nível 3: $1,629.10 (15% de $10,860)
```

## 🐳 Deploy com EasyPanel

### 1. **Configuração no EasyPanel**
- **Repository**: `https://github.com/szinka/bot-trader-easypanel`
- **Branch**: `main`
- **Port**: `8080`

### 2. **Variáveis de Ambiente**
```env
IQ_EMAIL=seu_email@iqoption.com
IQ_PASSWORD=sua_senha
DATABASE_URL=postgres://user:pass@host:5432/db
ENTRY_PERCENTAGE=5.0
WINS_TO_LEVEL_UP=5
LOSS_COMPENSATION=1
```

### 3. **Deploy Automático**
- EasyPanel detecta mudanças no GitHub
- Build automático com Docker
- Deploy em produção

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Erro de Conexão IQ Option
```
ERRO CRÍTICO: IQOptionAPI.__init__() missing 1 required positional argument: 'password'
```
**Solução:** Verifique as credenciais no arquivo `.env`

#### 2. Erro de Banco de Dados
```
could not translate host name "chatwoot_teste" to address
```
**Solução:** Configure corretamente a `DATABASE_URL`

#### 3. Trade Rejeitado
```
"Ordem rejeitada em Binária e Digital"
```
**Solução:** 
- Verifique se o ativo está aberto (EURUSD-OTC funciona)
- Confirme se tem saldo suficiente
- Use duração válida (1, 5, 15 minutos)

#### 4. Bad Gateway no Deploy
```
Bad gateway - the service failed to handle your request
```
**Solução:** 
- Verifique se o serviço está rodando
- Confirme as variáveis de ambiente
- Verifique os logs do container

### Logs Úteis

```bash
# Ver logs do container
docker-compose logs -f bot-trader

# Testar conexão local
curl http://localhost:8080/status

# Testar trade local
curl -X POST http://localhost:8080/trade \
  -H "Content-Type: application/json" \
  -d '{"ativo":"EURUSD-OTC","acao":"call","duracao":5,"tipo_conta":"PRACTICE","valor_entrada":10}'
```

## 📊 Monitoramento

### Logs Importantes
- `INFO - Conectando à IQ Option...` - Início da conexão
- `INFO - Conexão com IQ Option bem-sucedida.` - Conexão OK
- `INFO - Saldo inicial (PRACTICE): $10860.65` - Saldo carregado
- `INFO - Trade executado com sucesso!` - Trade realizado

### Métricas
- **Saldo Atual** - Consulta via `/balance`
- **Histórico** - Consulta via `/history`
- **Performance** - Win rate calculado automaticamente
- **Gerenciamento** - Status via `/management`

## 🎯 Ativos Suportados

### Ativos Testados e Funcionais
- **EURUSD-OTC** ✅ (Recomendado)
- **GBPUSD-OTC** ✅
- **EURUSD** ⚠️ (Pode ter restrições)
- **GBPUSD** ⚠️ (Pode ter restrições)

### Durações Suportadas
- **1 minuto** ✅
- **5 minutos** ✅
- **15 minutos** ✅

## 🔒 Segurança

### Boas Práticas
- ✅ **Nunca compartilhe** suas credenciais IQ Option
- ✅ **Use sempre HTTPS** em produção
- ✅ **Configure firewall** adequadamente
- ✅ **Monitore logs** regularmente
- ✅ **Faça backup** do banco de dados

### Variáveis Sensíveis
```env
# NUNCA commite estas variáveis
IQ_EMAIL=seu_email@iqoption.com
IQ_PASSWORD=sua_senha
DATABASE_URL=postgres://user:pass@host:5432/db
```

## 📞 Suporte

### Verificação Rápida
```bash
# 1. Status da API
curl http://localhost:8080/status

# 2. Saldo da conta
curl http://localhost:8080/balance?tipo_conta=PRACTICE

# 3. Teste de trade
curl -X POST http://localhost:8080/trade \
  -H "Content-Type: application/json" \
  -d '{"ativo":"EURUSD-OTC","acao":"call","duracao":5,"tipo_conta":"PRACTICE","valor_entrada":10}'
```

### Problemas Comuns
1. **Conexão IQ Option** - Verifique credenciais
2. **Trade Rejeitado** - Use EURUSD-OTC, verifique saldo
3. **Deploy Falhou** - Verifique Dockerfile e variáveis
4. **Banco de Dados** - Configure DATABASE_URL

---

**⚠️ Aviso:** Trading envolve riscos. Use apenas com dinheiro que pode perder.

**🔒 Segurança:** Nunca compartilhe suas credenciais IQ Option.

**💰 Sucesso:** Sistema testado e funcionando com EURUSD-OTC! 