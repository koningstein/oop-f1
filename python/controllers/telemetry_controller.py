"""
F1 25 Telemetry System - Telemetry Controller
(Versie 8: State management voor Packet 2 en Packet 11)
"""
import threading
from services import logger_service
from models import SessionModel, DriverModel, LapModel
from typing import Optional, List, Dict, Any

try:
    from packet_parsers.packet_header import PacketHeader
    from packet_parsers.lap_parser import LapData, LapDataPacket
    from packet_parsers.participant_parser import ParticipantData, ParticipantsPacket
    from packet_parsers.position_parser import LapPositionsData, LapPositionsPacket
    # --- NIEUWE IMPORT ---
    from packet_parsers.history_parser import SessionHistoryData
except ImportError:
    print("[FATAL ERROR] TelemetryController kon parser dataclasses niet importeren.")


    class LapData:
        pass


    class LapDataPacket:
        pass


    class ParticipantData:
        pass


    class ParticipantsPacket:
        pass


    class LapPositionsData:
        pass


    class PacketHeader:
        pass


    class SessionHistoryData:
        pass  # Placeholder


class TelemetryController:

    def __init__(self):
        self.logger = logger_service.get_logger('TelemetryController')
        self.session_model = SessionModel()
        self.driver_model = DriverModel()
        self.lap_model = LapModel()
        self.lock = threading.Lock()

        # --- Data Opslag (State) ---

        # Voor Live Timing (Packet 2)
        self.player_lap_data: Optional[LapData] = None
        self.all_lap_data: List[LapData] = [LapData() for _ in range(22)]

        # Voor Historie Tabel (Packet 11)
        self.player_session_history: Optional[SessionHistoryData] = None

        # Andere data
        self.participants: List[ParticipantData] = [ParticipantData() for _ in range(22)]
        self.position_data: Optional[LapPositionsData] = None

        self.logger.info("Telemetry Controller geïnitialiseerd (P2, P4, P11, P15)")

    # --- Data Update Methoden ---

    def update_lap_data_packet(self, packet: LapDataPacket, header: PacketHeader):
        """ Update de LIVE data van Packet 2 """
        with self.lock:
            self.all_lap_data = packet.lap_data
            player_index = header.player_car_index
            if not (0 <= player_index < 22):
                return

            # Sla alleen de *huidige* live data van de speler op
            self.player_lap_data = packet.lap_data[player_index]

    def update_session_history(self, packet: SessionHistoryData, header: PacketHeader):
        """
        Update de HISTORIE data van Packet 11.
        De DataProcessor filtert al dat dit de speler is.
        """
        with self.lock:
            self.player_session_history = packet
            self.logger.debug(f"P11 (History) geüpdatet voor car_idx {packet.car_idx}")

    def update_participant_data(self, packet: ParticipantsPacket):
        with self.lock:
            self.participants = packet.participants

    def update_position_data(self, packet: LapPositionsPacket):
        with self.lock:
            self.position_data = packet.lap_positions

    # --- Data Getter Methoden ---

    def get_player_lap_data(self) -> Optional[LapData]:
        """ Voor live 'Huidige Ronde' (1.5) - Bron: Packet 2 """
        with self.lock:
            return self.player_lap_data

    def get_player_lap_history(self) -> Optional[SessionHistoryData]:
        """ Haalt de complete ronde historie op (voor 1.5) - Bron: Packet 11 """
        with self.lock:
            return self.player_session_history

    # ... (Rest van de getters blijven ongewijzigd) ...
    def get_combined_timing_data(self) -> List[Dict[str, Any]]:
        combined_data = []
        with self.lock:
            local_participants = list(self.participants)
            local_lap_data = list(self.all_lap_data)

            # Voeg een check toe of de data al geïnitialiseerd is
            if not local_participants or not local_lap_data:
                return []

            for i in range(22):
                p_data = local_participants[i]
                l_data = local_lap_data[i]

                # Check of p_data wel de get_name methode heeft
                driver_name = ""
                if hasattr(p_data, 'get_name'):
                    driver_name = p_data.get_name()

                if driver_name:
                    # Zoek naar best_lap_time_ms (bestaat niet in LapData V11)
                    # We gebruiken last_lap_time_ms als fallback
                    best_lap_ms = 0
                    if hasattr(l_data, 'best_lap_time_ms'):
                        best_lap_ms = l_data.best_lap_time_ms

                    combined_data.append({
                        'name': driver_name, 'position': l_data.car_position,
                        'last_lap_time_ms': l_data.last_lap_time_ms,
                        'current_lap_time_ms': l_data.current_lap_time_ms,
                        'best_lap_time_ms': best_lap_ms,  # Gebruik de gevonden waarde
                    })
        return sorted(combined_data, key=lambda x: x['position'])

    def get_position_chart_data(self) -> (Optional[LapPositionsData], List[str]):
        with self.lock:
            if not self.position_data or not self.participants:
                return None, []
            names = [p.get_name() for p in self.participants if hasattr(p, 'get_name') and p.get_name()]
            return self.position_data, names

    def get_tournament_standings(self) -> List[Dict[str, Any]]:
        self.logger.info("get_tournament_standings (1.3) aangeroepen")
        try:
            demo_standings = [
                {"Pos": "1.", "Naam": "Marcel (DB)", "Team": "Mercedes", "Punten": "150"},
                {"Pos": "2.", "Naam": "Verstappen (DB)", "Team": "Red Bull", "Punten": "144"},
            ]
            return demo_standings
        except Exception as e:
            self.logger.error(f"Databasefout in get_tournament_standings: {e}")
            return []

    def get_current_session_id(self):
        self.logger.warning("TelemetryController.get_current_session_id aangeroepen (placeholder).")
        return None