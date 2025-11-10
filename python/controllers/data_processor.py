"""
F1 25 Telemetry System - Data Processor
Verwerkt rauwe UDP pakketten en stuurt data naar de juiste controllers.
"""
import struct
from services import logger_service

# --- AANGEPASTE IMPORTS ---
from controllers.telemetry_controller import TelemetryController
# SessionController is TOEGEVOEGD
from controllers.session_controller import SessionController

# --- EINDE AANPASSING ---

try:
    from packet_parsers.packet_header import PacketHeader
    from packet_parsers.packet_types import PacketID, MAX_CARS

    # Importeer de PARSER-CLASSES
    from packet_parsers.lap_parser import LapDataPacket, LapData
    from packet_parsers.history_parser import SessionHistoryParser
    # SessionParser is TOEGEVOEGD
    from packet_parsers.session_parser import SessionParser, SessionData

except ImportError as e:
    print(f"[FATAL ERROR] DataProcessor kon packet parsers niet importeren: {e}")


    # Placeholders
    class PacketHeader:
        pass


    class LapDataPacket:
        pass


    class LapData:
        pass


    class SessionHistoryParser:
        pass


    class SessionParser:
        pass  # Toegevoegd


    class SessionData:
        pass  # Toegevoegd


    class PacketID:
        SESSION = 1  # Toegevoegd
        LAP_DATA = 2
        SESSION_HISTORY = 11


    MAX_CARS = 22


class DataProcessor:
    """
    Verwerkt rauwe UDP-pakketten en delegeert naar controllers.
    """

    def __init__(self, telemetry_controller: TelemetryController, session_controller: SessionController):
        """
        Initialiseer de Data Processor.

        Args:
            telemetry_controller: Controller voor lap/telemetry opslag.
            session_controller: Controller voor sessie lifecycle.
        """
        self.logger = logger_service.get_logger('DataProcessor')

        # --- AANGEPAST: Sla *beide* controllers op ---
        self.telemetry_controller = telemetry_controller
        self.session_controller = session_controller

        # Initialiseer de parsers
        self.history_parser = SessionHistoryParser()
        self.session_parser = SessionParser()  # TOEGEVOEGD

        self.logger.info("Data Processor geïnitialiseerd")

    def process_packet(self, data: bytes):
        """
        Callback functie die door de UDPListener wordt aangeroepen.
        """
        if not data:
            return

        header = None
        try:
            header = PacketHeader.from_bytes(data)

            if not header:
                self.logger.warning("Kon packet header niet parsen (data leeg?)")
                return

            packet_id = header.packet_id

            # --- AANGEPASTE ROUTING ---

            if packet_id == PacketID.SESSION:
                # NIEUWE ROUTE: Verwerk Packet 1 (Sessie)
                self._process_session_data(data, header)

            elif packet_id == PacketID.LAP_DATA:
                self._process_lap_data(data, header)

            elif packet_id == PacketID.SESSION_HISTORY:
                self._process_session_history(data, header)

            # --- EINDE AANPASSING ---

        except ImportError:
            self.logger.error("Kan pakket niet verwerken door importfout in parsers.")
        except AttributeError as e:
            self.logger.error(f"Fout bij parsen (verkeerde parser structuur?): {e}", exc_info=True)
        except Exception as e:
            packet_id_str = header.packet_id if header else 'N/A'
            self.logger.error(f"Fout bij verwerken pakket (ID: {packet_id_str}): {e}", exc_info=True)

    # --- NIEUWE FUNCTIE ---
    def _process_session_data(self, data: bytes, header: PacketHeader):
        """
        Verwerk het volledige Session Data pakket (Packet 1).
        Dit creëert de sessie in de database.
        """
        payload = data[29:]
        # Gebruik de SessionParser
        parsed_session_data = self.session_parser.parse(header, payload)

        if not parsed_session_data:
            self.logger.warning("Kon SessionDataPacket niet parsen (parser gaf None).")
            return

        # Gebruik de session_uid (Python-stijl) van de header
        # en geef de geparste data door aan de SessionController.
        self.session_controller.start_session(header.session_uid, parsed_session_data)

    # --- EINDE NIEUWE FUNCTIE ---

    def _process_lap_data(self, data: bytes, header: PacketHeader):
        """
        Verwerk het volledige Lap Data pakket (Packet 2).
        """

        payload = data[29:]
        # Aanname: LapDataPacket __init__ gebruikt (header, payload)
        packet = LapDataPacket(header, payload)

        if not packet or not packet.lap_data:
            self.logger.warning("Kon LapDataPacket niet parsen of data is leeg.")
            return

        player_index = header.player_car_index

        if 0 <= player_index < 22:
            player_lap_data = packet.lap_data[player_index]

            self.telemetry_controller.update_lap_data(
                player_lap_data,
                header.session_uid,
                player_index
            )

    def _process_session_history(self, data: bytes, header: PacketHeader):
        """
        Verwerk het volledige Session History pakket (Packet 11).
        """

        payload = data[29:]
        packet_data = self.history_parser.parse(header, payload)

        if not packet_data:
            self.logger.warning("Kon SessionHistoryPacket niet parsen (parser gaf None).")
            return

        self.telemetry_controller.update_lap_validation(packet_data, header.session_uid)