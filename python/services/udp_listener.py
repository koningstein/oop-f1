"""
F1 25 Telemetry System - UDP Listener
Service voor ontvangen en routeren van UDP telemetry packets
"""

import socket
import threading
from typing import Optional, Callable, Dict
from config import UDP_CONFIG
from services import logger_service
# from packet_parsers import PacketHeader, PacketID, get_packet_name
from packet_parsers.packet_header import PacketHeader
from packet_parsers.packet_types import PacketID, get_packet_name


class UDPListener:
    """
    UDP Listener voor F1 25 telemetry packets
    Ontvangt packets en roept geregistreerde handlers aan
    """
    
    def __init__(self):
        """Initialiseer UDP listener"""
        self.logger = logger_service.get_logger('UDPListener')
        self.host = UDP_CONFIG['host']
        self.port = UDP_CONFIG['port']
        self.buffer_size = UDP_CONFIG['buffer_size']
        
        self.socket: Optional[socket.socket] = None
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # Handlers: {PacketID: callback_function}
        self.handlers: Dict[int, Callable] = {}
        
        # Statistieken
        self.packets_received = 0
        self.packets_processed = 0
        self.packets_errors = 0
        self.last_packet_time = 0
    
    def register_handler(self, packet_id: PacketID, handler: Callable):
        """
        Registreer handler functie voor specifiek packet type
        
        Args:
            packet_id: PacketID enum waarde
            handler: Callback functie die aangeroepen wordt
        """
        self.handlers[packet_id] = handler
        self.logger.info(
            f"Handler geregistreerd voor {get_packet_name(packet_id)} (ID {packet_id})"
        )
    
    def unregister_handler(self, packet_id: PacketID):
        """Verwijder handler voor packet type"""
        if packet_id in self.handlers:
            del self.handlers[packet_id]
            self.logger.info(f"Handler verwijderd voor packet ID {packet_id}")
    
    def start(self):
        """Start UDP listener in aparte thread"""
        if self.running:
            self.logger.warning("UDP listener draait al")
            return
        
        try:
            # Maak UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.settimeout(UDP_CONFIG['timeout'])
            
            self.running = True
            
            # Start listener thread
            self.thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.thread.start()
            
            self.logger.info(f"UDP listener gestart op {self.host}:{self.port}")
            
        except Exception as e:
            self.logger.error(f"Fout bij starten UDP listener: {e}")
            self.running = False
            raise
    
    def stop(self):
        """Stop UDP listener"""
        if not self.running:
            return
        
        self.logger.info("UDP listener wordt gestopt...")
        self.running = False
        
        # Wacht op thread
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        
        # Sluit socket
        if self.socket:
            self.socket.close()
            self.socket = None
        
        self.logger.info(
            f"UDP listener gestopt. "
            f"Ontvangen: {self.packets_received}, "
            f"Verwerkt: {self.packets_processed}, "
            f"Errors: {self.packets_errors}"
        )
    
    def _listen_loop(self):
        """Hoofd listener loop (draait in aparte thread)"""
        self.logger.info("Wachten op telemetry data...")
        
        while self.running:
            try:
                # Ontvang UDP packet
                data, addr = self.socket.recvfrom(self.buffer_size)
                self.packets_received += 1
                
                # Parse header
                header = PacketHeader.from_bytes(data)
                if not header:
                    self.packets_errors += 1
                    self.logger.warning("Ongeldige packet header")
                    continue
                
                # Valideer header
                if not header.is_valid():
                    self.packets_errors += 1
                    self.logger.warning(f"Header validatie gefaald: {header}")
                    continue
                
                # Update stats
                self.last_packet_time = header.session_time
                
                # Roep handler aan als geregistreerd
                if header.packet_id in self.handlers:
                    try:
                        payload = header.get_payload(data)
                        self.handlers[header.packet_id](header, payload)
                        self.packets_processed += 1
                    except Exception as e:
                        self.packets_errors += 1
                        self.logger.error(
                            f"Handler error voor {get_packet_name(header.packet_id)}: {e}"
                        )
                
            except socket.timeout:
                # Timeout is normaal, ga door
                continue
            except Exception as e:
                if self.running:  # Alleen loggen als we nog draaien
                    self.packets_errors += 1
                    self.logger.error(f"Fout in listener loop: {e}")
    
    def get_stats(self) -> dict:
        """
        Verkrijg statistieken van de listener
        
        Returns:
            Dict met statistieken
        """
        return {
            'running': self.running,
            'packets_received': self.packets_received,
            'packets_processed': self.packets_processed,
            'packets_errors': self.packets_errors,
            'last_packet_time': self.last_packet_time,
            'registered_handlers': len(self.handlers)
        }
    
    def is_running(self) -> bool:
        """Check of listener actief is"""
        return self.running