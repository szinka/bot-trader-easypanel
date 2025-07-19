#!/bin/bash
# start.sh

echo "🚀 Iniciando Bot Trader..."
echo "📊 Verificando configurações..."

# Verifica se as variáveis de ambiente estão configuradas
if [ -z "$IQ_EMAIL" ] || [ -z "$IQ_PASSWORD" ]; then
    echo "❌ Erro: IQ_EMAIL e IQ_PASSWORD devem estar configurados!"
    exit 1
fi

echo "✅ Configurações OK"
echo "🌐 Iniciando servidor na porta 8080..."

# Inicia o servidor Python
python main.py