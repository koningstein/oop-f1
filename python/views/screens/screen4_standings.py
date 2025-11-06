"""
F1 25 Telemetry System - Screen 4: Klassement
Leaderboard met alle drivers gesorteerd op beste lap tijd
"""

import os
from models import SessionModel, LapModel
from services import logger_service
from utils import ms_to_time_string, get_team_name

class Screen4Standings:
    """Scherm 4: Klassement"""
    
    def __init__(self, telemetry_controller):
        """
        Initialiseer klassement scherm
        
        Args:
            telemetry_controller: Referentie naar telemetry controller
        """
        self.logger = logger_service.get_logger('Screen4')
        self.telemetry_controller = telemetry_controller
        
        self.session_model = SessionModel()
        self.lap_model = LapModel()
    
    def render(self):
        """Render het klassement scherm"""
        self.clear_screen()
        
        print("=" * 80)
        print(" " * 26 + "SCHERM 4: KLASSEMENT")
        print("=" * 80)
        
        session_id = self.telemetry_controller.get_current_session_id()
        
        if not session_id:
            print("\n  Geen actieve sessie - wachten op telemetry data...")
            print("=" * 80)
            return
        
        # Haal leaderboard op
        leaderboard = self.lap_model.get_session_leaderboard(session_id)
        
        if not leaderboard:
            print("\n  Nog geen lap tijden beschikbaar")
            print("  Wachten op voltooide rondes...")
            print("=" * 80)
            return
        
        self._render_leaderboard(leaderboard)
        
        print("=" * 80)
    
    def _render_leaderboard(self, leaderboard: list):
        """
        Render leaderboard tabel
        
        Args:
            leaderboard: List met driver best laps
        """
        print("\n[ KLASSEMENT - BESTE RONDETIJDEN ]")
        print("-" * 80)
        print("")
        
        # Header
        print(f"  {'Pos':<5} {'Driver':<25} {'Team':<20} {'Beste Tijd':<12} {'Gap':<10}")
        print("  " + "-" * 76)
        
        # Bepaal beste tijd voor gap berekening
        best_time = leaderboard[0]['best_lap_time'] if leaderboard else 0
        
        for idx, entry in enumerate(leaderboard):
            position = idx + 1
            driver_name = entry.get('driver_name') or f"Driver {entry['car_index']}"
            team_id = entry.get('team_id', 0)
            team_name = get_team_name(team_id)
            best_lap_time = entry['best_lap_time']
            
            # Truncate lange namen
            if len(driver_name) > 24:
                driver_name = driver_name[:21] + "..."
            if len(team_name) > 19:
                team_name = team_name[:16] + "..."
            
            # Formatteer tijd
            time_str = ms_to_time_string(best_lap_time)
            
            # Bereken gap naar leider
            if position == 1:
                gap_str = "-"
            else:
                gap_ms = best_lap_time - best_time
                gap_seconds = gap_ms / 1000
                gap_str = f"+{gap_seconds:.3f}"
            
            # Highlight speler (als bekend)
            prefix = "  "
            player_car = self.telemetry_controller.player_car_index
            if player_car is not None and entry['car_index'] == player_car:
                prefix = "► "
            
            print(
                f"{prefix}{position:<5} {driver_name:<25} {team_name:<20} "
                f"{time_str:<12} {gap_str:<10}"
            )
        
        print("")
        print(f"  Totaal aantal drivers: {len(leaderboard)}")
    
    def clear_screen(self):
        """Clear console scherm"""
        os.system('cls' if os.name == 'nt' else 'clear')