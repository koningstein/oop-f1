"""
F1 25 Telemetry System - Lap Model
Database operaties voor lap en sector tijden
"""

from typing import Optional, Dict, Any, List
from models.database import database
from services import logger_service


class LapModel:
    """Model voor lap data in database"""

    def __init__(self):
        """Initialiseer lap model"""
        self.logger = logger_service.get_logger('LapModel')
        self.db = database

    def save_lap(self, lap_data: Dict[str, Any]) -> bool:
        """
        Sla lap time op in database

        Args:
            lap_data: Dict met lap informatie
                - session_id
                - car_index
                - lap_number
                - lap_time_ms
                - sector1_ms, sector2_ms, sector3_ms
                - sector1_valid, sector2_valid, sector3_valid
                - is_valid

        Returns:
            True als succesvol
        """
        query = """
            INSERT INTO laps (
                session_id, car_index, lap_number, lap_time_ms,
                sector1_ms, sector2_ms, sector3_ms,
                sector1_valid, sector2_valid, sector3_valid, is_valid
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                lap_time_ms = VALUES(lap_time_ms),
                sector1_ms = VALUES(sector1_ms),
                sector2_ms = VALUES(sector2_ms),
                sector3_ms = VALUES(sector3_ms),
                sector1_valid = VALUES(sector1_valid),
                sector2_valid = VALUES(sector2_valid),
                sector3_valid = VALUES(sector3_valid),
                is_valid = VALUES(is_valid)
        """

        params = (
            lap_data.get('session_id'),
            lap_data.get('car_index'),
            lap_data.get('lap_number'),
            lap_data.get('lap_time_ms'),
            lap_data.get('sector1_ms'),
            lap_data.get('sector2_ms'),
            lap_data.get('sector3_ms'),
            lap_data.get('sector1_valid', True),
            lap_data.get('sector2_valid', True),
            lap_data.get('sector3_valid', True),
            lap_data.get('is_valid', True)
        )

        success = self.db.execute_query(query, params)

        if success:
            # --- AANGEPAST ---
            # Log level verhoogd van DEBUG naar INFO.
            # Dit is de melding die je wilde zien bij een succesvolle insert.
            self.logger.info(
                f"Database: Lap {lap_data.get('lap_number')} opgeslagen "
                f"(Car {lap_data.get('car_index')}, SessionID {lap_data.get('session_id')})"
            )
            # --- EINDE AANPASSING ---

        # Deze generieke log-aanroep behouden we,
        # 'execute_query' in database.py logt alleen errors, dus deze is nodig voor 'success'
        logger_service.log_database_operation("INSERT/UPDATE", "laps", success)
        return success

    def get_laps_for_driver(self, session_id: int, car_index: int) -> List[Dict[str, Any]]:
        """
        Haal alle laps op voor een driver in een sessie

        Args:
            session_id: Session ID
            car_index: Car index

        Returns:
            List met lap dicts
        """
        query = """
            SELECT * FROM laps 
            WHERE session_id = %s AND car_index = %s
            ORDER BY lap_number ASC
        """
        return self.db.fetch_all(query, (session_id, car_index))

    def get_best_lap(self, session_id: int, car_index: int) -> Optional[Dict[str, Any]]:
        """
        Haal beste lap tijd op voor een driver

        Args:
            session_id: Session ID
            car_index: Car index

        Returns:
            Lap dict met snelste tijd of None
        """
        query = """
            SELECT * FROM laps 
            WHERE session_id = %s AND car_index = %s AND is_valid = TRUE
            ORDER BY lap_time_ms ASC
            LIMIT 1
        """
        return self.db.fetch_one(query, (session_id, car_index))

    def get_best_sectors(self, session_id: int, car_index: int) -> Dict[str, Optional[int]]:
        """
        Haal beste sector tijden op voor een driver

        Args:
            session_id: Session ID
            car_index: Car index

        Returns:
            Dict met beste sector tijden
        """
        result = {
            'sector1': None,
            'sector2': None,
            'sector3': None
        }

        # Beste sector 1
        query = """
            SELECT MIN(sector1_ms) as best FROM laps
            WHERE session_id = %s AND car_index = %s AND sector1_valid = TRUE
        """
        s1 = self.db.fetch_one(query, (session_id, car_index))
        if s1 and s1['best']:
            result['sector1'] = s1['best']

        # Beste sector 2
        query = """
            SELECT MIN(sector2_ms) as best FROM laps
            WHERE session_id = %s AND car_index = %s AND sector2_valid = TRUE
        """
        s2 = self.db.fetch_one(query, (session_id, car_index))
        if s2 and s2['best']:
            result['sector2'] = s2['best']

        # Beste sector 3
        query = """
            SELECT MIN(sector3_ms) as best FROM laps
            WHERE session_id = %s AND car_index = %s AND sector3_valid = TRUE
        """
        s3 = self.db.fetch_one(query, (session_id, car_index))
        if s3 and s3['best']:
            result['sector3'] = s3['best']

        return result

    def get_session_leaderboard(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Haal leaderboard op voor een sessie (beste lap per driver)

        Args:
            session_id: Session ID

        Returns:
            List met driver best laps, gesorteerd op tijd
        """
        query = """
            SELECT 
                l.car_index,
                d.driver_name,
                d.team_id,
                MIN(l.lap_time_ms) as best_lap_time,
                l.lap_number
            FROM laps l
            LEFT JOIN drivers d ON l.session_id = d.session_id AND l.car_index = d.car_index
            WHERE l.session_id = %s AND l.is_valid = TRUE
            GROUP BY l.car_index
            ORDER BY best_lap_time ASC
        """
        return self.db.fetch_all(query, (session_id,))

    def get_lap_count(self, session_id: int, car_index: int) -> int:
        """
        Tel aantal laps voor een driver

        Args:
            session_id: Session ID
            car_index: Car index

        Returns:
            Aantal laps
        """
        query = """
            SELECT COUNT(*) as count FROM laps
            WHERE session_id = %s AND car_index = %s
        """
        result = self.db.fetch_one(query, (session_id, car_index))
        return result['count'] if result else 0