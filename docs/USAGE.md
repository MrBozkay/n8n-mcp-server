# n8n MCP Server Kullanım Kılavuzu

## 📋 İçindekiler
- [Kurulum](#kurulum)
- [Konfigürasyon](#konfigürasyon)
- [Sunucuyu Başlatma](#sunucuyu-başlatma)
- [MCP Tools](#mcp-tools)
- [Örnekler](#örnekler)
- [Sorun Giderme](#sorun-giderme)

## 🚀 Kurulum

### 1. Gereksinimler
- Python 3.8 veya üzeri
- n8n Cloud instance erişimi
- n8n API Key

### 2. Bağımlılıkları Yükleme
```bash
cd n8n-mcp-server
pip install -r requirements.txt
```

### 3. n8n API Key Alma
1. n8n Cloud hesabınıza giriş yapın
2. Settings > Personal API tokens sayfasına gidin
3. Yeni bir API token oluşturun
4. Token'ı güvenli bir yerde saklayın

## ⚙️ Konfigürasyon

### Yöntem 1: Konfigürasyon Dosyası ile

1. **Konfigürasyon dosyasını kopyalayın:**
```bash
cp config/config.example.json config/config.json
```

2. **API key'inizi ekleyin:**
```json
{
  "n8n": {
    "base_url": "https://yaskagroup1.app.n8n.cloud",
    "api_key": "YOUR_ACTUAL_N8N_API_KEY_HERE",
    "timeout": 30,
    "max_retries": 3
  }
}
```

### Yöntem 2: Environment Variables ile

1. **Environment dosyasını oluşturun:**
```bash
cp .env.example .env
```

2. **API key'inizi ekleyin:**
```bash
N8N_BASE_URL=https://yaskagroup1.app.n8n.cloud
N8N_API_KEY=YOUR_ACTUAL_N8N_API_KEY_HERE
```

## 🏃 Sunucuyu Başlatma

### Konfigürasyon Dosyası ile:
```bash
python -m src.n8n_mcp.server config/config.json
```

### Environment Variables ile:
```bash
python -m src.n8n_mcp.server --env
```

### Başarılı Başlatma:
```
2024-10-04 15:30:00 - n8n_mcp - INFO - Starting n8n MCP Server version=1.0.0
2024-10-04 15:30:01 - n8n_mcp - INFO - n8n API connection verified
2024-10-04 15:30:01 - n8n_mcp - INFO - n8n MCP Server started and ready for connections
```

## 🛠 MCP Tools

Sunucu aşağıdaki MCP tool'ları sağlar:

### 1. create_workflow
Yeni bir n8n workflow oluşturur.

**Parametreler:**
- `name` (zorunlu): Workflow adı
- `nodes` (opsiyonel): Node konfigürasyonu
- `connections` (opsiyonel): Bağlantı konfigürasyonu
- `active` (opsiyonel): Aktif durumu (varsayılan: false)
- `tags` (opsiyonel): Etiketler

### 2. get_workflow
Belirli bir workflow'u ID ile getirir.

**Parametreler:**
- `workflow_id` (zorunlu): Workflow ID'si
- `use_cache` (opsiyonel): Cache kullanımı (varsayılan: true)

### 3. list_workflows
Workflow'ları listeler.

**Parametreler:**
- `active` (opsiyonel): Aktif durum filtresi
- `tags` (opsiyonel): Etiket filtresi
- `limit` (opsiyonel): Maksimum sonuç sayısı (varsayılan: 20)
- `offset` (opsiyonel): Atlama sayısı (varsayılan: 0)

### 4. search_workflows
Workflow'ları ada veya etikete göre arar.

**Parametreler:**
- `query` (zorunlu): Arama sorgusu
- `limit` (opsiyonel): Maksimum sonuç sayısı (varsayılan: 20)

### 5. health_check
n8n API bağlantısını kontrol eder.

**Parametreler:** Yok

## 📚 Örnekler

### Claude ile Kullanım

1. **Sunucuyu başlatın**
2. **Claude'e MCP server'ı tanıtın**
3. **Workflow yönetim komutlarını kullanın:**

```
Create a simple workflow named "Daily Report" with a webhook trigger
```

```
List all active workflows
```

```
Search for workflows containing "email"
```

```
Check if the n8n API connection is working
```

### Python Script ile Test

```python
import asyncio
import json
from src.n8n_mcp.client import N8nApiClient, WorkflowModel

async def test_connection():
    client = N8nApiClient(
        base_url="https://yaskagroup1.app.n8n.cloud",
        api_key="YOUR_API_KEY"
    )
    
    # Health check
    is_healthy = await client.health_check()
    print(f"API Health: {is_healthy}")
    
    # List workflows
    workflows = await client.list_workflows(limit=5)
    print(f"Found {len(workflows)} workflows")
    
    await client.close()

# Çalıştır
asyncio.run(test_connection())
```

## 🔧 Sorun Giderme

### Yaygın Hatalar

#### 1. "Configuration error: N8N_API_KEY environment variable is required"
**Çözüm:** API key'inizi doğru şekilde ayarlayın:
```bash
export N8N_API_KEY="your_actual_api_key_here"
```

#### 2. "n8n API health check failed"
**Kontroller:**
- API key'in geçerli olduğunu doğrulayın
- n8n instance URL'inin doğru olduğunu kontrol edin
- İnternet bağlantınızı kontrol edin

#### 3. "Invalid n8n configuration"
**Çözüm:** Konfigürasyon dosyanızı kontrol edin:
- `base_url` "http" veya "https" ile başlamalı
- `api_key` en az 10 karakter olmalı

### Log Dosyalarını İnceleme

Log dosyası varsayılan olarak `logs/n8n_mcp_server.log` konumundadır:

```bash
tail -f logs/n8n_mcp_server.log
```

### Debug Mode

Debug seviyesinde log için konfigürasyonu güncelleyin:
```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

## 📈 Performans İpuçları

### 1. Cache Kullanımı
- GET istekleri için cache aktif (varsayılan 5 dakika)
- Sık kullanılan workflow'lar için cache TTL'yi artırın

### 2. Rate Limiting
- Varsayılan: 100 istek/dakika
- Gerektiğinde ayarlayın: `security.rate_limiting.requests_per_minute`

### 3. Timeout Ayarları
- API timeout: 30 saniye (varsayılan)
- Yavaş bağlantılar için artırın

## 🔒 Güvenlik

### API Key Güvenliği
- API key'leri asla koda hard-code etmeyin
- Environment variables veya güvenli konfigürasyon kullanın
- API key'leri düzenli olarak yenileyin

### Network Güvenliği
- HTTPS kullanımını zorunlu tutun
- Firewall kurallarını uygun şekilde ayarlayın

## 🆘 Destek

### Loglama Seviyeleri
- `ERROR`: Kritik hatalar
- `WARNING`: Uyarılar
- `INFO`: Genel bilgiler (varsayılan)
- `DEBUG`: Detaylı debug bilgileri

### GitHub Issues
Sorun bildirimi ve özellik istekleri için GitHub repository'sini kullanın.

### İletişim
Acil durumlar için proje yöneticisi ile iletişime geçin.