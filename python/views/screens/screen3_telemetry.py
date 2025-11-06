"""
F1 25 Telemetry System - Screen 3: Live Telemetrie
Real-time telemetrie data weergave
"""

import os
from models import SessionModel, DriverModel, TelemetryModel
from services import logger_service
from utils import format_speed, format_percentage

class Screen3Telemetry:
    """Scherm 3: Live Telemetrie"""
    
    def __init__(self, telemetry_controller):
        """
        Initialiseer telemetrie scherm
        
        Args:
            telemetry_controller: Referentie naar telemetry controller
        """
        self.logger = logger_service.get_logger('Screen3')
        self.telemetry_controller = telemetry_controller
        
        self.session_model = SessionModel()
        self.driver_model = DriverModel()
        self.telemetry_model = TelemetryModel()
    
    def render(self):
        """Render het telemetrie scherm"""
        self.clear_screen()
        
        print("=" * 80)
        print(" " * 23 + "SCHERM 3: LIVE TELEMETRIE")
        print("=" * 80)
        
        session_id = self.telemetry_controller.get_current_session_id()
        
        if not session_id:
            print("\n  Geen actieve sessie - wachten op telemetry data...")
            print("=" * 80)
            return
        
        player_car_index = self.telemetry_controller.player_car_index
        
        if player_car_index is None:
            print("\n  Geen speler data beschikbaar")
            print("=" * 80)
            return
        
        # Haal driver naam op
        driver = self.driver_model.get_driver(session_id, player_car_index)
        driver_name = driver.get('driver_name', 'Unknown') if driver else 'Unknown'
        
        print(f"\n  Driver: {driver_name}")
        print("")
        
        # Haal laatste telemetrie op
        telemetry = self.telemetry_model.get_latest_telemetry(session_id, player_car_index)
        
        if not telemetry:
            print("  Geen telemetrie data beschikbaar")
            print("  Wachten op Car Telemetry packets...")
            print("=" * 80)
            return
        
        self._render_telemetry(telemetry)
        
        print("=" * 80)
    
    def _render_telemetry(self, telemetry: dict):
        """
        Render telemetrie data
        
        Args:
            telemetry: Telemetry dict uit database
        """
        print("[ LIVE TELEMETRIE DATA ]")
        print("-" * 80)
        print("")
        
        # Snelheid
        speed = telemetry.get('speed', 0)
        print(f"  Snelheid:          {format_speed(speed)}")
        print("")
        
        # Motor
        rpm = telemetry.get('rpm', 0)
        gear = telemetry.get('gear', 0)
        gear_str = str(gear) if gear > 0 else 'R' if gear == -1 else 'N'
        
        print(f"  RPM:               {rpm:5d}")
        print(f"  Versnelling:       {gear_str:>5}")
        print("")
        
        # Inputs
        throttle = telemetry.get('throttle', 0)
        brake = telemetry.get('brake', 0)
        
        print(f"  Throttle:          {format_percentage(throttle)}")
        print(f"  Brake:             {format_percentage(brake)}")
        print("")
        
        # DRS
        drs = telemetry.get('drs', False)
        drs_str = "ACTIEF" if drs else "Inactief"
        print(f"  DRS:               {drs_str}")
        print("")
        
        # Visual bars voor throttle en brake
        self._render_input_bars(throttle, brake)
    
    def _render_input_bars(self, throttle: float, brake: float):
        """
        Render visuele bars voor throttle en brake
        
        Args:
            throttle: Throttle waarde (0.0 - 1.0)
            brake: Brake waarde (0.0 - 1.0)
        """
        print("[ INPUT VISUALISATIE ]")
        print("-" * 80)
        
        # Throttle bar
        throttle_blocks = int(throttle * 40)
        throttle_bar = "█" * throttle_blocks + "░" * (40 - throttle_blocks)
        print(f"  Throttle: [{throttle_bar}] {int(throttle * 100):3d}%")
        
        # Brake bar
        brake_blocks = int(brake * 40)
        brake_bar = "█" * brake_blocks + "░" * (40 - brake_blocks)
        print(f"  Brake:    [{brake_bar}] {int(brake * 100):3d}%")
        print("")
    
    def clear_screen(self):
        """Clear console scherm"""
        os.system('cls' if os.name == 'nt' else 'clear')