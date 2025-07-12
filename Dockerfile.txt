# Dockerfile

# 1. Usa uma imagem base oficial e leve do Python
FROM python:3.11-slim

# 2. Define o diretório de trabalho dentro do container
WORKDIR /app

# 3. Copia a lista de dependências para o container
COPY requirements.txt .

# 4. Instala as dependências listadas
RUN python -m pip install -r requirements.txt

# 5. Copia todo o resto do código (seu script .py) para o container
COPY . .

# 6. Define o comando que será executado para iniciar o bot
# ATENÇÃO: Verifique se 'bot_auditor.py' é o nome exato do seu script!
CMD ["python", "-u", "bot_auditor.py"]