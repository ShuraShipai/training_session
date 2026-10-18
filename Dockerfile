FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends flac libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /code
COPY requirements.txt .
# CPU-only wheels avoid pulling CUDA packages into a CPU Space.
RUN pip install --no-cache-dir torch==2.8.0 torchvision==0.23.0 --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt
RUN useradd --create-home --uid 1000 appuser && mkdir -p /opt/u2net && chown appuser /opt/u2net
ENV U2NET_HOME=/opt/u2net PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 YOLO_CONFIG_DIR=/tmp/ultralytics
USER appuser
# Download the unchanged default rembg model at build time, not per visitor.
RUN python -c "from rembg import new_session; new_session()"
COPY --chown=appuser:appuser app ./app
COPY --chown=appuser:appuser projects/rock-paper-scissors/best.pt ./projects/rock-paper-scissors/best.pt
COPY --chown=appuser:appuser .streamlit ./.streamlit
EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/_stcore/health', timeout=3)"
CMD ["streamlit", "run", "app/main.py", "--server.address=0.0.0.0", "--server.port=7860"]
