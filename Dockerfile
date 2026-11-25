# Imagen de la app de Streamlit. Los datos no se copian: se montan con compose.yaml.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /srv

# Las dependencias van antes que el código para aprovechar la caché de capas.
COPY requirements-app.txt .
RUN pip install --no-cache-dir -r requirements-app.txt

COPY .streamlit ./.streamlit
COPY app ./app
COPY src ./src

# Ejecutar sin privilegios de administrador.
RUN useradd --create-home --uid 1000 appuser
USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --start-interval=2s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health', timeout=4)"]

CMD ["streamlit", "run", "app/streamlit_app.py", \
     "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
