"""
F1 25 Telemetry System - Configuratie
Centrale configuratie voor database, UDP en logging instellingen
"""

import os
from pathlib import Path

# Project directories
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"

# Maak logs directory aan als die niet bestaat
LOGS_DIR.mkdir(exist_ok=True)

# Database configuratie
DATABASE = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'racesimulator',
    'port': 3306,
    'charset': 'utf8mb4'
}

# UDP Telemetry configuratie
UDP_CONFIG = {
    'host': '127.0.0.1',
    'port': 20777,
    'buffer_size': 2048,
    'timeout': 1.0
}

# Logging configuratie
LOGGING = {
    'log_file': LOGS_DIR / 'telemetry.log',
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'max_bytes': 10 * 1024 * 1024,  # 10 MB
    'backup_count': 5
}

# F1 25 Packet configuratie
F1_25_CONFIG = {
    'packet_format': 2025,
    'game_year': 25,
    'max_cars': 22
}

# Display configuratie
DISPLAY = {
    'refresh_rate': 60,  # Hz
    'screens': 6,
    'default_screen': 1
}

# Data opslag configuratie
DATA_RETENTION = {
    'keep_telemetry_seconds': 300,  # 5 minuten live telemetrie in DB
    'keep_sessions_days': 90,  # Bewaar sessies 90 dagen
}