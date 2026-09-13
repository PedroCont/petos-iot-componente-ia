# Imagem base leve com Python
FROM python:3.11-slim

# Diretorio de trabalho dentro do container
WORKDIR /app

# Copia so o requirements primeiro (aproveita cache do Docker em rebuilds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante da aplicacao (app.py + modelo .pkl)
COPY . .

# Porta exposta pela API
EXPOSE 8000

# Comando de inicializacao do container
CMD ["python", "app.py"]
