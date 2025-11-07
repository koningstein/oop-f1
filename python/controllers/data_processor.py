"""
F1 25 Telemetry System - Data Processor
Verwerkt rauwe UDP pakketten en stuurt data naar de juiste controllers.
"""
from services import logger_service
from controllers.telemetry_controller import TelemetryController

# --- GECORRIGEERDE IMPORTS ---
# We importeren nu de klassen vanuit hun specifieke bestanden,
# gebaseerd op je originele listener en bestandsstructuur.
try:
    from packet_parsers.packet_header import PacketHeader
    from packet_parsers.packet_types import PacketID, PacketLapData
except ImportError as e:
    print(f"[FATAL ERROR] DataProcessor kon packet parsers niet importeren: {e}")
    print("[FATAL ERROR] Zorg dat 'packet_header.py' en 'packet_types.py' bestaan in 'packet_parsers'.")
    # Placeholders om te voorkomen dat de app crasht bij import
    class PacketHeader: pass
    class PacketLapData: pass
    class PacketID:
        LAP_DATA = 2

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
            # --- GECORRIGEERDE METHODE ---
            # Stap 1: Parse de header om de Packet ID te krijgen
            # We gebruiken nu .from_bytes() zoals in jouw originele code
            header = PacketHeader.from_bytes(data)
            
            if not header:
                self.logger.warning("Kon packet header niet parsen (data leeg?)")
                return

            packet_id = header.m_packetId

            # Stap 2: Stuur data naar de juiste verwerker
            
            # --- Verwerking voor Scherm 1.5 ---
            if packet_id == PacketID.LAP_DATA:
                self._process_lap_data(data, header)
                
            # --- Voeg hier meer 'if' statements toe voor andere pakketten ---
            # elif packet_id == PacketID.CAR_TELEMETRY:
            #    self._process_telemetry_data(data, header)

        except ImportError:
            # Vangt de error van de placeholder classes
            self.logger.error("Kan pakket niet verwerken door importfout in parsers.")
        except AttributeError as e:
            # Vangt fouten zoals .from_bytes() niet gevonden
            self.logger.error(f"Fout bij parsen (verkeerde parser structuur?): {e}", exc_info=True)
        except Exception as e:
            packet_id_str = header.m_packetId if header else 'N/A'
            self.logger.error(f"Fout bij verwerken pakket (ID: {packet_id_str}): {e}", exc_info=True)

    def _process_lap_data(self, data: bytes, header: PacketHeader):
        """
        Verwerk het volledige Lap Data pakket (Packet 2).
        """
        # --- GECORRIGEERDE METHODE ---
        # Parse het volledige pakket met .from_bytes()
        packet = PacketLapData.from_bytes(data)
        
        if not packet:
            self.logger.warning("Kon PacketLapData niet parsen.")
            return
            
        # Haal de data voor de speler op
        player_index = header.m_playerCarIndex
        if 0 <= player_index < 22: # cs_maxNumCarsInUDPData = 22
            player_lap_data = packet.m_lapData[player_index]
            
            # Stuur deze specifieke data (LapData struct) naar de Telemetry Controller
            self.telemetry_controller.update_lap_data(player_lap_data)

    # ... (Hier komen later meer _process_... methodes) ...