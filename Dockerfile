# Stage 1: Build stage
FROM python:3.11-slim-bullseye as builder

# Sanal ortam için ortam değişkenleri
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Bağımlılıkları kur
WORKDIR /app
COPY requirements.txt .
RUN python3 -m venv $VIRTUAL_ENV && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Final stage
FROM python:3.11-slim-bullseye as final

# Çalışma dizinini ve Python yolunu ayarla
WORKDIR /app
ENV PYTHONPATH /app

# Sanal ortamı builder'dan kopyala
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Uygulama kaynak kodunu kopyala
COPY src/ .

# Güvenlik için root olmayan bir kullanıcı oluştur ve ona geç
RUN useradd --create-home appuser
USER appuser

# Sunucuyu başlat
CMD ["python", "-m", "n8n_mcp.server", "--env"]