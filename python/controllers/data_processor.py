"""
F1 25 Telemetry System - Data Processor
(Versie 9: Gebaseerd op V7 (werkend) + P1/SessionController-injectie)
"""
from typing import Set

# --- SYSTEEM IMPORT FIX ---
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --- EINDE SYSTEEM IMPORT FIX ---

from services import logger_service

# Importeer de controllers (Type Hinting)
from controllers.telemetry_controller import TelemetryController
# --- AANGEPAST: SessionController import ---
from controllers.session_controller import SessionController

# --- EINDE AANPASSING ---

try:
    from packet_parsers.packet_header import PacketHeader
    from packet_parsers.packet_types import PacketID

    # --- AANGEPAST: Importeer ALLE parsers die we nodig hebben ---
    from packet_parsers.session_parser import SessionParser
    from packet_parsers.lap_parser import LapDataParser
    from packet_parsers.participant_parser import ParticipantsParser
    from packet_parsers.history_parser import SessionHistoryParser

    try:
        from packet_parsers.position_parser import LapPositionsParser
    except ImportError:
        # Fallback voor de naam in jouw V7-code ('PositionParser')
        from packet_parsers.position_parser import PositionParser as LapPositionsParser
    # --- EINDE AANPASSING ---

except ImportError as e:
    print(f"[FATAL ERROR] DataProcessor kon packet parsers niet importeren: {e}")
    logger_service.get_logger('DataProcessor').error(f"Fatal Import Error: {e}", exc_info=True)
    sys.exit(1)


class DataProcessor:
    """
    Verwerkt rauwe UDP-pakketten en delegeert naar controllers.
    (Gebaseerd op de werkende V7-logica)
    """

    # --- AANGEPAST: __init__ accepteert nu SessionController ---
    def __init__(self, telemetry_controller: TelemetryController, session_controller: SessionController):
        self.logger = logger_service.get_logger('DataProcessor')
        self.telemetry_controller = telemetry_controller
        # --- NIEUWE INJECTIE ---
        self.session_controller = session_controller
        # --- EINDE NIEUWE INJECTIE ---

        # --- Registreer de parsers (V7 logica + P1) ---
        self.parsers = {
            PacketID.SESSION: SessionParser(),  # Nodig voor DB
            PacketID.LAP_DATA: LapDataParser(),
            PacketID.PARTICIPANTS: ParticipantsParser(),
            PacketID.SESSION_HISTORY: SessionHistoryParser(),
        }
        if LapPositionsParser:
            self.parsers[PacketID.LAP_POSITIONS] = LapPositionsParser()
        else:
            self.logger.warning("LapPositionsParser (P15) niet geladen. P15 wordt genegeerd.")
        # --- EINDE PARSER REGISTRATIE ---

        # --- STATE (uit V7/V8) ---
        self.player_car_index = 0
        self.history_packets_sent: Set[int] = set()
        # --- EINDE STATE ---

        self.logger.info("Data Processor V9 (V7+DB) geïnitialiseerd (P1, P2, P4, P11, P15)")

    # --- EINDE AANPASSING ---

    def process_packet(self, data: bytes):
        """
        Callback functie die door de UDPListener wordt aangeroepen.
        (Logica 1:1 overgenomen uit jouw werkende V7)
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

                # --- DIT IS DE KERNLOGICA (uit V7) ---
                # ALLE parsers (inclusief LapDataParser) krijgen (header, payload)
                # Mijn eerdere 'if/else' was de fout.
                payload = header.get_payload(data)
                parsed_packet_object = parser.parse(header, payload)
                # --- EINDE KERNLOGICA ---

                # --- DE CRASH-FIX (uit V7) ---
                # Als de parser faalt (bv. size check), retourneert het None.
                if not parsed_packet_object:
                    # De parser heeft zelf al gelogd (bv. "payload size incorrect")
                    self.logger.warning(
                        f"Parser voor PacketID {packet_id} retourneerde None (corrupt/invalid size). Stoppen met routering.")
                    return
                # --- EINDE CRASH-FIX ---

                # --- ROUTING LOGICA (V7 + P1) ---

                # NIEUWE ROUTE (DATABASE)
                if packet_id == PacketID.SESSION:
                    self.session_controller.process_session_packet(parsed_packet_object, header)

                # OUDE ROUTES (LIVE VIEW)
                elif packet_id == PacketID.LAP_DATA:
                    self.telemetry_controller.update_lap_data_packet(parsed_packet_object, header)

                elif packet_id == PacketID.PARTICIPANTS:
                    self.telemetry_controller.update_participant_data(parsed_packet_object)
                    # Update de state voor P11 filtering
                    self.player_car_index = header.player_car_index

                elif packet_id == PacketID.LAP_POSITIONS:
                    self.telemetry_controller.update_position_data(parsed_packet_object)

                elif packet_id == PacketID.SESSION_HISTORY:
                    # Filter: Stuur alleen de historie van de speler naar de controller
                    if parsed_packet_object.car_idx == self.player_car_index:
                        if parsed_packet_object.car_idx not in self.history_packets_sent:
                            self.logger.info(
                                f"Eerste P1J (History) ontvangen voor speler (idx {self.player_car_index})")
                            self.history_packets_sent.add(parsed_packet_object.car_idx)
                        self.telemetry_controller.update_session_history(parsed_packet_object, header)
                # --- EINDE ROUTING ---

            # (else: debug log voor 'Nog geen parser' is niet nodig)

        except Exception as e:
            packet_id_str = header.packet_id if header else 'N/A'
            self.logger.error(f"Fout bij verwerken pakket (ID: {packet_id_str}): {e}", exc_info=True)