"""
F1 25 Telemetry System - Data Processor
Verwerkt rauwe UDP pakketten en stuurt data naar de juiste controllers.
(GECORRIGEERDE VERSIE)
"""
import struct
from services import logger_service
from controllers.telemetry_controller import TelemetryController

# --- IMPORTEER ALLE PARSERS EN TYPES ---
try:
    from packet_parsers.packet_header import PacketHeader
    from packet_parsers.packet_types import PacketID
    
    # Importeer de parsers die we gaan gebruiken
    from packet_parsers.lap_parser import LapDataParser, LapDataPacket, LapData
    from packet_parsers.session_parser import SessionParser
    from packet_parsers.participant_parser import ParticipantsParser
    from packet_parsers.car_parser import CarTelemetryParser
    # (Voeg hier later de rest van je 16 parsers toe)

except ImportError as e:
    print(f"[FATAL ERROR] DataProcessor kon packet parsers niet importeren: {e}")
    logger_service.get_logger('DataProcessor').error(f"Fatal Import Error: {e}", exc_info=True)
    # Placeholders om crashes te voorkomen, hoewel de app niet zal werken
    class PacketHeader: pass
    class LapDataPacket: pass
    class LapData: pass
    class PacketID: LAP_DATA = 2
    class LapDataParser: pass


class DataProcessor:
    """
    Verwerkt rauwe UDP-pakketten en delegeert naar controllers.
    Volgt MVC-patroon door parsers uit packet_parsers te gebruiken.
    """
    
    def __init__(self, telemetry_controller: TelemetryController):
        """
        Initialiseer de Data Processor.
        
        Args:
            telemetry_controller: De centrale controller voor data opslag.
        """
        self.logger = logger_service.get_logger('DataProcessor')
        self.telemetry_controller = telemetry_controller
        
        # --- NIEUW: Registreer de parsers (volgens MVC) ---
        # We instantiëren hier de parsers.
        self.parsers = {
            # PacketID.SESSION: SessionParser(),
            PacketID.LAP_DATA: LapDataParser(),
            # PacketID.PARTICIPANTS: ParticipantsParser(),
            # PacketID.CAR_TELEMETRY: CarTelemetryParser(),
            # (Voeg hier de rest van je 16 parsers toe)
        }
        
        self.logger.info("Data Processor geïnitialiseerd met F1 25 parsers")

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
            # 1. Parse de Header
            header = PacketHeader.from_bytes(data)
            
            if not header or not header.is_valid():
                # Gebruik de is_valid() methode uit packet_header.py
                self.logger.warning("Ongeldige of niet-F1 25 header ontvangen.")
                return
            
            packet_id = header.packet_id

            # 2. Delegeer naar de juiste parser (MVC)
            if packet_id in self.parsers:
                parser = self.parsers[packet_id]
                
                # Haal de payload op (data ZONDER de header)
                payload = header.get_payload(data)
                
                # 3. De parser doet het zware werk
                parsed_packet_object = parser.parse(header, payload)
                
                if not parsed_packet_object:
                    self.logger.warning(f"Parser voor PacketID {packet_id} faalde (payload size?)")
                    return

                # 4. Stuur het *geparste object* naar de juiste verwerkingsmethode
                if packet_id == PacketID.LAP_DATA:
                    self._process_lap_data(parsed_packet_object, header)
                
                # (Voeg hier 'elif' blokken toe voor andere pakket IDs)
                # elif packet_id == PacketID.SESSION:
                #    self._process_session_data(parsed_packet_object, header)

            else:
                # We loggen alleen als de packet ID bekend is maar geen parser heeft
                if packet_id in PacketID._value2member_map_:
                    self.logger.debug(f"Nog geen parser geregistreerd voor PacketID {packet_id}")

        except ImportError:
            self.logger.error("Kan pakket niet verwerken door importfout in parsers.")
        except AttributeError as e:
            self.logger.error(f"Fout bij parsen (structuur klopt niet?): {e}", exc_info=True)
        except Exception as e:
            packet_id_str = header.packet_id if header else 'N/A'
            self.logger.error(f"Fout bij verwerken pakket (ID: {packet_id_str}): {e}", exc_info=True)

    def _process_lap_data(self, packet: LapDataPacket, header: PacketHeader):
        """
        Verwerk het *geparste* Lap Data pakket (Packet 2).
        
        Args:
            packet: Het LapDataPacket dataclass object (uit lap_parser.py)
            header: De PacketHeader
        """
        
        # De oude, handmatige parsing logica is nu *weg*.
        
        player_index = header.player_car_index
        
        # De 'packet.lap_data' is de lijst met 22 LapData objecten
        if 0 <= player_index < len(packet.lap_data):
            # Haal de specifieke LapData dataclass voor de speler op
            player_lap_data_struct = packet.lap_data[player_index]
            
            # Stuur deze specifieke data (LapData struct) naar de Telemetry Controller
            self.telemetry_controller.update_lap_data(player_lap_data_struct)
        else:
            self.logger.warning(f"Player index {player_index} buiten bereik voor LapData.")

    # ... (Hier komen later je andere _process_... methodes) ...
    # def _process_session_data(self, packet: SessionData, header: PacketHeader):
    #     pass