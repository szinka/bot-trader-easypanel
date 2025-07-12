# Dockerfile (Versão Final com Git)

# 1. Usa uma imagem base oficial e leve do Python
FROM python:3.11-slim

# 2. Define o diretório de trabalho dentro do container
WORKDIR /app

# 3. Copia a lista de dependências para o container
COPY requirements.txt .

# --- ### A CORREÇÃO ESTÁ AQUI ### ---
# Antes de rodar o pip, primeiro instalamos o 'git' dentro do container.
RUN apt-get update && apt-get install -y git
# --- ### FIM DA CORREÇÃO ### ---

# 5. Agora o pip install vai funcionar, porque o git existe.
RUN python -m pip install -r requirements.txt

# 6. Copia todo o resto do código para o container
COPY . .

# 7. Define o comando que será executado para iniciar o bot
# ATENÇÃO: Verifique se 'bot_auditor.py' é o nome exato do seu script!
CMD ["python", "-u", "bot_auditor.py"]