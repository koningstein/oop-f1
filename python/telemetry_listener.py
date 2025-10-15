"""
F1 25 Telemetry - UDP Listener
Hoofdklasse die UDP packets ontvangt en naar de juiste parsers stuurt
"""

import socket
from typing import Dict, Callable, Optional
from packet_header import PacketHeader
from packet_types import PacketID

# Import alle packet parsers
from motion_packets import MotionPacket, MotionExPacket
from session_packets import SessionPacket, EventPacket
from lap_packets import LapDataPacket, LapPositionsPacket
from car_packets import CarTelemetryPacket, CarStatusPacket, CarDamagePacket
from participants_packets import ParticipantsPacket, LobbyInfoPacket
from other_packets import (
    CarSetupsPacket, FinalClassificationPacket, SessionHistoryPacket,
    TyreSetsPacket, TimeTrialPacket
)

class F1TelemetryListener:
    """
    UDP Listener voor F1 25 telemetry
    
    Gebruik:
        listener = F1TelemetryListener(host='127.0.0.1', port=20777)
        listener.register_handler(PacketID.CAR_TELEMETRY, my_handler_function)
        listener.start()
    """
    
    def __init__(self, host: str = '127.0.0.1', port: int = 20777, buffer_size: int = 2048):
        """
        Initialiseer de telemetry listener
        
        Args:
            host: IP adres om naar te luisteren (default: localhost)
            port: UDP poort (default: 20777)
            buffer_size: Buffer grootte voor UDP packets (default: 2048 bytes)
        """
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.sock: Optional[socket.socket] = None
        self.running = False
        
        # Dictionary met packet handlers: {PacketID: handler_function}
        self.packet_handlers: Dict[PacketID, Callable] = {}
        
        # Statistieken
        self.packets_received = 0
        self.packets_processed = 0
        self.packets_errors = 0
        
        # Status tracking voor console output
        self.is_waiting_for_data = False
        self.seen_packet_types = set()
        
        # Parser mapping
        self.parsers = {
            PacketID.MOTION: MotionPacket,
            PacketID.SESSION: SessionPacket,
            PacketID.LAP_DATA: LapDataPacket,
            PacketID.EVENT: EventPacket,
            PacketID.PARTICIPANTS: ParticipantsPacket,
            PacketID.CAR_SETUPS: CarSetupsPacket,
            PacketID.CAR_TELEMETRY: CarTelemetryPacket,
            PacketID.CAR_STATUS: CarStatusPacket,
            PacketID.FINAL_CLASSIFICATION: FinalClassificationPacket,
            PacketID.LOBBY_INFO: LobbyInfoPacket,
            PacketID.CAR_DAMAGE: CarDamagePacket,
            PacketID.SESSION_HISTORY: SessionHistoryPacket,
            PacketID.TYRE_SETS: TyreSetsPacket,
            PacketID.MOTION_EX: MotionExPacket,
            PacketID.TIME_TRIAL: TimeTrialPacket,
            PacketID.LAP_POSITIONS: LapPositionsPacket,
        }
    
    def register_handler(self, packet_id: PacketID, handler: Callable):
        """
        Registreer een handler functie voor een specifiek packet type
        
        Args:
            packet_id: Type packet (bijv. PacketID.CAR_TELEMETRY)
            handler: Functie die wordt aangeroepen met parsed packet als argument
            
        Example:
            def my_handler(packet: CarTelemetryPacket):
                print(packet.get_player_telemetry().speed)
            
            listener.register_handler(PacketID.CAR_TELEMETRY, my_handler)
        """
        self.packet_handlers[packet_id] = handler
        print(f"✓ Handler geregistreerd voor {packet_id.name}")
    
    def unregister_handler(self, packet_id: PacketID):
        """
        Verwijder een handler voor een packet type
        
        Args:
            packet_id: Type packet om te verwijderen
        """
        if packet_id in self.packet_handlers:
            del self.packet_handlers[packet_id]
            print(f"✓ Handler verwijderd voor {packet_id.name}")
    
    def register_all_handlers(self, handler: Callable):
        """
        Registreer dezelfde handler voor ALLE packet types
        Handig voor logging of opslaan van alle data
        
        Args:
            handler: Functie die wordt aangeroepen voor elk packet
        """
        for packet_id in PacketID:
            if packet_id != PacketID.ePacketIdMax:  # Skip max enum value
                self.register_handler(packet_id, handler)
    
    def start(self):
        """
        Start de UDP listener
        Blijft draaien tot KeyboardInterrupt (Ctrl+C)
        """
        if self.running:
            print("⚠ Listener draait al!")
            return
        
        try:
            # Maak UDP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((self.host, self.port))
            self.running = True
            
            print("=" * 60)
            print(f"🏎️  F1 25 Telemetry Listener")
            print("=" * 60)
            print(f"Luisteren op {self.host}:{self.port}")
            print(f"Geregistreerde handlers: {len(self.packet_handlers)}")
            for packet_id in self.packet_handlers.keys():
                print(f"  • {packet_id.name}")
            print()
            print("Druk op Ctrl+C om te stoppen...")
            print("=" * 60)
            print()
            
            # Main loop
            while self.running:
                try:
                    data, addr = self.sock.recvfrom(self.buffer_size)
                    self.packets_received += 1
                    self._process_packet(data)
                    
                except Exception as e:
                    self.packets_errors += 1
                    print(f"❌ Fout bij ontvangen packet: {e}")
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Stoppen...")
            self._print_statistics()
        
        except Exception as e:
            print(f"\n❌ Fatale fout: {e}")
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop de listener en sluit de socket"""
        self.running = False
        if self.sock:
            self.sock.close()
            self.sock = None
        print("✓ Listener gestopt")
    
    def _process_packet(self, data: bytes):
        """
        Verwerk een ontvangen UDP packet
        
        Args:
            data: Ruwe bytes van UDP packet
        """
        # Minimale packet grootte check
        if len(data) < 29:
            self.packets_errors += 1
            return
        
        try:
            # Parse header
            header = PacketHeader.from_bytes(data)
            
            # Valideer packet format
            if not header.is_valid():
                self.packets_errors += 1
                print(f"⚠ Verkeerd packet format: {header.packet_format} (verwacht 2025)")
                return
            
            # Check of we een handler hebben voor dit packet type
            packet_id = PacketID(header.packet_id)
            
            if packet_id not in self.packet_handlers:
                # Geen handler geregistreerd, skip
                return
            
            # Parse het packet
            packet = self._parse_packet(header, data)
            
            if packet is None:
                self.packets_errors += 1
                return
            
            # Roep handler aan
            try:
                self.packet_handlers[packet_id](packet)
                self.packets_processed += 1
            except Exception as e:
                self.packets_errors += 1
                print(f"❌ Fout in handler voor {packet_id.name}: {e}")
        
        except Exception as e:
            self.packets_errors += 1
            print(f"❌ Fout bij verwerken packet: {e}")
    
    def _parse_packet(self, header: PacketHeader, data: bytes):
        """
        Parse packet naar juiste klasse op basis van header
        
        Args:
            header: Geparsete PacketHeader
            data: Ruwe packet bytes
            
        Returns:
            Geparsed packet object of None bij fout
        """
        try:
            packet_id = PacketID(header.packet_id)
            
            # Zoek juiste parser
            if packet_id in self.parsers:
                parser_class = self.parsers[packet_id]
                return parser_class(header, data)
            else:
                print(f"⚠ Geen parser voor packet type: {packet_id.name}")
                return None
        
        except Exception as e:
            print(f"❌ Parse fout voor {header.get_packet_type_name()}: {e}")
            return None
    
    def _print_statistics(self):
        """Print statistieken over ontvangen packets"""
        print("\n" + "=" * 60)
        print("📊 Statistieken")
        print("=" * 60)
        print(f"Ontvangen packets:  {self.packets_received}")
        print(f"Verwerkte packets:  {self.packets_processed}")
        print(f"Fouten:             {self.packets_errors}")
        
        if self.packets_received > 0:
            success_rate = (self.packets_processed / self.packets_received) * 100
            print(f"Succes rate:        {success_rate:.1f}%")
        print("=" * 60)
    
    def get_statistics(self) -> dict:
        """
        Krijg statistieken als dictionary
        
        Returns:
            Dict met packets_received, packets_processed, packets_errors
        """
        return {
            'packets_received': self.packets_received,
            'packets_processed': self.packets_processed,
            'packets_errors': self.packets_errors,
            'success_rate': (self.packets_processed / self.packets_received * 100) 
                           if self.packets_received > 0 else 0
        }
    
    def reset_statistics(self):
        """Reset alle statistieken naar 0"""
        self.packets_received = 0
        self.packets_processed = 0
        self.packets_errors = 0
        print("✓ Statistieken gereset")


# ===== HELPER FUNCTIES =====

def create_simple_listener(handlers: Dict[PacketID, Callable], 
                          host: str = '127.0.0.1', 
                          port: int = 20777) -> F1TelemetryListener:
    """
    Helper functie om snel een listener te maken met handlers
    
    Args:
        handlers: Dictionary met {PacketID: handler_function}
        host: IP adres (default: localhost)
        port: UDP poort (default: 20777)
        
    Returns:
        Geconfigureerde F1TelemetryListener
        
    Example:
        listener = create_simple_listener({
            PacketID.CAR_TELEMETRY: handle_telemetry,
            PacketID.LAP_DATA: handle_lap_data
        })
        listener.start()
    """
    listener = F1TelemetryListener(host, port)
    
    for packet_id, handler in handlers.items():
        listener.register_handler(packet_id, handler)
    
    return listener