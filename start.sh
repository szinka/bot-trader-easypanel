#!/bin/sh
# Inicia o Gunicorn a partir da raiz do projeto, especificando o caminho completo para o app.
gunicorn -w 2 "API.api_server:app" -b 0.0.0.0:8080