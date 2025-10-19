# Stage 1: Build stage
FROM python:3.11-slim-bullseye as builder

# Çalışma dizinini ayarla
WORKDIR /app

# Sanal ortam oluştur
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Sadece üretim bağımlılıklarını kur
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Final stage
FROM python:3.11-slim-bullseye as final

WORKDIR /app

# Sanal ortamı ve kaynak kodunu builder'dan kopyala
COPY --from=builder /opt/venv /opt/venv
COPY src/ ./src/

# Ortam değişkenlerini ayarla ve sunucuyu başlatmak için CMD komutunu tanımla
ENV PATH="/opt/venv/bin:$PATH"
CMD ["python", "-m", "src.n8n_mcp.server", "--env"]