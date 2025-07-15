# Usa uma imagem base oficial do Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o resto do projeto para o diretório de trabalho
COPY . .

# Expõe a porta que o gunicorn vai usar
EXPOSE 8080

# Dá permissão de execução ao script de start
RUN chmod +x ./start.sh

# Comando para iniciar a aplicação quando o container for executado
CMD ["./start.sh"]