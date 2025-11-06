"""
F1 25 Telemetry System - Logger Service
Centraal logging systeem voor alle applicatie events
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from config import LOGGING

class LoggerService:
    """
    Centraal logging service voor de telemetry applicatie
    """
    
    _instance = None
    _loggers = {}
    
    def __new__(cls):
        """Singleton pattern - één logging instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialiseer logging configuratie"""
        if self._initialized:
            return
            
        self._initialized = True
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuratie met file en console handlers"""
        # Root logger configuratie
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, LOGGING['level']))
        
        # Voorkom dubbele handlers
        if root_logger.handlers:
            root_logger.handlers.clear()
        
        # File handler met rotatie
        file_handler = RotatingFileHandler(
            filename=LOGGING['log_file'],
            maxBytes=LOGGING['max_bytes'],
            backupCount=LOGGING['backup_count'],
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(LOGGING['format'])
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # Voeg handlers toe
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        logging.info("=" * 60)
        logging.info("Logging service geïnitialiseerd")
        logging.info(f"Log bestand: {LOGGING['log_file']}")
        logging.info("=" * 60)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Verkrijg een logger voor een specifieke module
        
        Args:
            name: Naam van de module/component
            
        Returns:
            logging.Logger: Configured logger instance
        """
        if name not in self._loggers:
            logger = logging.getLogger(name)
            self._loggers[name] = logger
            logger.info(f"Logger '{name}' aangemaakt")
        
        return self._loggers[name]
    
    def log_packet_received(self, packet_id: int, packet_name: str):
        """Log ontvangst van UDP packet"""
        logger = self.get_logger('UDP')
        logger.debug(f"Packet ontvangen: {packet_name} (ID: {packet_id})")
    
    def log_database_operation(self, operation: str, table: str, success: bool):
        """Log database operatie"""
        logger = self.get_logger('Database')
        level = logging.INFO if success else logging.ERROR
        status = "succesvol" if success else "gefaald"
        logger.log(level, f"{operation} op tabel '{table}' {status}")
    
    def log_error(self, component: str, error: Exception, context: str = ""):
        """Log error met context informatie"""
        logger = self.get_logger(component)
        logger.error(f"Error in {context}: {type(error).__name__}: {str(error)}", exc_info=True)


# Singleton instance
logger_service = LoggerService()