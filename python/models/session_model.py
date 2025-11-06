"""
F1 25 Telemetry System - Session Model
Database operaties voor sessions
"""

from typing import Optional, Dict, Any
from datetime import datetime
from models.database import database
from services import logger_service

class SessionModel:
    """Model voor session data in database"""
    
    def __init__(self):
        """Initialiseer session model"""
        self.logger = logger_service.get_logger('SessionModel')
        self.db = database
        self.current_session_id: Optional[int] = None
    
    def create_session(self, session_data: Dict[str, Any]) -> Optional[int]:
        """
        Maak nieuwe sessie aan in database
        
        Args:
            session_data: Dict met session informatie
            
        Returns:
            Session ID of None bij fout
        """
        query = """
            INSERT INTO sessions (
                session_uid, track_id, session_type, weather,
                track_temperature, air_temperature, total_laps, session_duration
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            session_data.get('session_uid'),
            session_data.get('track_id'),
            session_data.get('session_type'),
            session_data.get('weather'),
            session_data.get('track_temperature'),
            session_data.get('air_temperature'),
            session_data.get('total_laps'),
            session_data.get('session_duration')
        )
        
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            
            session_id = cursor.lastrowid
            cursor.close()
            connection.close()
            
            self.current_session_id = session_id
            self.logger.info(f"Nieuwe sessie aangemaakt: ID {session_id}")
            logger_service.log_database_operation("INSERT", "sessions", True)
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"Fout bij aanmaken sessie: {e}")
            logger_service.log_database_operation("INSERT", "sessions", False)
            return None
    
    def get_session_by_uid(self, session_uid: int) -> Optional[Dict[str, Any]]:
        """
        Zoek sessie op basis van session_uid
        
        Args:
            session_uid: Unieke sessie identifier
            
        Returns:
            Session data dict of None
        """
        query = "SELECT * FROM sessions WHERE session_uid = %s"
        result = self.db.fetch_one(query, (session_uid,))
        
        if result:
            self.current_session_id = result['id']
        
        return result
    
    def get_or_create_session(self, session_uid: int, session_data: Dict[str, Any]) -> int:
        """
        Haal bestaande sessie op of maak nieuwe aan
        
        Args:
            session_uid: Unieke sessie identifier
            session_data: Session data voor nieuwe sessie
            
        Returns:
            Session ID
        """
        existing = self.get_session_by_uid(session_uid)
        
        if existing:
            return existing['id']
        
        return self.create_session(session_data)
    
    def update_session(self, session_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update sessie gegevens
        
        Args:
            session_id: ID van de sessie
            updates: Dict met te updaten velden
            
        Returns:
            True als succesvol
        """
        if not updates:
            return True
        
        # Bouw UPDATE query dynamisch
        set_clauses = [f"{key} = %s" for key in updates.keys()]
        query = f"UPDATE sessions SET {', '.join(set_clauses)} WHERE id = %s"
        params = tuple(updates.values()) + (session_id,)
        
        success = self.db.execute_query(query, params)
        logger_service.log_database_operation("UPDATE", "sessions", success)
        
        return success
    
    def end_session(self, session_id: int) -> bool:
        """
        Markeer sessie als beëindigd
        
        Args:
            session_id: ID van de sessie
            
        Returns:
            True als succesvol
        """
        query = "UPDATE sessions SET ended_at = NOW() WHERE id = %s"
        success = self.db.execute_query(query, (session_id,))
        
        if success:
            self.logger.info(f"Sessie {session_id} beëindigd")
        
        return success
    
    def get_current_session_id(self) -> Optional[int]:
        """
        Verkrijg huidige actieve session ID
        
        Returns:
            Session ID of None
        """
        return self.current_session_id
    
    def get_recent_sessions(self, limit: int = 10) -> list:
        """
        Haal recente sessies op
        
        Args:
            limit: Aantal sessies
            
        Returns:
            List met session dicts
        """
        query = """
            SELECT * FROM sessions 
            ORDER BY started_at DESC 
            LIMIT %s
        """
        return self.db.fetch_all(query, (limit,))