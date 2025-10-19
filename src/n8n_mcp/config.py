"""
Konfigürasyon Yönetimi

Uygulama ayarlarını güvenli bir şekilde yönetmek için konfigürasyon sınıfları.
"""

import os
import json
from typing import Optional, Dict, Any
from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class N8nConfig(BaseModel):
    """n8n API konfigürasyonu"""
    base_url: str = Field(..., description="n8n instance base URL")
    api_key: str = Field(..., description="n8n API key")
    timeout: int = Field(30, description="Request timeout in seconds")
    max_retries: int = Field(3, description="Maximum retry attempts")


class McpConfig(BaseModel):
    """MCP sunucu konfigürasyonu"""
    server_name: str = Field("n8n-workflow-manager", description="MCP server name")
    version: str = Field("1.0.0", description="Server version")
    description: str = Field("MCP server for managing n8n workflows", description="Server description")
    port: int = Field(8080, description="Server port")


class LoggingConfig(BaseModel):
    """Logging konfigürasyonu"""
    level: str = Field("INFO", description="Log level")
    format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
        description="Log format"
    )
    file: Optional[str] = Field(None, description="Log file path")
    max_bytes: int = Field(10485760, description="Max log file size in bytes (10MB)")
    backup_count: int = Field(5, description="Number of backup files to keep")


class SecurityConfig(BaseModel):
    """Güvenlik konfigürasyonu"""
    enable_authentication: bool = Field(True, description="Enable authentication")
    rate_limiting: Dict[str, Any] = Field(
        default_factory=lambda: {
            "enabled": True,
            "requests_per_minute": 100
        },
        description="Rate limiting settings"
    )


class PerformanceConfig(BaseModel):
    """Performans konfigürasyonu"""
    cache_ttl: int = Field(300, description="Cache TTL in seconds")
    max_concurrent_requests: int = Field(10, description="Max concurrent requests")
    response_timeout: int = Field(2, description="Response timeout target in seconds")


class Settings(BaseSettings):
    """Ana konfigürasyon sınıfı"""
    
    # Alt konfigürasyonlar
    n8n: N8nConfig
    mcp: McpConfig = Field(default_factory=McpConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    
    model_config = {
        "env_file": ".env",
        "env_nested_delimiter": "__",
        "case_sensitive": False,
        "extra": "ignore"  # Extra alanları yoksay
    }
    
    @classmethod
    def load_from_file(cls, config_path: Optional[str] = None) -> "Settings":
        """Konfigürasyon dosyasından ayarları yükle"""
        if config_path is None:
            # Varsayılan konfigürasyon dosyası yolları
            possible_paths = [
                "config/config.json",
                "config.json",
                os.path.expanduser("~/.n8n-mcp/config.json"),
                "/etc/n8n-mcp/config.json"
            ]
            
            config_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break
            
            if config_path is None:
                raise FileNotFoundError(
                    f"Config file not found in any of these locations: {possible_paths}"
                )
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        return cls(**config_data)
    
    @classmethod
    def load_from_env(cls) -> "Settings":
        """Ortam değişkenlerinden ayarları yükle"""
        
        # .env dosyasından değişkenleri yükle
        from dotenv import load_dotenv
        load_dotenv()
        
        # Gerekli ortam değişkenlerini kontrol et
        n8n_base_url = os.getenv("N8N_BASE_URL", "").strip()
        n8n_api_key = os.getenv("N8N_API_KEY", "").strip()
        
        if not n8n_base_url:
            raise ValueError("N8N_BASE_URL environment variable is required")
        
        if not n8n_api_key:
            raise ValueError("N8N_API_KEY environment variable is required")
        
        config_data = {
            "n8n": {
                "base_url": n8n_base_url,
                "api_key": n8n_api_key,
                "timeout": int(os.getenv("N8N_TIMEOUT", "30")),
                "max_retries": int(os.getenv("N8N_MAX_RETRIES", "3"))
            }
        }
        
        # MCP ayarları
        if os.getenv("MCP_SERVER_NAME"):
            config_data["mcp"] = {
                "server_name": os.getenv("MCP_SERVER_NAME"),
                "version": os.getenv("MCP_VERSION", "1.0.0"),
                "description": os.getenv("MCP_DESCRIPTION", "MCP server for managing n8n workflows"),
                "port": int(os.getenv("MCP_PORT", "8080"))
            }
        
        # Logging ayarları
        if os.getenv("LOG_LEVEL"):
            config_data["logging"] = {
                "level": os.getenv("LOG_LEVEL"),
                "format": os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
                "file": os.getenv("LOG_FILE"),
                "max_bytes": int(os.getenv("LOG_MAX_BYTES", "10485760")),
                "backup_count": int(os.getenv("LOG_BACKUP_COUNT", "5"))
            }
        
        return cls(**config_data)
    
    def save_to_file(self, config_path: str):
        """Konfigürasyonu dosyaya kaydet"""
        # Konfigürasyon dizinini oluştur
        config_dir = os.path.dirname(config_path)
        if config_dir:
            os.makedirs(config_dir, exist_ok=True)
        
        # Konfigürasyonu JSON olarak kaydet
        config_dict = self.model_dump()
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
    
    def validate_n8n_connection(self) -> bool:
        """n8n konfigürasyonunun geçerli olup olmadığını kontrol et"""
        try:
            # Basit URL ve API key kontrolü
            if not self.n8n.base_url or not self.n8n.base_url.startswith('http'):
                return False
            
            if not self.n8n.api_key or len(self.n8n.api_key) < 10:
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_log_file_path(self) -> Optional[str]:
        """Log dosya yolunu al"""
        if self.logging.file:
            # Relatif yolları mutlak yola çevir
            if not os.path.isabs(self.logging.file):
                return os.path.abspath(self.logging.file)
            return self.logging.file
        return None


def load_settings(config_path: Optional[str] = None, use_env: bool = False) -> Settings:
    """
    Konfigürasyonu yükle
    
    Args:
        config_path: Konfigürasyon dosya yolu
        use_env: Ortam değişkenlerini kullan
    
    Returns:
        Settings: Yüklenmiş konfigürasyon
    """
    if use_env:
        return Settings.load_from_env()
    else:
        return Settings.load_from_file(config_path)


def create_example_config(output_path: str = "config/config.example.json"):
    """Örnek konfigürasyon dosyası oluştur"""
    example_config = {
        "n8n": {
            "base_url": "https://yaskagroup1.app.n8n.cloud",
            "api_key": "YOUR_N8N_API_KEY_HERE",
            "timeout": 30,
            "max_retries": 3
        },
        "mcp": {
            "server_name": "n8n-workflow-manager",
            "version": "1.0.0",
            "description": "MCP server for managing n8n workflows",
            "port": 8080
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": "logs/n8n_mcp_server.log",
            "max_bytes": 10485760,
            "backup_count": 5
        },
        "security": {
            "enable_authentication": True,
            "rate_limiting": {
                "enabled": True,
                "requests_per_minute": 100
            }
        },
        "performance": {
            "cache_ttl": 300,
            "max_concurrent_requests": 10,
            "response_timeout": 2
        }
    }
    
    # Dizin oluştur
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Dosyayı kaydet
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(example_config, f, indent=2, ensure_ascii=False)
    
    print(f"Example config created at: {output_path}")


if __name__ == "__main__":
    # Test ve örnek konfigürasyon oluşturma
    create_example_config()