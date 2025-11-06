"""
F1 25 Telemetry System - Screen 6: Sessie Historie
Overzicht van recente sessies en statistieken
"""

import os
from models import SessionModel, LapModel
from services import logger_service
from utils import (
    get_track_name, get_session_type_name, get_weather_name,
    ms_to_time_string
)
from datetime import datetime

class Screen6History:
    """Scherm 6: Sessie Historie"""
    
    def __init__(self, telemetry_controller):
        """
        Initialiseer historie scherm
        
        Args:
            telemetry_controller: Referentie naar telemetry controller
        """
        self.logger = logger_service.get_logger('Screen6')
        self.telemetry_controller = telemetry_controller
        
        self.session_model = SessionModel()
        self.lap_model = LapModel()
    
    def render(self):
        """Render het historie scherm"""
        self.clear_screen()
        
        print("=" * 80)
        print(" " * 23 + "SCHERM 6: SESSIE HISTORIE")
        print("=" * 80)
        
        # Haal recente sessies op
        sessions = self.session_model.get_recent_sessions(limit=10)
        
        if not sessions:
            print("\n  Nog geen sessies beschikbaar")
            print("  Start een sessie in F1 25 om data te verzamelen")
            print("=" * 80)
            return
        
        print("\n[ RECENTE SESSIES ]")
        print("-" * 80)
        
        # Header
        print(f"  {'#':<4} {'Datum/Tijd':<20} {'Circuit':<20} {'Type':<15} {'Status':<10}")
        print("  " + "-" * 76)
        
        for idx, session in enumerate(sessions):
            session_num = idx + 1
            
            # Datum/tijd
            started_at = session.get('started_at')
            if isinstance(started_at, datetime):
                dt_str = started_at.strftime('%d-%m-%Y %H:%M')
            else:
                dt_str = "Unknown"
            
            # Circuit
            track = get_track_name(session.get('track_id', 0))
            if len(track) > 19:
                track = track[:16] + "..."
            
            # Type
            session_type = get_session_type_name(session.get('session_type', 0))
            if len(session_type) > 14:
                session_type = session_type[:11] + "..."
            
            # Status
            ended_at = session.get('ended_at')
            status = "Voltooid" if ended_at else "Actief"
            
            print(f"  {session_num:<4} {dt_str:<20} {track:<20} {session_type:<15} {status:<10}")
        
        print("")
        
        # Toon details van meest recente sessie
        if sessions:
            self._render_session_details(sessions[0])
        
        print("=" * 80)
    
    def _render_session_details(self, session: dict):
        """
        Render details van een sessie
        
        Args:
            session: Session dict
        """
        print("[ DETAILS MEEST RECENTE SESSIE ]")
        print("-" * 80)
        
        session_id = session['id']
        
        # Basis info
        track = get_track_name(session.get('track_id', 0))
        session_type = get_session_type_name(session.get('session_type', 0))
        weather = get_weather_name(session.get('weather', 0))
        
        print(f"  Circuit:           {track}")
        print(f"  Sessie Type:       {session_type}")
        print(f"  Weer:              {weather}")
        
        # Haal leaderboard op voor deze sessie
        leaderboard = self.lap_model.get_session_leaderboard(session_id)
        
        if leaderboard:
            print(f"  Aantal drivers:    {len(leaderboard)}")
            
            # Snelste lap
            fastest = leaderboard[0]
            fastest_name = fastest.get('driver_name', 'Unknown')
            fastest_time = ms_to_time_string(fastest['best_lap_time'])
            
            print(f"  Snelste lap:       {fastest_time} ({fastest_name})")
        else:
            print(f"  Nog geen lap data")
        
        print("")
    
    def clear_screen(self):
        """Clear console scherm"""
        os.system('cls' if os.name == 'nt' else 'clear')