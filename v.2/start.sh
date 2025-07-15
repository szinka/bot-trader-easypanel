#!/bin/bash
# start.sh

echo "Iniciando o servidor Gunicorn..."
# Inicia o servidor Flask usando Gunicorn, que é apropriado para produção
# Ele vai procurar pela variável 'app' dentro do arquivo 'api_server.py' na pasta 'API'
gunicorn --bind 0.0.0.0:8080 --workers 1 "API.api_server:app"