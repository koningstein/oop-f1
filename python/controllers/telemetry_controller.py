"""
F1 25 Telemetry System - Telemetry Controller
(Versie 7: Correcte state logic voor lap history)
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

        # --- GECORRIGEERDE State voor Lap History (Scherm 1.5) ---
        self.completed_laps: List[LapData] = []
        # We houden de *vorige* state bij om voltooide ronden te vangen
        self.previous_player_data: Optional[LapData] = None
        # --- EINDE CORRECTIE ---

        self.logger.info("Telemetry Controller geïnitialiseerd (Full Grid State, Lap History)")

    # --- Data Update Methoden ---

    def update_lap_data_packet(self, packet: LapDataPacket, header: PacketHeader):
        with self.lock:
            self.all_lap_data = packet.lap_data
            player_index = header.player_car_index
            if not (0 <= player_index < 22):
                return

            # 1. Haal de *nieuwe* data op
            new_player_data = packet.lap_data[player_index]
            self.player_lap_data = new_player_data # Sla live data op (voor 'Huidige Ronde')

            # 2. Check of we de *vorige* state moeten opslaan
            if self.previous_player_data:

                # Check 1: Is er een nieuwe ronde gestart?
                new_lap_started = new_player_data.current_lap_num > self.previous_player_data.current_lap_num

                # Check 2: Gaan we terug naar de pits?
                reset_detected = new_player_data.current_lap_num == 0 and self.previous_player_data.current_lap_num > 0

                if new_lap_started:
                    # De *vorige* state (previous_player_data) bevat nu
                    # de S1, S2 en Totaal tijd van de zojuist voltooide ronde.

                    # Sla de *vorige* state op (de voltooide ronde)
                    # Sla de outlap (ronde 0) niet op
                    if self.previous_player_data.current_lap_num > 0:
                        self.completed_laps.append(self.previous_player_data)
                        self.logger.info(f"Ronde {self.previous_player_data.current_lap_num} opgeslagen (Tijd: {self.previous_player_data.last_lap_time_ms})")

                elif reset_detected:
                     self.logger.info("Resetting lap history (terug naar garage/nieuw sessie)")
                     self.completed_laps = []

            # 3. Update de 'previous' state voor de *volgende* iteratie
            self.previous_player_data = new_player_data

    # ... (Rest van de update-methoden blijven ongewijzigd) ...
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

    def get_completed_laps(self) -> List[LapData]:
        """ Haalt de lijst met voltooide ronden op (voor 1.5) """
        with self.lock:
            return list(self.completed_laps) # Retourneer een kopie

    # ... (Rest van de getters blijven ongewijzigd) ...
    def get_combined_timing_data(self) -> List[Dict[str, Any]]:
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
                        'name': driver_name, 'position': l_data.car_position,
                        'last_lap_time_ms': l_data.last_lap_time_ms,
                        'current_lap_time_ms': l_data.current_lap_time_ms,
                        'best_lap_time_ms': l_data.best_lap_time_ms,
                    })
        return sorted(combined_data, key=lambda x: x['position'])

    def get_position_chart_data(self) -> (Optional[LapPositionsData], List[str]):
        with self.lock:
            if not self.position_data or not self.participants:
                return None, []
            names = [p.get_name() for p in self.participants if p.get_name()]
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