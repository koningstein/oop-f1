"""
F1 25 Telemetry System - Screen 5: Vergelijking
Vergelijk je prestaties met andere drivers
"""

import os
from models import SessionModel, DriverModel, LapModel
from services import logger_service
from utils import ms_to_time_string, ms_to_sector_string, format_gap

class Screen5Comparison:
    """Scherm 5: Vergelijking"""
    
    def __init__(self, telemetry_controller):
        """
        Initialiseer vergelijking scherm
        
        Args:
            telemetry_controller: Referentie naar telemetry controller
        """
        self.logger = logger_service.get_logger('Screen5')
        self.telemetry_controller = telemetry_controller
        
        self.session_model = SessionModel()
        self.driver_model = DriverModel()
        self.lap_model = LapModel()
    
    def render(self):
        """Render het vergelijking scherm"""
        self.clear_screen()
        
        print("=" * 80)
        print(" " * 25 + "SCHERM 5: VERGELIJKING")
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
        
        # Haal leaderboard op om leider te vinden
        leaderboard = self.lap_model.get_session_leaderboard(session_id)
        
        if not leaderboard or len(leaderboard) < 2:
            print("\n  Onvoldoende data voor vergelijking")
            print("  Meerdere drivers moeten een ronde hebben voltooid")
            print("=" * 80)
            return
        
        # Vind speler positie
        player_entry = None
        leader_entry = leaderboard[0]
        
        for entry in leaderboard:
            if entry['car_index'] == player_car_index:
                player_entry = entry
                break
        
        if not player_entry:
            print("\n  Geen lap tijden voor speler")
            print("=" * 80)
            return
        
        # Vergelijk met leider
        self._render_comparison(session_id, player_car_index, player_entry, 
                                leader_entry['car_index'], leader_entry)
        
        print("=" * 80)
    
    def _render_comparison(self, session_id: int, player_car: int, 
                          player_entry: dict, leader_car: int, leader_entry: dict):
        """
        Render vergelijking tussen speler en leider
        
        Args:
            session_id: Session ID
            player_car: Speler car index
            player_entry: Speler leaderboard entry
            leader_car: Leider car index
            leader_entry: Leider leaderboard entry
        """
        # Haal namen op
        player_driver = self.driver_model.get_driver(session_id, player_car)
        leader_driver = self.driver_model.get_driver(session_id, leader_car)
        
        player_name = player_driver.get('driver_name', 'You') if player_driver else 'You'
        leader_name = leader_driver.get('driver_name', 'Leader') if leader_driver else 'Leader'
        
        print(f"\n  Vergelijking: {player_name} vs {leader_name}")
        print("")
        
        # Beste lap vergelijking
        print("[ BESTE RONDETIJD ]")
        print("-" * 80)
        
        player_time = player_entry['best_lap_time']
        leader_time = leader_entry['best_lap_time']
        gap = player_time - leader_time
        
        print(f"  {player_name:<30} {ms_to_time_string(player_time)}")
        print(f"  {leader_name:<30} {ms_to_time_string(leader_time)}")
        print(f"  Verschil:                      {format_gap(gap)}")
        print("")
        
        # Sector vergelijking
        player_sectors = self.lap_model.get_best_sectors(session_id, player_car)
        leader_sectors = self.lap_model.get_best_sectors(session_id, leader_car)
        
        self._render_sector_comparison(player_name, leader_name, 
                                       player_sectors, leader_sectors)
        
        # Rondetelling
        player_laps = self.lap_model.get_lap_count(session_id, player_car)
        leader_laps = self.lap_model.get_lap_count(session_id, leader_car)
        
        print("[ AANTAL RONDES ]")
        print("-" * 80)
        print(f"  {player_name:<30} {player_laps:3d} rondes")
        print(f"  {leader_name:<30} {leader_laps:3d} rondes")
        print("")
    
    def _render_sector_comparison(self, player_name: str, leader_name: str,
                                  player_sectors: dict, leader_sectors: dict):
        """
        Render sector vergelijking
        
        Args:
            player_name: Naam van speler
            leader_name: Naam van leider
            player_sectors: Speler sector tijden
            leader_sectors: Leider sector tijden
        """
        print("[ BESTE SECTORTIJDEN ]")
        print("-" * 80)
        
        for sector_num in [1, 2, 3]:
            sector_key = f'sector{sector_num}'
            player_time = player_sectors.get(sector_key)
            leader_time = leader_sectors.get(sector_key)
            
            print(f"  Sector {sector_num}:")
            
            if player_time and leader_time:
                player_str = ms_to_sector_string(player_time)
                leader_str = ms_to_sector_string(leader_time)
                gap = player_time - leader_time
                gap_str = format_gap(gap)
                
                print(f"    {player_name:<28} {player_str:>10}")
                print(f"    {leader_name:<28} {leader_str:>10}")
                print(f"    Verschil: {gap_str:>10}")
            elif player_time:
                player_str = ms_to_sector_string(player_time)
                print(f"    {player_name:<28} {player_str:>10}")
                print(f"    {leader_name:<28} {'-.---':>10}")
            else:
                print(f"    Geen data beschikbaar")
            
            print("")
    
    def clear_screen(self):
        """Clear console scherm"""
        os.system('cls' if os.name == 'nt' else 'clear')