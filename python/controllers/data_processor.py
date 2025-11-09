"""
F1 25 Telemetry System - Data Processor
(Versie 7: Toevoeging Packet 11 - Session History)
"""
from services import logger_service
from controllers.telemetry_controller import TelemetryController

try:
    from packet_parsers.packet_header import PacketHeader
    from packet_parsers.packet_types import PacketID
    from packet_parsers.lap_parser import LapDataParser, LapDataPacket
    from packet_parsers.participant_parser import ParticipantsParser, ParticipantsPacket
    from packet_parsers.position_parser import PositionParser, LapPositionsPacket
    # --- NIEUWE IMPORT ---
    from packet_parsers.history_parser import SessionHistoryParser, SessionHistoryData
except ImportError as e:
    print(f"[FATAL ERROR] DataProcessor kon packet parsers niet importeren: {e}")
    logger_service.get_logger('DataProcessor').error(f"Fatal Import Error: {e}", exc_info=True)
    raise


class DataProcessor:
    """
    Verwerkt rauwe UDP-pakketten en delegeert naar controllers.
    """

    def __init__(self, telemetry_controller: TelemetryController):
        self.logger = logger_service.get_logger('DataProcessor')
        self.telemetry_controller = telemetry_controller

        # --- Registreer de parsers (volgens MVC) ---
        self.parsers = {
            PacketID.LAP_DATA: LapDataParser(),
            PacketID.PARTICIPANTS: ParticipantsParser(),
            PacketID.LAP_POSITIONS: PositionParser(),
            # --- NIEUWE PARSER ---
            PacketID.SESSION_HISTORY: SessionHistoryParser(),
        }
        self.logger.info("Data Processor geïnitialiseerd (P2, P4, P11, P15)")

    def process_packet(self, data: bytes):
        """
        Callback functie die door de UDPListener wordt aangeroepen.
        """
        if not data: return
        header = None
        try:
            header = PacketHeader.from_bytes(data)
            if not header or not header.is_valid():
                return

            packet_id = header.packet_id

            if packet_id in self.parsers:
                parser = self.parsers[packet_id]
                payload = header.get_payload(data)
                parsed_packet_object = parser.parse(header, payload)

                if not parsed_packet_object:
                    self.logger.warning(f"Parser voor PacketID {packet_id} faalde")
                    return

                # --- ROUTING LOGICA ---
                if packet_id == PacketID.LAP_DATA:
                    self.telemetry_controller.update_lap_data_packet(parsed_packet_object, header)

                elif packet_id == PacketID.PARTICIPANTS:
                    self.telemetry_controller.update_participant_data(parsed_packet_object)

                elif packet_id == PacketID.LAP_POSITIONS:
                    self.telemetry_controller.update_position_data(parsed_packet_object)

                # --- NIEUWE ROUTE (PACKET 11) ---
                elif packet_id == PacketID.SESSION_HISTORY:
                    # Filter: Stuur alleen de historie van de speler naar de controller
                    player_index = header.player_car_index
                    if parsed_packet_object.car_idx == player_index:
                        self.telemetry_controller.update_session_history(parsed_packet_object, header)
                # --- EINDE NIEUWE ROUTE ---

            else:
                try:
                    packet_name = PacketID(packet_id).name
                    self.logger.debug(f"Nog geen parser geregistreerd voor PacketID {packet_id} ({packet_name})")
                except ValueError:
                    self.logger.warning(f"Onbekende PacketID {packet_id} ontvangen.")

        except Exception as e:
            packet_id_str = header.packet_id if header else 'N/A'
            self.logger.error(f"Fout bij verwerken pakket (ID: {packet_id_str}): {e}", exc_info=True)