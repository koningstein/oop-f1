"""
F1 25 Telemetry System - Telemetry Controller
Beheert de state en het opslaan van telemetrie data.
(Versie 9: Correcte snake_case attributen voor LapData)
"""

from services import logger_service
from typing import Optional, Dict, Any, List

# --- IMPORTS ---
from models.lap_model import LapModel
from models.session_model import SessionModel
from models.driver_model import DriverModel
from packet_parsers.lap_parser import LapData
from packet_parsers.history_parser import SessionHistoryData, LapHistoryData
from services.data_validator import data_validator


class TelemetryController:
    """
    Verwerkt specifieke data (zoals LapData) en roept de
    juiste models aan om de data op te slaan in de database.
    """

    def __init__(self):
        """Initialiseer de Telemetry Controller"""
        self.logger = logger_service.get_logger('TelemetryController')

        self.lap_model = LapModel()
        self.session_model = SessionModel()
        self.driver_model = DriverModel()
        self.validator = data_validator

        self.player_car_index: Optional[int] = None

        self.logger.info("Telemetry Controller geïnitialiseerd")

    def get_current_session_id(self) -> Optional[int]:
        """
        Pass-through methode om de View (screen1) toegang te geven
        tot de actieve session ID via het session_model.
        """
        return self.session_model.get_current_session_id()

    # --- FUNCTIES VOOR DE VIEW (DATA OPHALEN) ---

    def get_player_lap_data(self) -> Optional[Dict[str, Any]]:
        """
        Haalt de *meest recente* opgeslagen ronde data op voor de speler.
        """
        session_id = self.get_current_session_id()
        if session_id is None or self.player_car_index is None:
            return None

        try:
            all_laps = self.lap_model.get_laps_for_driver(session_id, self.player_car_index)

            if not all_laps:
                return None

            return all_laps[-1]

        except Exception as e:
            self.logger.error(f"Fout bij ophalen get_player_lap_data: {e}", exc_info=True)
            return None

    def get_player_lap_history(self) -> List[Dict[str, Any]]:
        """
        Haalt *alle* opgeslagen rondes op voor de speler.
        """
        session_id = self.get_current_session_id()

        if session_id is None:
            self.logger.debug("get_player_lap_history: Geen actieve sessie.")
            return []

        if self.player_car_index is None:
            self.logger.debug("get_player_lap_history: Player car index is nog onbekend.")
            return []

        try:
            all_laps = self.lap_model.get_laps_for_driver(session_id, self.player_car_index)
            return all_laps

        except Exception as e:
            self.logger.error(f"Fout bij ophalen get_player_lap_history: {e}", exc_info=True)
            return []

    # --- METHODES VOOR DATA OPSLAG (bestaand) ---

    def update_lap_data(self, lap_data: LapData, session_uid: int, car_index: int):
        """
        Ontvangt LapData (Packet 2) van de DataProcessor
        en slaat deze op in de database.
        """

        if self.player_car_index is None:
            self.player_car_index = car_index

        current_db_id = self._get_db_session_id(session_uid)

        if current_db_id is None:
            self.logger.warning(
                f"Ontving LapData (UID {session_uid}), maar sessie is nog niet in DB. Data wordt genegeerd.")
            return

        # --- HIER IS DE FIX (snake_case) ---
        # Gebruik de Python-attributen van de LapData dataclass
        lap_number_to_save = lap_data.current_lap_num - 1
        # --- EINDE FIX ---

        if lap_number_to_save <= 0:
            return

        try:
            # --- HIER IS DE FIX (snake_case) ---
            s1_ms = self._convert_sector_time(lap_data.sector1_time_minutes_part, lap_data.sector1_time_ms_part)
            s2_ms = self._convert_sector_time(lap_data.sector2_time_minutes_part, lap_data.sector2_time_ms_part)
            s3_ms = self._calculate_sector3(lap_data.last_lap_time_in_ms, s1_ms, s2_ms)

            lap_data_dict = {
                'session_id': current_db_id,
                'car_index': car_index,
                'lap_number': lap_number_to_save,
                'lap_time_ms': lap_data.last_lap_time_in_ms,
                'sector1_ms': s1_ms,
                'sector2_ms': s2_ms,
                'sector3_ms': s3_ms,
                'is_valid': not bool(lap_data.current_lap_invalid),
                'sector1_valid': s1_ms is not None,
                'sector2_valid': s2_ms is not None,
                'sector3_valid': s3_ms is not None,
            }
            # --- EINDE FIX ---

            if self.validator.validate_lap_data(lap_data_dict):
                self.lap_model.save_lap(lap_data_dict)
            else:
                self.logger.warning(f"Lap data (P2) faalde validatie: {lap_data_dict}")

        except Exception as e:
            self.logger.error(f"Fout bij opslaan lap data (P2): {e}", exc_info=True)

    def update_lap_validation(self, history_packet: SessionHistoryData, session_uid: int):
        """
        Ontvangt SessionHistory (Packet 11) en werkt de
        definitieve validatie-status bij in de database.
        (Deze functie was al correct en gebruikt snake_case)
        """
        current_db_id = self._get_db_session_id(session_uid)

        if current_db_id is None:
            self.logger.warning(
                f"Ontving History (UID {session_uid}), maar sessie is niet in DB. Data wordt genegeerd.")
            return

        car_index = history_packet.car_idx

        if self.player_car_index is None:
            # Aanname: de history is van de speler
            self.player_car_index = car_index

        self.logger.debug(f"Verwerken Packet 11 (History) voor auto {car_index} in sessie {current_db_id}")

        for i in range(history_packet.num_laps):
            lap_history: LapHistoryData = history_packet.lap_history_data[i]
            lap_number = i + 1  # Ronden zijn 1-based

            validation_dict = self.validator.parse_lap_validation_flags(
                lap_history.lap_valid_bit_flags
            )

            s1_ms = lap_history.get_sector1_total_ms()
            s2_ms = lap_history.get_sector2_total_ms()
            s3_ms = lap_history.get_sector3_total_ms()

            if s1_ms == 0: s1_ms = None
            if s2_ms == 0: s2_ms = None
            if s3_ms == 0: s3_ms = None

            try:
                lap_data_dict = {
                    'session_id': current_db_id,
                    'car_index': car_index,
                    'lap_number': lap_number,
                    'lap_time_ms': lap_history.lap_time_ms,
                    'sector1_ms': s1_ms,
                    'sector2_ms': s2_ms,
                    'sector3_ms': s3_ms,
                    'is_valid': validation_dict['is_valid'],
                    'sector1_valid': validation_dict['sector1_valid'],
                    'sector2_valid': validation_dict['sector2_valid'],
                    'sector3_valid': validation_dict['sector3_valid'],
                }

                self.lap_model.save_lap(lap_data_dict)

            except Exception as e:
                self.logger.error(f"Fout bij opslaan lap validatie (P11): {e}", exc_info=True)

    def _get_db_session_id(self, session_uid: int) -> Optional[int]:
        """
        Interne helper om de DB primary key (id) te krijgen
        van de session_uid (uit de packets).
        """
        session = self.session_model.get_session_by_uid(session_uid)
        if session:
            self.session_model.current_session_id = session['id']
            return session.get('id')

        current_id = self.session_model.get_current_session_id()
        if current_id:
            return current_id

        return None

    def _convert_sector_time(self, minutes: int, ms_part: int) -> Optional[int]:
        """Helper: Converteer F1 25 sector tijd (min + ms) naar pure MS"""
        if minutes == 255 or ms_part == 65535:
            return None
        total_ms = (minutes * 60 * 1000) + ms_part
        return total_ms if total_ms > 0 else None

    def _calculate_sector3(self, lap_ms: int, s1_ms: Optional[int], s2_ms: Optional[int]) -> Optional[int]:
        """Helper: Bereken S3 tijd (voor Packet 2)."""
        if lap_ms and s1_ms and s2_ms and lap_ms > 0 and (s1_ms + s2_ms) < lap_ms:
            return lap_ms - s1_ms - s2_ms
        return None