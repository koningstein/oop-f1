"""
F1 2025 Telemetry Listener - Configuratie
Auto-detecteert development (lokaal) of production (school server)
"""

import socket

# ==================== ENVIRONMENT DETECTION ====================
# Haal hostname op
HOSTNAME = socket.gethostname().lower()

# Development hostnames (voeg jouw PC naam toe!)
DEVELOPMENT_HOSTNAMES = ['desktop', 'laptop', 'localhost', 'student-pc', 'DESKTOP-LLHPV58']

# Check of we in development zijn
IS_DEVELOPMENT = any(name in HOSTNAME for name in DEVELOPMENT_HOSTNAMES)


class Config:
    """Centrale configuratie voor F1 telemetry listener"""
    
    # ==================== DATABASE ====================
    if IS_DEVELOPMENT:
        # LOKAAL (WampServer)
        DB_HOST = 'localhost'
        DB_USER = 'root'
        DB_PASSWORD = ''
        ENVIRONMENT = 'DEVELOPMENT'
    else:
        # PRODUCTIE (School Server)
        DB_HOST = '192.168.1.100'
        DB_USER = 'f1_user'
        DB_PASSWORD = 'SterkWachtwoord123'
        ENVIRONMENT = 'PRODUCTION'
    
    DB_PORT = 3306
    DB_NAME = 'racesimulator'
    
    # ==================== UDP SETTINGS ====================
    UDP_IP = '0.0.0.0'
    UDP_PORT = 20777
    
    # ==================== SIMULATOR INFO ====================
    SIMULATOR_ID = 1
    SIMULATOR_NAME = 'Simulator_1'
    
    # ==================== TRACK NAMES ====================
    TRACK_NAMES = {
        0: "Melbourne", 1: "Paul Ricard", 2: "Shanghai", 3: "Sakhir (Bahrain)",
        4: "Catalunya", 5: "Monaco", 6: "Montreal", 7: "Silverstone",
        8: "Hockenheim", 9: "Hungaroring", 10: "Spa", 11: "Monza",
        12: "Singapore", 13: "Suzuka", 14: "Abu Dhabi", 15: "Texas",
        16: "Brazil", 17: "Austria", 18: "Sochi", 19: "Mexico",
        20: "Baku", 21: "Sakhir Short", 22: "Silverstone Short",
        23: "Texas Short", 24: "Suzuka Short", 25: "Hanoi",
        26: "Zandvoort", 27: "Imola", 28: "Portimao", 29: "Jeddah",
        30: "Miami", 31: "Las Vegas", 32: "Losail"
    }
    
    SESSION_TYPES = {
        0: "Unknown", 1: "Practice 1", 2: "Practice 2", 3: "Practice 3",
        4: "Short Practice", 5: "Q1", 6: "Q2", 7: "Q3",
        8: "Short Qualifying", 9: "OSQ", 10: "Race", 11: "Race 2",
        12: "Race 3", 13: "Time Trial"
    }
    
    # ==================== APPLICATIE SETTINGS ====================
    DEBUG = IS_DEVELOPMENT
    MAX_CACHE_SIZE = 200
    
    @classmethod
    def print_config(cls):
        """Print huidige configuratie"""
        print("\n" + "="*60)
        print("F1 TELEMETRY LISTENER - CONFIGURATIE")
        print("="*60)
        print(f"Environment:      {cls.ENVIRONMENT}")
        print(f"Hostname:         {HOSTNAME}")
        print(f"Simulator:        {cls.SIMULATOR_NAME} (ID: {cls.SIMULATOR_ID})")
        print(f"\nDatabase:")
        print(f"  Host:           {cls.DB_HOST}:{cls.DB_PORT}")
        print(f"  Database:       {cls.DB_NAME}")
        print(f"  User:           {cls.DB_USER}")
        print(f"\nUDP:")
        print(f"  Listening:      {cls.UDP_IP}:{cls.UDP_PORT}")
        print(f"\nDebug Mode:       {cls.DEBUG}")
        print("="*60 + "\n")

# Singleton instance
config = Config()