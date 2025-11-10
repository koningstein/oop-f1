"""
F1 25 Telemetry System - Driver Model
Database operaties voor driver/participant data
"""

from typing import Optional, Dict, Any, List
from models.database import database
from services import logger_service

class DriverModel:
    """Model voor driver data in database"""
    
    def __init__(self):
        """Initialiseer driver model"""
        self.logger = logger_service.get_logger('DriverModel')
        self.db = database
    
    def save_driver(self, driver_data: Dict[str, Any]) -> bool:
        """
        Sla driver op in database (UPSERT)
        
        Args:
            driver_data: Dict met driver informatie
                - session_id
                - car_index
                - driver_name
                - team_id
                - race_number
                - nationality
                - is_player
        
        Returns:
            True als succesvol
        """
        query = """
            INSERT INTO drivers (
                session_id, car_index, driver_name, team_id,
                race_number, nationality, is_player
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                driver_name = VALUES(driver_name),
                team_id = VALUES(team_id),
                race_number = VALUES(race_number),
                nationality = VALUES(nationality),
                is_player = VALUES(is_player)
        """
        
        params = (
            driver_data.get('session_id'),
            driver_data.get('car_index'),
            driver_data.get('driver_name', ''),
            driver_data.get('team_id'),
            driver_data.get('race_number'),
            driver_data.get('nationality'),
            driver_data.get('is_player', False)
        )
        
        success = self.db.execute_query(query, params)
        
        if success:
            self.logger.debug(
                f"Driver opgeslagen: {driver_data.get('driver_name')} "
                f"(Car {driver_data.get('car_index')})"
            )
        
        logger_service.log_database_operation("INSERT/UPDATE", "drivers", success)
        return success
    
    def get_driver(self, session_id: int, car_index: int) -> Optional[Dict[str, Any]]:
        """
        Haal driver op
        
        Args:
            session_id: Session ID
            car_index: Car index
            
        Returns:
            Driver dict of None
        """
        query = """
            SELECT * FROM drivers
            WHERE session_id = %s AND car_index = %s
        """
        return self.db.fetch_one(query, (session_id, car_index))
    
    def get_all_drivers(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Haal alle drivers in een sessie op
        
        Args:
            session_id: Session ID
            
        Returns:
            List met driver dicts
        """
        query = """
            SELECT * FROM drivers
            WHERE session_id = %s
            ORDER BY car_index ASC
        """
        return self.db.fetch_all(query, (session_id,))
    
    def get_player_driver(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        Haal speler driver op
        
        Args:
            session_id: Session ID
            
        Returns:
            Driver dict of None
        """
        query = """
            SELECT * FROM drivers
            WHERE session_id = %s AND is_player = TRUE
            LIMIT 1
        """
        return self.db.fetch_one(query, (session_id,))
    
    def get_driver_name(self, session_id: int, car_index: int) -> str:
        """
        Haal driver naam op
        
        Args:
            session_id: Session ID
            car_index: Car index
            
        Returns:
            Driver naam of "Unknown"
        """
        driver = self.get_driver(session_id, car_index)
        if driver and driver.get('driver_name'):
            return driver['driver_name']
        return f"Driver {car_index}"
    
    def update_driver(self, session_id: int, car_index: int, updates: Dict[str, Any]) -> bool:
        """
        Update driver gegevens
        
        Args:
            session_id: Session ID
            car_index: Car index
            updates: Dict met te updaten velden
            
        Returns:
            True als succesvol
        """
        if not updates:
            return True
        
        set_clauses = [f"{key} = %s" for key in updates.keys()]
        query = f"""
            UPDATE drivers 
            SET {', '.join(set_clauses)}
            WHERE session_id = %s AND car_index = %s
        """
        params = tuple(updates.values()) + (session_id, car_index)
        
        success = self.db.execute_query(query, params)
        logger_service.log_database_operation("UPDATE", "drivers", success)
        
        return success