# 🤖 Bot Trader - Sistema de Trading Automatizado

Sistema completo de trading automatizado com interface web, API REST e integração IQ Option.

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.11+
- Docker (opcional)
- Conta IQ Option

### Instalação Local
```bash
# Clone o repositório
git clone https://github.com/szinka/bot-trader-easypanel.git
cd bot-trader-easypanel

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp env.example .env
# Edite o arquivo .env com suas credenciais

# Execute o servidor
python main.py
```

### Docker
```bash
# Build da imagem
docker build -t bot-trader .

# Executar container
docker run -p 8080:8080 --env-file .env bot-trader
```

## 🌐 Interface Web

Acesse: `http://localhost:8080`

### Funcionalidades da Interface:
- 📊 **Dashboard em tempo real**
- 💰 **Saldo Real vs Simulado** (toggle)
- 📈 **Gráfico de performance**
- 📋 **Histórico de trades**
- 🎯 **Win rate e estatísticas**

## 🔌 API REST - Endpoints

### Base URL: `http://localhost:8080`

### 1. **GET /balance** - Saldo Atual
```bash
curl http://localhost:8080/balance
```
**Resposta:**
```json
{
  "saldo": 10870.65,
  "conta": "PRACTICE",
  "moeda": "USD"
}
```

### 2. **GET /balance/{tipo}** - Saldo por Tipo de Conta
```bash
# Conta Real
curl http://localhost:8080/balance/real

# Conta Simulada
curl http://localhost:8080/balance/practice
```

### 3. **GET /candles/{ativo}** - Dados de Candles
```bash
curl http://localhost:8080/candles/EURUSD
```
**Parâmetros opcionais:**
- `timeframe`: 1, 5, 15, 30, 60 (minutos)
- `count`: número de candles (padrão: 100)

**Exemplo:**
```bash
curl "http://localhost:8080/candles/EURUSD?timeframe=5&count=50"
```

### 4. **GET /history** - Histórico de Trades
```bash
curl http://localhost:8080/history
```
**Resposta:**
```json
{
  "trades": [
    {
      "id": 1,
      "ativo": "EURUSD",
      "acao": "CALL",
      "valor": 10.0,
      "resultado": "WIN",
      "lucro": 8.0,
      "data": "2025-07-19 10:30:00"
    }
  ],
  "total_trades": 50,
  "wins": 35,
  "win_rate": 70.0
}
```

### 5. **GET /management** - Status do Gerenciamento
```bash
curl http://localhost:8080/management
```
**Resposta:**
```json
{
  "ativo": true,
  "nivel_atual": 3,
  "wins_consecutivos": 2,
  "entrada_atual": 10.0,
  "proxima_entrada": 15.0,
  "estrategia": "Torre MK"
}
```

### 6. **POST /management/start** - Iniciar Gerenciamento
```bash
curl -X POST http://localhost:8080/management/start
```

### 7. **POST /management/stop** - Parar Gerenciamento
```bash
curl -X POST http://localhost:8080/management/stop
```

### 8. **POST /management/reset** - Resetar Gerenciamento
```bash
curl -X POST http://localhost:8080/management/reset
```

### 9. **POST /trade** - Executar Trade Manual
```bash
curl -X POST http://localhost:8080/trade \
  -H "Content-Type: application/json" \
  -d '{
    "ativo": "EURUSD",
    "acao": "CALL",
    "valor": 10.0,
    "duracao": 5
  }'
```

### 10. **GET /performance** - Dados de Performance
```bash
curl http://localhost:8080/performance
```
**Resposta:**
```json
{
  "saldo_inicial": 10000.0,
  "saldo_atual": 10870.65,
  "lucro_total": 870.65,
  "percentual_lucro": 8.7,
  "total_trades": 50,
  "wins": 35,
  "losses": 15,
  "win_rate": 70.0,
  "maior_sequencia_wins": 8,
  "maior_sequencia_losses": 3
}
```

### 11. **GET /status** - Status Geral do Sistema
```bash
curl http://localhost:8080/status
```
**Resposta:**
```json
{
  "status": "online",
  "conexao_iq": true,
  "conexao_db": true,
  "gerenciamento_ativo": false,
  "ultima_atualizacao": "2025-07-19 10:30:00",
  "versao": "3.6"
}
```

## 🔧 Configuração

### Variáveis de Ambiente (.env)
```env
# Credenciais IQ Option
IQ_EMAIL=seu_email@exemplo.com
IQ_PASSWORD=sua_senha

# Banco de Dados
DATABASE_URL=postgres://user:pass@host:port/db

# Configurações do Gerenciamento
ENTRY_PERCENTAGE=5.0
WINS_TO_LEVEL_UP=5
LOSS_COMPENSATION=1

# Servidor
FLASK_DEBUG=false
```

## 📊 Estratégia Torre MK

O sistema implementa a estratégia "Torre MK":

- **Progressão**: Aumenta entrada após wins consecutivos
- **Proteção**: Reseta após loss
- **Configurável**: Percentual de entrada e wins para subir nível

## 🛠️ Comandos Úteis

### Verificar Status
```bash
# Testar conexão IQ Option
curl http://localhost:8080/status

# Verificar saldo
curl http://localhost:8080/balance

# Ver performance
curl http://localhost:8080/performance
```

### Gerenciamento
```bash
# Iniciar sistema
curl -X POST http://localhost:8080/management/start

# Parar sistema
curl -X POST http://localhost:8080/management/stop

# Resetar
curl -X POST http://localhost:8080/management/reset
```

### Trades
```bash
# Trade manual CALL
curl -X POST http://localhost:8080/trade \
  -H "Content-Type: application/json" \
  -d '{"ativo":"EURUSD","acao":"CALL","valor":10.0,"duracao":5}'

# Trade manual PUT
curl -X POST http://localhost:8080/trade \
  -H "Content-Type: application/json" \
  -d '{"ativo":"EURUSD","acao":"PUT","valor":10.0,"duracao":5}'
```

## 📱 Interface Web

Acesse `http://localhost:8080` para:

- **Dashboard em tempo real**
- **Gráficos de performance**
- **Histórico de trades**
- **Controle de contas (Real/Simulado)**
- **Configurações do sistema**

## 🔍 Logs

O sistema gera logs detalhados:
- Conexão IQ Option
- Execução de trades
- Mudanças de saldo
- Erros e exceções

## 🚨 Troubleshooting

### Problemas Comuns:

1. **Erro de conexão IQ Option**
   - Verifique credenciais no .env
   - Teste login manual no site

2. **Erro de banco de dados**
   - Verifique DATABASE_URL
   - Use SQLite para testes locais

3. **Porta ocupada**
   - Mude a porta no main.py
   - Ou mate o processo na porta 8080

## 📞 Suporte

Para dúvidas ou problemas:
- Verifique os logs do sistema
- Teste os endpoints individualmente
- Confirme configurações no .env

---

**Versão:** 3.6  
**Última atualização:** 2025-07-19  
**Status:** ✅ Funcionando 