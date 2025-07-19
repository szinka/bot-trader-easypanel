# Sistema Multi-Conta - Bot Trader

## Problema Resolvido

O sistema original tinha um **problema crítico de contaminação de dados** entre contas REAL e PRACTICE. O gerenciamento de risco era único e global, causando:

- **Valores de entrada incorretos**: Conta Demo em nível avançado afetando operações com dinheiro real
- **Progresso ilusório**: Wins na Demo fazendo o sistema avançar de nível para operações Real
- **Risco financeiro**: Operações com dinheiro real usando parâmetros de conta de prática

## Solução Implementada

### 1. **Isolamento Completo de Estados**

Cada tipo de conta (REAL e PRACTICE) agora possui:
- ✅ **Gerenciador independente** com estado próprio
- ✅ **Histórico separado** de trades
- ✅ **Níveis isolados** com valores de entrada específicos
- ✅ **Sequência de wins/losses** independente

### 2. **Nova Arquitetura**

#### `GerenciadorMultiConta`
```python
# Gerencia múltiplos gerenciadores Torre MK
gerenciador_multi = GerenciadorMultiConta(config)
gerenciador_multi.get_proxima_entrada('REAL', saldo_real)
gerenciador_multi.get_proxima_entrada('PRACTICE', saldo_practice)
```

#### Banco de Dados Atualizado
```sql
-- Tabela estado_gerenciamento com suporte a múltiplas contas
CREATE TABLE estado_gerenciamento (
    id SERIAL PRIMARY KEY,
    tipo_conta VARCHAR(10) NOT NULL UNIQUE,  -- REAL ou PRACTICE
    total_wins INTEGER NOT NULL DEFAULT 0,
    level_entries_json TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tabela trades com identificação de conta
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    tipo_conta VARCHAR(10) NOT NULL,  -- REAL ou PRACTICE
    -- ... outros campos
);
```

### 3. **Novos Endpoints da API**

#### Consultar Estado do Gerenciador
```http
GET /get_estado_gerenciador?tipo_conta=REAL
GET /get_estado_gerenciador?tipo_conta=PRACTICE
```

#### Histórico Filtrado por Conta
```http
GET /get_historico_trades?tipo_conta=REAL
GET /get_historico_trades?tipo_conta=PRACTICE
```

#### Reset Seletivo
```http
POST /resetar_historico
{
    "tipo_conta": "REAL"  // Reseta apenas REAL, ou omitir para resetar tudo
}
```

### 4. **Exemplo de Uso**

#### Operação na Conta Real
```json
POST /trade
{
    "tipo_conta": "REAL",
    "ativo": "EURUSD",
    "acao": "call",
    "duracao": 5,
    "valor_entrada": "gen"  // Usa gerenciamento específico da conta REAL
}
```

#### Operação na Conta Practice
```json
POST /trade
{
    "tipo_conta": "PRACTICE",
    "ativo": "EURUSD", 
    "acao": "put",
    "duracao": 5,
    "valor_entrada": "gen"  // Usa gerenciamento específico da conta PRACTICE
}
```

## Benefícios da Implementação

### ✅ **Segurança Financeira**
- Conta REAL sempre opera com valores apropriados
- Sem contaminação de dados entre contas
- Gerenciamento de risco específico para cada tipo

### ✅ **Flexibilidade**
- Testes na PRACTICE não afetam configurações da REAL
- Cada conta pode ter estratégias diferentes
- Reset independente de cada conta

### ✅ **Transparência**
- Histórico separado por conta
- Estado do gerenciamento visível por conta
- Logs específicos para cada operação

### ✅ **Escalabilidade**
- Fácil adição de novos tipos de conta
- Estrutura preparada para múltiplos usuários
- Migração automática de dados existentes

## Migração de Dados

O sistema inclui um script de migração (`API/migrate_db.py`) que:

1. **Faz backup** dos dados existentes
2. **Recria tabelas** com nova estrutura
3. **Migra dados antigos** para conta PRACTICE
4. **Preserva histórico** completo de operações

## Configuração

### Variáveis de Ambiente
```env
DATABASE_URL=postgresql://user:pass@host:port/db
IQ_EMAIL=seu_email@exemplo.com
IQ_PASSWORD=sua_senha
ENTRY_PERCENTAGE=5.0
WINS_TO_LEVEL_UP=5
LOSS_COMPENSATION=1
```

### Executar Migração
```bash
cd API
python migrate_db.py
```

## Estrutura de Arquivos

```
API/
├── api_server.py          # Servidor principal com novos endpoints
├── gerenciamento.py       # GerenciadorMultiConta + GerenciamentoTorreMK
├── database.py           # Funções DB com suporte multi-conta
├── trader.py             # Classe Trader (inalterada)
├── migrate_db.py         # Script de migração
└── __init__.py
```

## Segurança Implementada

- ✅ **Isolamento completo** entre contas
- ✅ **Validação de tipo de conta** em todas as operações
- ✅ **Logs específicos** para cada conta
- ✅ **Backup automático** durante migração
- ✅ **Rollback** em caso de erro na migração

A implementação garante que **nunca mais** haverá contaminação entre contas REAL e PRACTICE, eliminando completamente os riscos financeiros identificados. 