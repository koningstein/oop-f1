"""
F1 25 Telemetry System - Telemetry Model
Database operaties voor live telemetrie data
"""

from typing import Optional, Dict, Any, List
from models.database import database
from services import logger_service

class TelemetryModel:
    """Model voor live telemetry data in database"""
    
    def __init__(self):
        """Initialiseer telemetry model"""
        self.logger = logger_service.get_logger('TelemetryModel')
        self.db = database
    
    def save_telemetry(self, telemetry_data: Dict[str, Any]) -> bool:
        """
        Sla telemetrie snapshot op
        
        Args:
            telemetry_data: Dict met telemetrie informatie
                - session_id
                - car_index
                - speed
                - throttle
                - brake
                - gear
                - rpm
                - drs
        
        Returns:
            True als succesvol
        """
        query = """
            INSERT INTO telemetry_live (
                session_id, car_index, speed, throttle, brake, gear, rpm, drs
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            telemetry_data.get('session_id'),
            telemetry_data.get('car_index'),
            telemetry_data.get('speed'),
            telemetry_data.get('throttle'),
            telemetry_data.get('brake'),
            telemetry_data.get('gear'),
            telemetry_data.get('rpm'),
            telemetry_data.get('drs', False)
        )
        
        success = self.db.execute_query(query, params)
        return success
    
    def get_latest_telemetry(self, session_id: int, car_index: int) -> Optional[Dict[str, Any]]:
        """
        Haal meest recente telemetrie op voor een driver
        
        Args:
            session_id: Session ID
            car_index: Car index
            
        Returns:
            Telemetry dict of None
        """
        query = """
            SELECT * FROM telemetry_live
            WHERE session_id = %s AND car_index = %s
            ORDER BY recorded_at DESC
            LIMIT 1
        """
        return self.db.fetch_one(query, (session_id, car_index))
    
    def get_telemetry_history(
        self, 
        session_id: int, 
        car_index: int, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Haal recente telemetrie geschiedenis op
        
        Args:
            session_id: Session ID
            car_index: Car index
            limit: Aantal records
            
        Returns:
            List met telemetry dicts
        """
        query = """
            SELECT * FROM telemetry_live
            WHERE session_id = %s AND car_index = %s
            ORDER BY recorded_at DESC
            LIMIT %s
        """
        return self.db.fetch_all(query, (session_id, car_index, limit))
    
    def cleanup_old_telemetry(self, session_id: int, seconds: int = 300) -> bool:
        """
        Verwijder oude telemetrie data (ouder dan X seconden)
        
        Args:
            session_id: Session ID
            seconds: Leeftijd in seconden
            
        Returns:
            True als succesvol
        """
        query = """
            DELETE FROM telemetry_live
            WHERE session_id = %s 
            AND recorded_at < DATE_SUB(NOW(), INTERVAL %s SECOND)
        """
        
        success = self.db.execute_query(query, (session_id, seconds))
        
        if success:
            self.logger.debug(f"Oude telemetrie data opgeschoond voor sessie {session_id}")
        
        return success
    
    def get_all_latest_telemetry(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Haal meest recente telemetrie op voor alle drivers
        
        Args:
            session_id: Session ID
            
        Returns:
            List met telemetry dicts per driver
        """
        query = """
            SELECT t1.* FROM telemetry_live t1
            INNER JOIN (
                SELECT car_index, MAX(recorded_at) as max_time
                FROM telemetry_live
                WHERE session_id = %s
                GROUP BY car_index
            ) t2 ON t1.car_index = t2.car_index AND t1.recorded_at = t2.max_time
            WHERE t1.session_id = %s
            ORDER BY t1.car_index ASC
        """
        return self.db.fetch_all(query, (session_id, session_id))