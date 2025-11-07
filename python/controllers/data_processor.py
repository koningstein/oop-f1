"""
F1 25 Telemetry System - Data Processor
Verwerkt rauwe UDP pakketten en stuurt data naar de juiste controllers.
"""
import struct
from services import logger_service
from controllers.telemetry_controller import TelemetryController

# --- GECORRIGEERDE IMPORTS ---
# Gebaseerd op je 'oud2' bestanden
try:
    from packet_parsers.packet_header import PacketHeader
    from packet_parsers.packet_types import PacketID, MAX_CARS
    
    # Aanname: 'oud2/lap_packets.py' heet nu 'packet_parsers/lap_parser.py'
    from packet_parsers.lap_parser import LapDataPacket, LapData, LapDataParser
    
except ImportError as e:
    print(f"[FATAL ERROR] DataProcessor kon packet parsers niet importeren: {e}")
    print("[FATAL ERROR] Controleer packet_header.py, packet_types.py en lap_parser.py.")
    # Placeholders
    class PacketHeader: pass
    class LapDataPacket: pass
    class LapData: pass
    class PacketID:
        LAP_DATA = 2
    MAX_CARS = 22

class DataProcessor:
    """
    Verwerkt rauwe UDP-pakketten en delegeert naar controllers.
    """
    
    def __init__(self, telemetry_controller: TelemetryController):
        """
        Initialiseer de Data Processor.
        
        Args:
            telemetry_controller: De centrale controller voor data opslag.
        """
        self.logger = logger_service.get_logger('DataProcessor')
        self.telemetry_controller = telemetry_controller
        self.lap_data_parser = LapDataParser()
        self.logger.info("Data Processor geïnitialiseerd")

    def process_packet(self, data: bytes):
        """
        Callback functie die door de UDPListener wordt aangeroepen
        met rauwe packet data.
        
        Args:
            data: De rauwe bytes van het UDP pakket.
        """
        if not data:
            return

        header = None
        try:
            # We gebruiken nu de juiste parser
            header = PacketHeader.from_bytes(data)
            
            if not header:
                self.logger.warning("Kon packet header niet parsen (data leeg?)")
                return
            
            # We gebruiken het juiste attribuut (uit 'oud2/packet_header.py')
            packet_id = header.packet_id

            # Stap 2: Stuur data naar de juiste verwerker
            
            if packet_id == PacketID.LAP_DATA:
                self._process_lap_data(data, header)
                
            # --- Voeg hier meer 'if' statements toe voor andere pakketten ---

        except ImportError:
            self.logger.error("Kan pakket niet verwerken door importfout in parsers.")
        except AttributeError as e:
            selfLAG FOUT OPSPOREN
            self.logger.error(f"Fout bij parsen (verkeerde parser structuur?): {e}", exc_info=True)
        except Exception as e:
            packet_id_str = header.packet_id if header else 'N/A'
            self.logger.error(f"Fout bij verwerken pakket (ID: {packet_id_str}): {e}", exc_info=True)

    def _process_lap_data(self, data: bytes, header: PacketHeader):
        """
        Verwerk het volledige Lap Data pakket (Packet 2).
        """
        
        packet = self.lap_data_parser.parse(header, data)
        
        if not packet:
            self.logger.warning("Kon LapDataPacket niet parsen.")
            return
            
        player_index = header.player_car_index
        
        if 0 <= player_index < 22:
            player_lap_data = packet.lap_data[player_index]
            
            # Stuur deze specifieke data (LapData struct) naar de Telemetry Controller
            self.telemetry_controller.update_lap_data(player_lap_data)
        # --- EINDE FIX ---

    # ... (Hier komen later meer _process_... methodes) ...