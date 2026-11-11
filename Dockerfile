FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd --uid 10001 --create-home appuser
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=appuser:appuser . .
USER appuser
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=10s --start-period=45s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health',timeout=5)"
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
