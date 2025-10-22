FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de la aplicación
COPY br.py .

# Instalar dependencias de Python
RUN pip install --no-cache-dir \
    shiny \
    pandas \
    shinywidgets \
    ipyleaflet \
    ipywidgets \
    requests \
    faicons \
    plotly \
    python-dotenv

# Exponer el puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["python", "-m", "shiny", "run", "br.py", "--host", "0.0.0.0", "--port", "8000"]