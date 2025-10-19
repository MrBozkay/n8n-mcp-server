"""
Logging Configuration

Structured logging kurulumu ve konfigürasyonu.
"""

import os
import sys
import logging
import logging.handlers
from typing import Optional
import structlog
from pathlib import Path

from .config import LoggingConfig


def setup_logging(config: LoggingConfig):
    """
    Structured logging'i ayarla
    
    Args:
        config: Logging konfigürasyonu
    """
    # Log level'ı ayarla
    log_level = getattr(logging, config.level.upper(), logging.INFO)
    
    # Root logger'ı konfigüre et
    logging.basicConfig(
        level=log_level,
        format=config.format,
        handlers=[]  # Handlers'ları manuel ekleyeceğiz
    )
    
    # Handlers'ları oluştur
    handlers = []
    
    # Console handler (her zaman ekle)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(config.format)
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)
    
    # File handler (eğer belirtilmişse)
    if config.file:
        log_file_path = Path(config.file)
        
        # Log dizinini oluştur
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Rotating file handler kullan
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file_path,
            maxBytes=config.max_bytes,
            backupCount=config.backup_count,
            encoding='utf-8'
        )
        
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(config.format)
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)
    
    # Root logger'a handlers'ları ekle
    root_logger = logging.getLogger()
    root_logger.handlers.clear()  # Mevcut handlers'ları temizle
    
    for handler in handlers:
        root_logger.addHandler(handler)
    
    # Structlog'u konfigüre et
    structlog.configure(
        processors=[
            # Built-in processors
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            
            # JSON formatter for structured logging
            structlog.processors.JSONRenderer() if config.file else structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # n8n-mcp specific logger
    logger = structlog.get_logger("n8n_mcp")
    logger.info(
        "Logging configured",
        level=config.level,
        file=config.file,
        max_bytes=config.max_bytes,
        backup_count=config.backup_count
    )


def get_logger(name: str = __name__):
    """
    Logger instance'ı al
    
    Args:
        name: Logger adı
    
    Returns:
        Structlog logger instance
    """
    return structlog.get_logger(name)