"""
F1 25 Telemetry System - Session Controller
Controller voor sessie lifecycle management
"""

from typing import Optional, Dict, Any
from models import SessionModel, DriverModel, LapModel
from services import logger_service
from packet_parsers import SessionData

class SessionController:
    """
    Controller voor sessie management
    Beheert sessie lifecycle en state
    """
    
    def __init__(self):
        """Initialiseer session controller"""
        self.logger = logger_service.get_logger('SessionController')
        
        self.session_model = SessionModel()
        self.driver_model = DriverModel()
        self.lap_model = LapModel()
        
        self.current_session_uid: Optional[int] = None
        self.current_session_id: Optional[int] = None
        self.session_active = False
        
        self.logger.info("Session controller geïnitialiseerd")
    
    def start_session(self, session_uid: int, session_data: SessionData) -> int:
        """
        Start nieuwe sessie of heractiveer bestaande
        
        Args:
            session_uid: Unieke sessie identifier
            session_data: Session packet data
            
        Returns:
            Session ID
        """
        # Check of sessie al bestaat
        existing = self.session_model.get_session_by_uid(session_uid)
        
        if existing:
            self.logger.info(f"Bestaande sessie heractiveerd: {session_uid}")
            self.current_session_id = existing['id']
            self.current_session_uid = session_uid
            self.session_active = True
            return existing['id']
        
        # Maak nieuwe sessie
        session_dict = {
            'session_uid': session_uid,
            'track_id': session_data.track_id,
            'session_type': session_data.session_type,
            'weather': session_data.weather,
            'track_temperature': session_data.track_temperature,
            'air_temperature': session_data.air_temperature,
            'total_laps': session_data.total_laps,
            'session_duration': session_data.session_duration
        }
        
        session_id = self.session_model.create_session(session_dict)
        
        if session_id:
            self.current_session_id = session_id
            self.current_session_uid = session_uid
            self.session_active = True
            self.logger.info(
                f"Nieuwe sessie gestart: ID {session_id}, "
                f"UID {session_uid}, Track {session_data.track_id}"
            )
        else:
            self.logger.error("Kon sessie niet aanmaken")
        
        return session_id
    
    def update_session(self, session_data: SessionData):
        """
        Update huidige sessie informatie
        
        Args:
            session_data: Session packet data
        """
        if not self.current_session_id:
            self.logger.warning("Geen actieve sessie om te updaten")
            return
        
        # Update alleen specifieke velden die kunnen wijzigen
        updates = {
            'weather': session_data.weather,
            'track_temperature': session_data.track_temperature,
            'air_temperature': session_data.air_temperature
        }
        
        self.session_model.update_session(self.current_session_id, updates)
    
    def end_session(self):
        """Beëindig huidige sessie"""
        if not self.current_session_id:
            self.logger.warning("Geen actieve sessie om te beëindigen")
            return
        
        self.session_model.end_session(self.current_session_id)
        
        self.logger.info(f"Sessie beëindigd: ID {self.current_session_id}")
        
        self.session_active = False
        self.current_session_id = None
        self.current_session_uid = None
    
    def get_session_id(self) -> Optional[int]:
        """
        Verkrijg huidige session ID
        
        Returns:
            Session ID of None
        """
        return self.current_session_id
    
    def is_session_active(self) -> bool:
        """
        Check of er een actieve sessie is
        
        Returns:
            True als sessie actief is
        """
        return self.session_active
    
    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """
        Verkrijg informatie over huidige sessie
        
        Returns:
            Session dict of None
        """
        if not self.current_session_uid:
            return None
        
        return self.session_model.get_session_by_uid(self.current_session_uid)
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """
        Verkrijg statistieken van huidige sessie
        
        Returns:
            Dict met statistieken
        """
        if not self.current_session_id:
            return {
                'active': False,
                'total_drivers': 0,
                'total_laps': 0
            }
        
        # Haal leaderboard op
        leaderboard = self.lap_model.get_session_leaderboard(self.current_session_id)
        
        # Tel totaal aantal laps
        total_laps = 0
        for entry in leaderboard:
            lap_count = self.lap_model.get_lap_count(
                self.current_session_id, 
                entry['car_index']
            )
            total_laps += lap_count
        
        return {
            'active': self.session_active,
            'session_id': self.current_session_id,
            'total_drivers': len(leaderboard),
            'total_laps': total_laps,
            'fastest_lap': leaderboard[0] if leaderboard else None
        }
    
    def cleanup_session_data(self):
        """Ruim oude sessie data op"""
        # Optioneel: implementeer cleanup van oude telemetrie data
        pass