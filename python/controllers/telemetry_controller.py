"""
F1 25 Telemetry System - Telemetry Controller
Beheert de data state en fungeert als interface voor de views.
(Versie 5: State management voor P2, P4, P15 en Database (1.3))
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
except ImportError:
    print("[FATAL ERROR] TelemetryController kon parser dataclasses niet importeren.")
    class LapData: pass
    class LapDataPacket: pass
    class ParticipantData: pass
    class ParticipantsPacket: pass
    class LapPositionsData: pass
    class PacketHeader: pass

class TelemetryController:
    """
    Beheert alle F1 25 telemetrie data (thread-safe)
    """

    def __init__(self):
        self.logger = logger_service.get_logger('TelemetryController')

        # Database modellen (voor 1.3)
        self.session_model = SessionModel()
        self.driver_model = DriverModel()
        self.lap_model = LapModel()

        self.lock = threading.Lock()

        # --- Data Opslag (State) ---
        self.player_lap_data: Optional[LapData] = None
        self.all_lap_data: List[LapData] = [LapData() for _ in range(22)]
        self.participants: List[ParticipantData] = [ParticipantData() for _ in range(22)]
        self.position_data: Optional[LapPositionsData] = None

        self.logger.info("Telemetry Controller geïnitialiseerd (Full Grid State)")

    # --- Data Update Methoden (Aangeroepen door DataProcessor) ---

    def update_lap_data_packet(self, packet: LapDataPacket, header: PacketHeader):
        with self.lock:
            self.all_lap_data = packet.lap_data
            player_index = header.player_car_index
            if 0 <= player_index < 22:
                self.player_lap_data = packet.lap_data[player_index]

    def update_participant_data(self, packet: ParticipantsPacket):
        with self.lock:
            self.participants = packet.participants

    def update_position_data(self, packet: LapPositionsPacket):
        """ Sla de positie data op (Packet 15) """
        with self.lock:
            self.position_data = packet.lap_positions
            self.logger.info(f"Position data (P15) ontvangen. {packet.lap_positions.num_laps} rondes.")

    # --- Data Getter Methoden (Aangeroepen door Views) ---

    def get_player_lap_data(self) -> Optional[LapData]:
        """ Voor 1.5 Live Timing """
        with self.lock:
            return self.player_lap_data

    def get_combined_timing_data(self) -> List[Dict[str, Any]]:
        """ Combineert P2 en P4 voor leaderboards (1.1, 1.2) """
        combined_data = []
        with self.lock:
            local_participants = list(self.participants)
            local_lap_data = list(self.all_lap_data)

            for i in range(22):
                p_data = local_participants[i]
                l_data = local_lap_data[i]
                driver_name = p_data.get_name()

                if driver_name:
                    combined_data.append({
                        'name': driver_name,
                        'position': l_data.car_position,
                        'last_lap_time_ms': l_data.last_lap_time_ms,
                        'current_lap_time_ms': l_data.current_lap_time_ms,
                        'best_lap_time_ms': l_data.best_lap_time_ms,
                    })
        return sorted(combined_data, key=lambda x: x['position'])

    def get_position_chart_data(self) -> (Optional[LapPositionsData], List[str]):
        """ Haalt P15 data en P4 namen op voor 1.4 """
        with self.lock:
            if not self.position_data or not self.participants:
                return None, []

            names = [p.get_name() for p in self.participants if p.get_name()]
            return self.position_data, names

    def get_tournament_standings(self) -> List[Dict[str, Any]]:
        """
        Haalt data op uit de DATABASE (Models) voor 1.3
        Dit is een placeholder; de daadwerkelijke query moet nog gebouwd worden.
        """
        self.logger.info("get_tournament_standings (1.3) aangeroepen")
        try:
            # TODO: Bouw hier de complexe SQL query
            # Voor nu, return we demo data uit de *database model laag*
            demo_standings = [
                {"Pos": "1.", "Naam": "Marcel (DB)", "Team": "Mercedes", "Punten": "150"},
                {"Pos": "2.", "Naam": "Verstappen (DB)", "Team": "Red Bull", "Punten": "144"},
            ]
            # drivers = self.driver_model.get_all_drivers_with_points()
            # return drivers
            return demo_standings
        except Exception as e:
            self.logger.error(f"Databasefout in get_tournament_standings: {e}")
            return []

    def get_current_session_id(self):
        self.logger.warning("TelemetryController.get_current_session_id aangeroepen (placeholder).")
        return None