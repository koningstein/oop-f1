"""
F1 25 Telemetry System - UDP Listener Service
Luistert naar UDP pakketten van F1 25
"""

import socket
import threading
from typing import Callable, Dict, Any, Optional
from services import logger_service
# Importeer de CONFIG dictionary uit config.py
try:
    from config import UDP_CONFIG
except ImportError:
    # Fallback als config.py niet gevonden kan worden
    print("[FATAL ERROR] config.py niet gevonden of UDP_CONFIG mist.")
    # Standaardwaarden om crashen te voorkomen (maar zal wss niet werken)
    UDP_CONFIG = {'host': '0.0.0.0', 'port': 20777, 'buffer_size': 2048, 'timeout': 1.0}


class UDPListener:
    """Luistert naar UDP pakketten op een aparte thread"""
    
    def __init__(self, packet_handler: Callable[[bytes], None]):
        """
        Initialiseer UDP listener
        
        Args:
            packet_handler: Een callback functie die de rauwe bytes
                            van een pakket als argument accepteert.
        """
        self.logger = logger_service.get_logger('UDPListener')
        
        # Gebruik de UDP_CONFIG dictionary
        self.host = UDP_CONFIG.get('host', '0.0.0.0')
        self.port = UDP_CONFIG.get('port', 20777)
        self.buffer_size = UDP_CONFIG.get('buffer_size', 2048)
        self.timeout = UDP_CONFIG.get('timeout', 1.0)
        
        self.sock: Optional[socket.socket] = None
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # De handler die de rauwe data gaat verwerken
        self.packet_handler = packet_handler 
        
        # Stats
        self.packets_received = 0
        self.packets_processed = 0
        self.packets_errors = 0

    def start(self):
        """Start de listener thread"""
        if self.running:
            self.logger.warning("UDP listener is al gestart")
            return
        
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # SO_REUSEADDR is goed gebruik in je originele bestand
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.sock.settimeout(self.timeout)  # Gebruik timeout uit config
            self.logger.info(f"UDP listener gestart op {self.host}:{self.port}")
        except OSError as e:
            self.logger.error(f"Kon socket niet binden op {self.host}:{self.port}: {e}")
            self.running = False
            # Gooi de exceptie opnieuw op zodat F1TelemetryApp deze kan vangen
            raise 
        
        self.running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop de listener thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
            self.logger.info("UDP listener thread gestopt")
        
        if self.sock:
            self.sock.close()
            self.sock = None
            self.logger.info("Socket gesloten")

    def run(self):
        """Hoofd loop voor de listener thread"""
        while self.running:
            try:
                # Wacht op data
                data, addr = self.sock.recvfrom(self.buffer_size)
                self.packets_received += 1
                
                if data:
                    # Stuur rauwe data naar de packet handler (DataProcessor)
                    self.packet_handler(data)
                    self.packets_processed += 1
                    
            except socket.timeout:
                # Geen data ontvangen, check of we nog moeten runnen
                continue
            except Exception as e:
                if self.running:
                    self.logger.error(f"Fout in listener loop: {e}", exc_info=True)
                    self.packets_errors += 1
        
        self.logger.info("UDP listener run loop gestopt")

    def is_running(self) -> bool:
        """Check of de listener actief is"""
        return self.running

    def get_stats(self) -> Dict[str, Any]:
        """Verkrijg statistieken"""
        return {
            "running": self.running,
            "packets_received": self.packets_received,
            "packets_processed": self.packets_processed,
            "packets_errors": self.packets_errors,
        }