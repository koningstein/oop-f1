"""
F1 25 Telemetry System - Telemetry Controller
(Versie 6: State management voor lap history (1.5))
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


    # (Placeholders)
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


class TelemetryController:
    """
    Beheert alle F1 25 telemetrie data (thread-safe)
    """

    def __init__(self):
        self.logger = logger_service.get_logger('TelemetryController')
        self.session_model = SessionModel()
        self.driver_model = DriverModel()
        self.lap_model = LapModel()
        self.lock = threading.Lock()

        # --- Data Opslag (State) ---
        self.player_lap_data: Optional[LapData] = None
        self.all_lap_data: List[LapData] = [LapData() for _ in range(22)]
        self.participants: List[ParticipantData] = [ParticipantData() for _ in range(22)]
        self.position_data: Optional[LapPositionsData] = None

        # --- NIEUW: State voor Lap History (Scherm 1.5) ---
        self.completed_laps: List[LapData] = []
        self.last_known_lap_num: int = 0
        # --- EINDE NIEUW ---

        self.logger.info("Telemetry Controller geïnitialiseerd (Full Grid State, Lap History)")

    # --- Data Update Methoden ---

    def update_lap_data_packet(self, packet: LapDataPacket, header: PacketHeader):
        with self.lock:
            self.all_lap_data = packet.lap_data
            player_index = header.player_car_index

            if not (0 <= player_index < 22):
                return

            # Haal de *huidige* data van de speler op
            current_player_data = packet.lap_data[player_index]
            self.player_lap_data = current_player_data  # Sla de live data op

            # --- NIEUW: Detecteer en bewaar voltooide ronden ---
            current_lap_num = current_player_data.current_lap_num

            # Als de game een nieuwe ronde detecteert (bv. van 1 naar 2)
            if current_lap_num > self.last_known_lap_num:
                # ... en de 'last_lap_time' is zojuist gezet (niet 0) ...
                if current_player_data.last_lap_time_ms > 0:
                    # Dan is de 'current_player_data' die we *net* hebben ontvangen
                    # de definitieve data voor de ronde die zojuist is voltooid.
                    # Sla deze op in onze historie.
                    self.completed_laps.append(current_player_data)
                    self.last_known_lap_num = current_lap_num
                    self.logger.info(
                        f"Ronde {current_lap_num - 1} opgeslagen in historie (Tijd: {current_player_data.last_lap_time_ms})")

            # Reset historie als we terug naar de garage gaan (Lap 0)
            elif current_lap_num == 0 and self.last_known_lap_num != 0:
                self.logger.info("Resetting lap history (terug naar garage/nieuw sessie)")
                self.completed_laps = []
                self.last_known_lap_num = 0
            # --- EINDE NIEUW ---

    def update_participant_data(self, packet: ParticipantsPacket):
        with self.lock:
            self.participants = packet.participants

    def update_position_data(self, packet: LapPositionsPacket):
        with self.lock:
            self.position_data = packet.lap_positions

    # --- Data Getter Methoden ---

    def get_player_lap_data(self) -> Optional[LapData]:
        """ Voor live 'Huidige Ronde' (1.5) """
        with self.lock:
            return self.player_lap_data

    # --- NIEUW: Getter voor de historie ---
    def get_completed_laps(self) -> List[LapData]:
        """ Haalt de lijst met voltooide ronden op (voor 1.5) """
        with self.lock:
            return list(self.completed_laps)  # Retourneer een kopie

    # --- EINDE NIEUW ---

    def get_combined_timing_data(self) -> List[Dict[str, Any]]:
        # ... (deze methode blijft ongewijzigd) ...
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
        # ... (deze methode blijft ongewijzigd) ...
        with self.lock:
            if not self.position_data or not self.participants:
                return None, []
            names = [p.get_name() for p in self.participants if p.get_name()]
            return self.position_data, names

    def get_tournament_standings(self) -> List[Dict[str, Any]]:
        # ... (deze methode blijft ongewijzigd) ...
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
        # ... (deze methode blijft ongewijzigd) ...
        self.logger.warning("TelemetryController.get_current_session_id aangeroepen (placeholder).")
        return None