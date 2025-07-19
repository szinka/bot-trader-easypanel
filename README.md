# 🤖 Bot Trader - API de Trading Automatizado

> **Sistema completo de trading automatizado integrado com IQ Option**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![EasyPanel](https://img.shields.io/badge/EasyPanel-Deploy-orange.svg)](https://easypanel.io)

## 🚀 Visão Geral

Bot Trader é uma API REST completa para execução automatizada de trades na IQ Option. O sistema inclui gerenciamento de risco, histórico de operações, múltiplas contas (Real/Practice) e interface de monitoramento.

### ✨ Características

- 🔐 **Autenticação IQ Option** - Conexão segura com a plataforma
- 💰 **Gerenciamento de Risco** - Controle automático de entradas
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
# IQ Option Credentials
IQ_EMAIL=seu_email@exemplo.com
IQ_PASSWORD=sua_senha

# Database
DATABASE_URL=postgres://user:password@host:5432/database?sslmode=disable

# Trading Configuration
ENTRY_PERCENTAGE=5.0
WINS_TO_LEVEL_UP=5
LOSS_COMPENSATION=1
```

### Configurações de Trading

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `ENTRY_PERCENTAGE` | % da banca por entrada | 5.0% |
| `WINS_TO_LEVEL_UP` | Wins para subir nível | 5 |
| `LOSS_COMPENSATION` | Compensação de perdas | 1 |

## 🚀 Execução

```bash
# Inicie o servidor
python main.py

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

### 💰 Consultar Saldo
```http
GET /balance?tipo_conta=PRACTICE
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
      "valor_investido": 50.0,
      "resultado": "win",
      "lucro": 45.0,
      "data": "2025-07-19T10:30:00"
    }
  ]
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
  "valor_entrada": 1
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
    "valor_investido": 50.0,
    "saldo_anterior": 10870.65,
    "order_id": "12345"
  },
  "saldo_atual": 10870.65,
  "conta": "PRACTICE"
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
    "nivel_atual": 1,
    "wins_consecutivos": 3,
    "proxima_entrada": 75.0,
    "banca_atual": 10870.65
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

## 🐳 Deploy com Docker

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["python", "main.py"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  bot-trader:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/trader
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: trader
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

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

#### 3. Bad Gateway no Deploy
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
  -d '{"ativo":"EURUSD-OTC","acao":"call","duracao":5,"tipo_conta":"PRACTICE","valor_entrada":1}'
```

## 📊 Monitoramento

### Logs Importantes
- `INFO - Conectando à IQ Option...` - Início da conexão
- `INFO - Conexão com IQ Option bem-sucedida.` - Conexão OK
- `INFO - Saldo inicial (PRACTICE): $10870.65` - Saldo carregado
- `INFO - Trade executado com sucesso!` - Trade realizado

### Métricas
- **Saldo Atual** - Consulta via `/balance`
- **Histórico** - Consulta via `/history`
- **Performance** - Win rate calculado automaticamente
- **Gerenciamento** - Status via `/management`

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é privado e não possui licença pública.

## 📞 Suporte

Para suporte técnico ou dúvidas:
- Verifique os logs do sistema
- Teste os endpoints localmente
- Confirme as configurações de ambiente

---

**⚠️ Aviso:** Trading envolve riscos. Use apenas com dinheiro que pode perder.

**🔒 Segurança:** Nunca compartilhe suas credenciais IQ Option. 