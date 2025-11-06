"""
F1 25 Telemetry System - Screen 1: Overzicht
Algemeen overzicht van sessie status en live data
"""

import os
from typing import Optional
from models import SessionModel, DriverModel, LapModel
from services import logger_service
from utils import (
    get_track_name, get_session_type_name, get_weather_name,
    ms_to_time_string, format_temperature
)

class Screen1Overview:
    """Scherm 1: Overzicht"""
    
    def __init__(self, telemetry_controller):
        """
        Initialiseer overzicht scherm
        
        Args:
            telemetry_controller: Referentie naar telemetry controller
        """
        self.logger = logger_service.get_logger('Screen1')
        self.telemetry_controller = telemetry_controller
        
        self.session_model = SessionModel()
        self.driver_model = DriverModel()
        self.lap_model = LapModel()
    
    def render(self):
        """Render het overzicht scherm"""
        self.clear_screen()
        
        print("=" * 80)
        print(" " * 25 + "SCHERM 1: OVERZICHT")
        print("=" * 80)
        
        session_id = self.telemetry_controller.get_current_session_id()
        
        if not session_id:
            print("\n  Geen actieve sessie")
            print("  Wachten op telemetry data van F1 25...")
            print("\n  Zorg dat UDP telemetry aan staat in de game!")
            print("=" * 80)
            return
        
        # Haal sessie info op
        session = self.session_model.get_session_by_uid(
            self.telemetry_controller.session_model.current_session_id
        )
        
        if session:
            self._render_session_info(session)
        
        # Haal driver info op
        player_car_index = self.telemetry_controller.player_car_index
        if player_car_index is not None:
            driver = self.driver_model.get_driver(session_id, player_car_index)
            if driver:
                self._render_driver_info(driver, session_id, player_car_index)
        
        print("=" * 80)
    
    def _render_session_info(self, session: dict):
        """
        Render sessie informatie
        
        Args:
            session: Session dict uit database
        """
        print("\n[ SESSIE INFORMATIE ]")
        print("-" * 80)
        
        track = get_track_name(session.get('track_id', 0))
        session_type = get_session_type_name(session.get('session_type', 0))
        weather = get_weather_name(session.get('weather', 0))
        
        print(f"  Circuit:           {track}")
        print(f"  Sessie Type:       {session_type}")
        print(f"  Weer:              {weather}")
        print(f"  Track Temp:        {format_temperature(session.get('track_temperature', 0))}")
        print(f"  Lucht Temp:        {format_temperature(session.get('air_temperature', 0))}")
        
        if session.get('total_laps'):
            print(f"  Totaal Ronden:     {session.get('total_laps')}")
        
        print("")
    
    def _render_driver_info(self, driver: dict, session_id: int, car_index: int):
        """
        Render driver informatie
        
        Args:
            driver: Driver dict
            session_id: Session ID
            car_index: Car index
        """
        print("[ DRIVER INFORMATIE ]")
        print("-" * 80)
        
        print(f"  Naam:              {driver.get('driver_name', 'Unknown')}")
        print(f"  Race Nummer:       {driver.get('race_number', 0)}")
        
        # Haal lap statistieken op
        lap_count = self.lap_model.get_lap_count(session_id, car_index)
        best_lap = self.lap_model.get_best_lap(session_id, car_index)
        
        print(f"  Gereden Ronden:    {lap_count}")
        
        if best_lap:
            best_time = ms_to_time_string(best_lap['lap_time_ms'])
            print(f"  Beste Ronde:       {best_time} (Ronde {best_lap['lap_number']})")
        else:
            print(f"  Beste Ronde:       --:--.---")
        
        print("")
    
    def clear_screen(self):
        """Clear console scherm"""
        os.system('cls' if os.name == 'nt' else 'clear')