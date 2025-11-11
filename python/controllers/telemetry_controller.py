"""
F1 25 Telemetry System - Telemetry Controller
(Versie 9.5: Correctie AttributeError 'lap_time_in_ms' -> 'lap_time_ms')
"""
import threading
from services import logger_service
from models import SessionModel, DriverModel, LapModel
from typing import Optional, List, Dict, Any, Set

# --- AANPASSING V9.2: Import voor Injectie ---
try:
    from controllers.session_controller import SessionController
except ImportError:
    print("[FATAL ERROR] TelemetryController kon SessionController niet importeren.")


    # Placeholder voor type hinting
    class SessionController:
        pass
# --- EINDE AANPASSING ---


try:
    from packet_parsers.packet_header import PacketHeader
    from packet_parsers.lap_parser import LapData, LapDataPacket
    from packet_parsers.participant_parser import ParticipantData, ParticipantsPacket
    from packet_parsers.position_parser import LapPositionsData, LapPositionsPacket
    from packet_parsers.history_parser import SessionHistoryData, LapHistoryData
except ImportError:
    print("[FATAL ERROR] TelemetryController kon parser dataclasses niet importeren.")


    # Placeholders...
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
        pass


    class LapHistoryData:
        pass


class TelemetryController:

    # --- AANPASSING V9.2: Injectie in __init__ ---
    def __init__(self, session_controller: SessionController):
        self.logger = logger_service.get_logger('TelemetryController')
        self.session_model = SessionModel()
        self.driver_model = DriverModel()
        self.lap_model = LapModel()

        # --- NIEUWE INJECTIE (V9.2) ---
        self.session_controller = session_controller
        # --- EINDE NIEUWE INJECTIE ---

        self.lock = threading.Lock()

        # --- Data Opslag (State) ---
        self.player_lap_data: Optional[LapData] = None
        self.all_lap_data: List[LapData] = [LapData() for _ in range(22)]
        self.player_session_history: Optional[SessionHistoryData] = None
        self.participants: List[ParticipantData] = [ParticipantData() for _ in range(22)]
        self.position_data: Optional[LapPositionsData] = None
        self.player_laps_saved_state: Dict[int, Set[int]] = {}
        self.current_session_uid: Optional[int] = None

        self.logger.info("Telemetry Controller (V9.5 - Robuust P11) geïnitialiseerd")

    # --- EINDE AANPASSING V9.2 ---

    # --- Data Update Methoden ---

    def update_lap_data_packet(self, packet: LapDataPacket, header: PacketHeader):
        """ Update de LIVE data van Packet 2 """
        with self.lock:
            self.current_session_uid = header.session_uid
            self.all_lap_data = packet.lap_data
            player_index = header.player_car_index
            if not (0 <= player_index < 22):
                return
            self.player_lap_data = packet.lap_data[player_index]

    # --- AANPASSING V9.5: Correctie 'lap_time_ms' ---
    def update_session_history(self, packet: SessionHistoryData, header: PacketHeader):
        """
        Update de HISTORIE data van Packet 11 (Bron: DataProcessor).
        (V9.5: Nu robuust tegen P1-falen + correcte LapHistoryData attributen)
        """
        car_index = packet.car_idx

        with self.lock:
            self.current_session_uid = header.session_uid

            # 1. Update de live state (voor de views)
            if header.player_car_index == car_index:
                self.player_session_history = packet
                self.logger.debug(f"P11 (History) geüpdatet voor car_idx {car_index}")

            # 2. Haal de database ID voor deze sessie op
            session_data = self._get_db_session_id_from_uid(header.session_uid)
            db_session_id: Optional[int] = None

            if not session_data:
                self.logger.warning(
                    f"Kan lap niet opslaan: Sessie (UID {header.session_uid}) "
                    f"is nog niet in de database. P1-falen wordt vermoed."
                )
                self.logger.info(f"P11 (History) forceert aanmaak van 'placeholder' sessie...")

                # --- ROBUUSTHEIDS FIX (V9.2) ---
                db_session_id = self.session_controller.create_placeholder_session(header)

                if not db_session_id:
                    self.logger.error(f"Nood-aanmaak van sessie {header.session_uid} is MISLUKT. Kan lap niet opslaan.")
                    return
                self.logger.info(f"Placeholder sessie succesvol (ID {db_session_id}). Doorgaan met lap save.")
                # --- EINDE FIX ---
            else:
                db_session_id = session_data.get('id')

            if not db_session_id:
                self.logger.error(f"Kritieke fout: db_session_id is 'None' na P1-check (UID {header.session_uid}).")
                return

            # 3. Initialiseer de 'saved laps' state voor deze auto
            if car_index not in self.player_laps_saved_state:
                self.player_laps_saved_state[car_index] = set()

            # 4. Loop door de ronde-historie en sla nieuwe rondes op
            for lap_num_minus_1, lap_entry in enumerate(packet.lap_history_data):
                lap_num = lap_num_minus_1 + 1

                # --- FIX V9.5 (Latente Bug) ---
                # De parser (HistoryParser) levert 'lap_time_ms' etc. (zonder _in_)
                # De error log (Did you mean: 'lap_time_ms'?) bevestigt dit.

                if lap_entry.lap_time_ms == 0:
                    continue
                # --- EINDE FIX V9.5 ---

                if lap_num in self.player_laps_saved_state[car_index]:
                    continue

                # --- NIEUWE RONDE GEVONDEN! ---
                flags = lap_entry.lap_valid_bit_flags
                is_lap_valid = (flags & 0x01) == 0
                is_s1_valid = (flags & 0x02) == 0
                is_s2_valid = (flags & 0x04) == 0
                is_s3_valid = (flags & 0x08) == 0

                # --- FIX V9.5 (Latente Bug) ---
                # Pas alle attribuutnamen aan
                lap_data_dict = {
                    "session_id": db_session_id,
                    "car_index": car_index,
                    "lap_number": lap_num,
                    "lap_time_ms": lap_entry.lap_time_ms,
                    "sector1_ms": lap_entry.sector1_time_ms,
                    "sector2_ms": lap_entry.sector2_time_ms,
                    "sector3_ms": lap_entry.sector3_time_ms,
                    "is_valid": is_lap_valid,
                    "sector1_valid": is_s1_valid,
                    "sector2_valid": is_s2_valid,
                    "sector3_valid": is_s3_valid
                }
                # --- EINDE FIX V9.5 ---

                # 5. Start de DB save in een APARTE THREAD (NON-BLOCKING)
                self.logger.debug(f"Start DB save thread voor Lap {lap_num}, Car {car_index}")
                db_thread = threading.Thread(
                    target=self.lap_model.save_lap,
                    args=(lap_data_dict,)
                )
                db_thread.start()

                # 6. Markeer de ronde als 'opgeslagen' in onze state
                self.player_laps_saved_state[car_index].add(lap_num)

    def update_participant_data(self, packet: ParticipantsPacket):
        with self.lock:
            self.participants = packet.participants

    def update_position_data(self, packet: LapPositionsPacket):
        with self.lock:
            self.position_data = packet.lap_positions

    # --- Data Getter Methoden ---

    def get_player_lap_data(self) -> Optional[LapData]:
        with self.lock:
            return self.player_lap_data

    def get_player_lap_history(self) -> Optional[SessionHistoryData]:
        with self.lock:
            return self.player_session_history

    def get_combined_timing_data(self) -> List[Dict[str, Any]]:
        combined_data = []
        with self.lock:
            local_participants = list(self.participants)
            local_lap_data = list(self.all_lap_data)

            if not local_participants or not local_lap_data:
                return []

            for i in range(22):
                p_data = local_participants[i]
                l_data = local_lap_data[i]

                driver_name = ""
                if hasattr(p_data, 'get_name'):
                    driver_name = p_data.get_name()

                if driver_name:
                    best_lap_ms = 0
                    if hasattr(l_data, 'best_lap_time_ms'):
                        best_lap_ms = l_data.best_lap_time_ms

                    combined_data.append({
                        'name': driver_name, 'position': l_data.car_position,
                        'last_lap_time_ms': l_data.last_lap_time_ms,
                        'current_lap_time_ms': l_data.current_lap_time_ms,
                        'best_lap_time_ms': best_lap_ms,
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

    # --- GECORRIGEERDE METHODE (TOEVOEGINg 3 uit V9.1) ---
    def get_current_session_id(self) -> Optional[int]:
        """
        Haalt de database 'id' (INT) op van de huidige actieve sessie.
        """
        uid_to_check = None
        with self.lock:
            uid_to_check = self.current_session_uid

        if not uid_to_check:
            self.logger.debug("get_current_session_id: Geen current_session_uid bekend.")
            return None

        session_data = self._get_db_session_id_from_uid(uid_to_check)

        if session_data:
            return session_data.get('id')  # Retourneert de database Primary Key (id)

        self.logger.debug(
            f"get_current_session_id: Kon session_uid {uid_to_check} "
            f"nog niet vinden in 'sessions' tabel (wacht op P11/P1).")
        return None

    # --- EINDE TOEVOEGINg 3 ---

    # --- NIEUWE HELPER METHODE (Deze was al in V9) ---
    def _get_db_session_id_from_uid(self, session_uid: int) -> Optional[Dict[str, Any]]:
        """
        Haalt de database 'id' op van de huidige sessie (uit de 'sessions' tabel)
        op basis van de 'session_uid' uit het UDP packet.
        """
        if not session_uid or session_uid == 0:
            return None

        try:
            session_data = self.session_model.get_session_by_uid(session_uid)
            return session_data
        except Exception as e:
            self.logger.error(f"Fout bij ophalen session_id voor UID {session_uid}: {e}")
            return None