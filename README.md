# 🤖 Bot Trader - Sistema de Trading Automatizado

Sistema completo de trading automatizado com interface web, gerenciamento de risco e suporte a contas REAL e SIMULADO.

## 🚀 Características Principais

- **🤖 Trading Automatizado** com gerenciamento de risco "Torre MK"
- **🌐 Interface Web** moderna e responsiva
- **💰 Multi-Conta** suporte a REAL e SIMULADO
- **📊 Dashboard** com gráficos e métricas em tempo real
- **⚙️ Configurável** via variáveis de ambiente
- **🐳 Docker** pronto para deploy

## 📋 Pré-requisitos

- Python 3.8+
- PostgreSQL (ou SQLite para desenvolvimento)
- Conta IQ Option

## 🛠️ Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/bot-trader.git
cd bot-trader
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite com suas credenciais
nano .env
```

### 4. Configure o banco de dados
```bash
# Para PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/bot_trader

# Para SQLite (desenvolvimento)
DATABASE_URL=sqlite:///bot_trader.db
```

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# Credenciais IQ Option
IQ_EMAIL=seu-email@exemplo.com
IQ_PASSWORD=sua-senha

# Banco de Dados
DATABASE_URL=postgresql://user:password@localhost/bot_trader

# Configurações de Gerenciamento
GERENCIAMENTO_PERCENT=5.0
ENTRY_PERCENTAGE=5.0
WINS_TO_LEVEL_UP=5
LOSS_COMPENSATION=1
```

## 🚀 Como Usar

### 1. Inicie o servidor
```bash
python API/api_server.py
```

### 2. Acesse a interface
```
http://localhost:8080
```

### 3. Use a interface web
- **Seletor de Conta**: Alterna entre REAL e SIMULADO
- **Dashboard**: Visualiza saldos, performance e win rate
- **Gráficos**: Acompanha evolução do saldo
- **Histórico**: Consulta trades anteriores

## 📊 Funcionalidades

### Interface Web
- ✅ **Dashboard Responsivo** com métricas em tempo real
- ✅ **Seletor de Conta** (REAL/SIMULADO)
- ✅ **Gráficos Interativos** de performance
- ✅ **Histórico Completo** de trades
- ✅ **Win Rate** calculado automaticamente

### Sistema de Trading
- ✅ **Gerenciamento Torre MK** com entradas progressivas
- ✅ **Validação de Saldo** antes de trades
- ✅ **Resposta Instantânea** sem esperar resultado
- ✅ **Multi-Conta** isolamento entre REAL e SIMULADO
- ✅ **Configuração Flexível** via environment variables

### API REST
- `GET /` - Interface web
- `GET /ping` - Status do sistema
- `GET /get_saldos` - Saldos das contas
- `POST /trade` - Executar trade
- `GET /get_historico_trades` - Histórico de trades
- `GET /get_estado_gerenciador` - Estado do gerenciamento
- `POST /resetar_historico` - Resetar histórico

## 🐳 Docker

### Build da imagem
```bash
docker build -t bot-trader .
```

### Executar com Docker Compose
```bash
docker-compose up -d
```

### Variáveis de ambiente no Docker
```yaml
environment:
  - IQ_EMAIL=${IQ_EMAIL}
  - IQ_PASSWORD=${IQ_PASSWORD}
  - DATABASE_URL=${DATABASE_URL}
  - GERENCIAMENTO_PERCENT=5.0
```

## 📈 Sistema de Gerenciamento

### Torre MK
- **Entradas Progressivas**: Valor aumenta conforme nível
- **Win/Loss Tracking**: Conta vitórias e derrotas
- **Level Management**: Sobe nível após 5 wins
- **Compensation**: Ajusta após perdas

### Configurações
- `GERENCIAMENTO_PERCENT`: 5.0% (padrão)
- `ENTRY_PERCENTAGE`: 5.0% (padrão)
- `WINS_TO_LEVEL_UP`: 5 wins para subir nível
- `LOSS_COMPENSATION`: 1 perda para compensar

## 🔧 Estrutura do Projeto

```
bot-trader/
├── API/
│   ├── api_server.py      # Servidor Flask principal
│   ├── trader.py          # Integração IQ Option
│   ├── gerenciamento.py   # Sistema Torre MK
│   ├── database.py        # Operações de banco
│   └── __init__.py
├── templates/
│   └── interface.html     # Interface web
├── docker-compose.yml     # Configuração Docker
├── Dockerfile            # Imagem Docker
├── requirements.txt      # Dependências Python
├── start.sh             # Script de inicialização
└── README.md           # Este arquivo
```

## 🚨 Segurança

- ✅ **Validação de Saldo** antes de trades
- ✅ **Limite de 5%** da banca para trades manuais
- ✅ **Isolamento de Contas** REAL/SIMULADO
- ✅ **Logs Detalhados** para auditoria
- ✅ **Tratamento de Erros** robusto

## 📝 Logs

O sistema gera logs detalhados:
- **INFO**: Operações normais
- **WARNING**: Avisos importantes
- **ERROR**: Erros tratáveis
- **CRITICAL**: Erros críticos

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 🆘 Suporte

Para suporte ou dúvidas:
1. Verifique os logs do servidor
2. Confirme as configurações de ambiente
3. Teste a conectividade com IQ Option
4. Abra uma issue no GitHub

---

**⚠️ Aviso**: Trading envolve riscos. Use apenas com dinheiro que pode perder. 