# Usa uma imagem base oficial do Python
FROM python:3.11-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de dependências
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Cria diretório para logs
RUN mkdir -p /app/logs

# Expõe a porta
EXPOSE 8080

# Comando para iniciar a aplicação
CMD ["python", "-m", "API.api_server"]