"""
F1 25 Telemetry System - Screen 2: Timing & Sectors
Gedetailleerde timing informatie met sectortijden
"""

import os
from models import SessionModel, DriverModel, LapModel
from services import logger_service
from utils import ms_to_time_string, ms_to_sector_string

class Screen2Timing:
    """Scherm 2: Timing & Sectors"""
    
    def __init__(self, telemetry_controller):
        """
        Initialiseer timing scherm
        
        Args:
            telemetry_controller: Referentie naar telemetry controller
        """
        self.logger = logger_service.get_logger('Screen2')
        self.telemetry_controller = telemetry_controller
        
        self.session_model = SessionModel()
        self.driver_model = DriverModel()
        self.lap_model = LapModel()
    
    def render(self):
        """Render het timing scherm"""
        self.clear_screen()
        
        print("=" * 80)
        print(" " * 22 + "SCHERM 2: TIMING & SECTORS")
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
        
        # Haal beste sectortijden op
        best_sectors = self.lap_model.get_best_sectors(session_id, player_car_index)
        self._render_best_sectors(best_sectors)
        
        # Haal alle laps op
        laps = self.lap_model.get_laps_for_driver(session_id, player_car_index)
        self._render_lap_times(laps)
        
        print("=" * 80)
    
    def _render_best_sectors(self, best_sectors: dict):
        """
        Render beste sectortijden
        
        Args:
            best_sectors: Dict met beste sector tijden
        """
        print("[ BESTE SECTORTIJDEN ]")
        print("-" * 80)
        
        s1 = ms_to_sector_string(best_sectors['sector1']) if best_sectors['sector1'] else "-.---"
        s2 = ms_to_sector_string(best_sectors['sector2']) if best_sectors['sector2'] else "-.---"
        s3 = ms_to_sector_string(best_sectors['sector3']) if best_sectors['sector3'] else "-.---"
        
        # Bereken theoretische beste lap
        if all(best_sectors.values()):
            theoretical = sum(best_sectors.values())
            theoretical_str = ms_to_time_string(theoretical)
        else:
            theoretical_str = "--:--.---"
        
        print(f"  Sector 1: {s1:>10}    Sector 2: {s2:>10}    Sector 3: {s3:>10}")
        print(f"  Theoretische Beste Ronde: {theoretical_str}")
        print("")
    
    def _render_lap_times(self, laps: list):
        """
        Render lap tijden tabel
        
        Args:
            laps: List met lap dicts
        """
        print("[ RONDETIJDEN ]")
        print("-" * 80)
        
        if not laps:
            print("  Nog geen rondetijden beschikbaar")
            return
        
        # Header
        print(f"  {'Ronde':<6} {'Tijd':<12} {'S1':<10} {'S2':<10} {'S3':<10} {'Valid':<6}")
        print("  " + "-" * 76)
        
        # Toon laatste 10 laps
        recent_laps = laps[-10:] if len(laps) > 10 else laps
        
        for lap in recent_laps:
            lap_num = lap['lap_number']
            lap_time = ms_to_time_string(lap['lap_time_ms'])
            s1 = ms_to_sector_string(lap['sector1_ms']) if lap['sector1_ms'] else "-.---"
            s2 = ms_to_sector_string(lap['sector2_ms']) if lap['sector2_ms'] else "-.---"
            s3 = ms_to_sector_string(lap['sector3_ms']) if lap['sector3_ms'] else "-.---"
            
            # Validatie markers
            s1_mark = "✓" if lap.get('sector1_valid') else "✗"
            s2_mark = "✓" if lap.get('sector2_valid') else "✗"
            s3_mark = "✓" if lap.get('sector3_valid') else "✗"
            valid_mark = "✓" if lap.get('is_valid') else "✗"
            
            # Kleur voor invalide lap (basis ASCII)
            prefix = "  "
            if not lap.get('is_valid'):
                prefix = "! "
            
            print(
                f"{prefix}{lap_num:<6} {lap_time:<12} "
                f"{s1:<8}{s1_mark} {s2:<8}{s2_mark} {s3:<8}{s3_mark} {valid_mark:<6}"
            )
        
        if len(laps) > 10:
            print(f"\n  (Toont laatste 10 van {len(laps)} rondes)")
    
    def clear_screen(self):
        """Clear console scherm"""
        os.system('cls' if os.name == 'nt' else 'clear')