# 🤖 Bot Trader - API de Trading Automatizado

> **Sistema completo de trading automatizado integrado com IQ Option**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![EasyPanel](https://img.shields.io/badge/EasyPanel-Deploy-orange.svg)](https://easypanel.io)

## 🚀 Visão Geral

Bot Trader é uma API REST simples para execução automatizada de trades na IQ Option. O sistema realiza ordens binárias via HTTP, calculando o valor da entrada como percentual da banca (mínimo R$ 2, máximo 5%).

### ✨ Características

- 🔐 **Autenticação IQ Option**
- 💰 **Gerenciamento por Percentual** (mín. R$ 2, máx. 5%)
- 📊 **Múltiplas Contas** (REAL, PRACTICE e TORNEIO)
- 🐳 **Docker Ready**
- 🌐 **API REST**

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

# Trading Configuration
ENTRY_PERCENTAGE=3.0          # % padrão da banca por entrada
GERENCIAMENTO_PERCENT=5.0     # Limite máximo de % por entrada
```

### Configurações de Trading

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `ENTRY_PERCENTAGE` | % da banca por entrada | 3.0% |
| `GERENCIAMENTO_PERCENT` | Limite máximo de % por entrada | 5.0% |

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
    "reset_management": "/management/reset",
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
  "percent": 3
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
Stub sem persistência: retorna lista vazia.

### ⚙️ Gerenciamento
```http
GET /management?tipo_conta=PRACTICE
```
**Resposta:**
```json
{
  "status": "sucesso",
  "estado": {
    "total_wins": 7,
    "level_entries": {"1": 543.03, "2": 814.55},
    "nivel_atual": 2
  }
}
```

### 🔄 Resetar Gerenciamento
```http
POST /management/reset
Content-Type: application/json

{
  "tipo_conta": "PRACTICE"
}
```
**Resposta:**
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

### 🔄 Resetar Histórico (Completo)
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
python tests/test_integration.py
```

### Teste do Gerenciamento
```bash
# Testes unitários de cálculo percentual
```

### Teste de Segurança entre Contas
```bash
# Testa isolamento entre contas REAL e PRACTICE
python .cursor/test_seguranca_contas.py
```

### Teste do Endpoint de Reset
```bash
# Testa o endpoint de reset do gerenciamento
python .cursor/test_endpoint_reset.py
```

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
    "percent": 3
  }'
```

### 4. **Resetar Gerenciamento**
```bash
# Reset do gerenciamento pegando 5% da banca atual
curl -X POST http://localhost:8080/management/reset \
  -H "Content-Type: application/json" \
  -d '{"tipo_conta": "PRACTICE"}'
```

### 5. **Receber Sinais Automáticos**
O bot está pronto para receber sinais via API. Envie POST para `/trade` com:
- `ativo`: EURUSD-OTC, GBPUSD, etc.
- `acao`: "call" ou "put"
- `duracao`: 1, 5, 15 minutos
- `tipo_conta`: "PRACTICE" ou "REAL"
- `percent`: percentual da banca (default 3%, mínimo R$ 2, máximo 5%)

## 💰 Gerenciamento por Percentual

### 🎯 Lógica Atualizada

O sistema implementa gerenciamento simples por percentual de banca.

#### **📈 Progressão de Níveis**
- **5 wins consecutivos** para subir de nível
- **Aumento de 50%** apenas no UP de nível (não a cada vitória)
- **Isolamento completo** entre contas REAL e PRACTICE
- **Mínimo de R$ 2,00** em todas as entradas (inclusive após reset)

#### **📊 Exemplo de Progressão**
```
Banca inicial: $10
Nível 1: $2.00 (mínimo)
Nível 2: $3.00 (+50% sobre nível 1)
Nível 3: $4.50 (+50% sobre nível 2)
Nível 4: $6.75 (+50% sobre nível 3)
```

#### **🔄 Regras de Perda**
- **Perda normal**: -1 win
- **Perda com 0 wins no nível**: Volta ao nível anterior -2 wins
- **Exemplo**: Nível 3 com 0 wins → perde → volta para nível 2 com 3 wins

#### **🛡️ Segurança**
- ✅ **Contas isoladas**: REAL e PRACTICE completamente separadas
- ✅ **Reset inteligente**: Endpoint calcula nova entrada como 10% da banca atual (mínimo R$ 2,00)
- ✅ **Mínimo garantido**: Todas as entradas respeitam mínimo de R$ 2,00
- ✅ **Persistência**: Estados salvos no banco de dados
- ✅ **Logs detalhados**: Monitoramento completo das operações

### 🔄 Endpoint de Reset

#### **Reset do Gerenciamento**
```bash
# Reset pegando 10% da banca atual (mínimo R$ 2,00)
curl -X POST http://localhost:8080/management/reset \
  -H "Content-Type: application/json" \
  -d '{"tipo_conta": "PRACTICE"}'
```

#### **O que o reset faz:**
1. **Seleciona a conta** especificada
2. **Pega o saldo atual** da conta
3. **Calcula nova entrada** como 10% da banca atual (mínimo R$ 2,00)
4. **Reseta o gerenciamento**:
   - Zera total_wins
   - Remove entradas de níveis superiores
   - Define nova entrada inicial
5. **Salva no banco** o novo estado

## NOVA LÓGICA DE GERENCIAMENTO DE ENTRADA

Agora, o valor de entrada para cada operação é calculado como percentual da banca.

- Se você enviar `"percent": 3`, a operação usará 3% do saldo atual.
- Se não informar, será usado o padrão de 3% do saldo.
- O valor mínimo de entrada é R$ 2,00.
- O gerenciamento por nível não influencia mais o valor da operação.

**Exemplo de requisição:**

```json
{
  "ativo": "EURUSD",
  "acao": "call",
  "duracao": 5,
  "tipo_conta": "REAL",
  "percent": 3
}
```

Esse exemplo fará uma operação usando 15% do saldo da conta REAL.

## 🐳 Deploy com EasyPanel

### 1. **Configuração no EasyPanel**
- **Repository**: `https://github.com/szinka/bot-trader-easypanel`
- **Branch**: `main`
- **Port**: `8080`

### 2. **Variáveis de Ambiente**
```env
IQ_EMAIL=seu_email@iqoption.com
IQ_PASSWORD=sua_senha
 
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

# Testar reset do gerenciamento
curl -X POST http://localhost:8080/management/reset \
  -H "Content-Type: application/json" \
  -d '{"tipo_conta":"PRACTICE"}'
```

## 📊 Monitoramento

### Logs Importantes
- `INFO - Conectando à IQ Option...` - Início da conexão
- `INFO - Conexão com IQ Option bem-sucedida.` - Conexão OK
- `INFO - Saldo inicial (PRACTICE): $10860.65` - Saldo carregado
- `INFO - Trade executado com sucesso!` - Trade realizado
- `INFO - Subiu para nível X, nova entrada: $Y` - UP de nível
- `INFO - Perdeu com 0 wins no nível X, voltou para nível Y -2 wins` - Regra de perda

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
- ✅ **Teste sempre** na conta PRACTICE primeiro

### Variáveis Sensíveis
```env
# NUNCA commite estas variáveis
IQ_EMAIL=seu_email@iqoption.com
IQ_PASSWORD=sua_senha
 
```

## 📞 Suporte

### Verificação Rápida
```bash
# 1. Status da API
curl http://localhost:8080/status

# 2. Saldo da conta
curl http://localhost:8080/balance?tipo_conta=PRACTICE

# 3. Estado do gerenciamento
curl http://localhost:8080/management?tipo_conta=PRACTICE

# 4. Teste de trade
curl -X POST http://localhost:8080/trade \
  -H "Content-Type: application/json" \
  -d '{"ativo":"EURUSD-OTC","acao":"call","duracao":5,"tipo_conta":"PRACTICE","valor_entrada":10}'

# 5. Reset do gerenciamento
curl -X POST http://localhost:8080/management/reset \
  -H "Content-Type: application/json" \
  -d '{"tipo_conta":"PRACTICE"}'
```

### Problemas Comuns
1. **Conexão IQ Option** - Verifique credenciais
2. **Trade Rejeitado** - Use EURUSD-OTC, verifique saldo
3. **Deploy Falhou** - Verifique Dockerfile e variáveis
4. **Gerenciamento** - Endpoint de reset é stub
5. **Gerenciamento** - Use endpoint de reset para corrigir

---

**⚠️ Aviso:** Trading envolve riscos. Use apenas com dinheiro que pode perder.

**🔒 Segurança:** Nunca compartilhe suas credenciais IQ Option.

**💰 Sucesso:** Sistema testado e funcionando com EURUSD-OTC e gerenciamento por percentual.

**🔄 Atualizações Recentes:**
 
- ✅ 5 wins para subir de nível
- ✅ Aumento de 50% apenas no UP de nível
- ✅ Regra de perda com 0 wins implementada
- ✅ Endpoint de reset do gerenciamento
- ✅ Isolamento completo entre contas
- ✅ Testes completos adicionados 