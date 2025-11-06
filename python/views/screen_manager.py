"""
F1 25 Telemetry System - Screen Manager
Beheert alle schermen en navigatie
"""

import time
from typing import Dict, Callable, Optional
from services import logger_service

class ScreenManager:
    """
    Screen manager voor beheer van alle schermen
    Centrale plek voor scherm registratie en rendering
    """
    
    def __init__(self):
        """Initialiseer screen manager"""
        self.logger = logger_service.get_logger('ScreenManager')
        
        # Scherm registratie
        self.screens: Dict[int, Callable] = {}
        self.screen_names: Dict[int, str] = {}
        
        # State
        self.current_screen = 1
        self.previous_screen = 1
        self.auto_refresh = False
        self.refresh_interval = 2.0  # seconden
        
        self.logger.info("Screen manager geïnitialiseerd")
    
    def register_screen(self, screen_number: int, screen_function: Callable, 
                       screen_name: str = ""):
        """
        Registreer scherm
        
        Args:
            screen_number: Scherm nummer (1-6)
            screen_function: Functie die scherm rendert
            screen_name: Optionele naam voor scherm
        """
        if not 1 <= screen_number <= 6:
            self.logger.warning(f"Ongeldig scherm nummer: {screen_number}")
            return False
        
        self.screens[screen_number] = screen_function
        
        if screen_name:
            self.screen_names[screen_number] = screen_name
        
        self.logger.info(f"Scherm {screen_number} geregistreerd: {screen_name}")
        return True
    
    def switch_screen(self, screen_number: int) -> bool:
        """
        Switch naar ander scherm
        
        Args:
            screen_number: Scherm nummer (1-6)
            
        Returns:
            True als succesvol
        """
        if screen_number not in self.screens:
            self.logger.warning(f"Scherm {screen_number} niet geregistreerd")
            return False
        
        self.previous_screen = self.current_screen
        self.current_screen = screen_number
        
        self.logger.info(f"Gewisseld naar scherm {screen_number}")
        return True
    
    def go_back(self) -> bool:
        """
        Ga terug naar vorige scherm
        
        Returns:
            True als succesvol
        """
        return self.switch_screen(self.previous_screen)
    
    def render_current_screen(self):
        """Render het huidige scherm"""
        if self.current_screen not in self.screens:
            self.logger.error(f"Kan scherm {self.current_screen} niet renderen")
            print(f"\n[ERROR] Scherm {self.current_screen} niet beschikbaar\n")
            return
        
        try:
            # Roep scherm functie aan
            self.screens[self.current_screen]()
        except Exception as e:
            self.logger.error(f"Fout bij renderen scherm {self.current_screen}: {e}")
            print(f"\n[ERROR] Fout bij weergeven scherm: {e}\n")
    
    def get_current_screen_number(self) -> int:
        """
        Verkrijg huidig scherm nummer
        
        Returns:
            Scherm nummer
        """
        return self.current_screen
    
    def get_current_screen_name(self) -> str:
        """
        Verkrijg naam van huidig scherm
        
        Returns:
            Scherm naam
        """
        return self.screen_names.get(self.current_screen, f"Scherm {self.current_screen}")
    
    def get_available_screens(self) -> Dict[int, str]:
        """
        Verkrijg lijst van beschikbare schermen
        
        Returns:
            Dict met {nummer: naam}
        """
        result = {}
        for screen_num in sorted(self.screens.keys()):
            name = self.screen_names.get(screen_num, f"Scherm {screen_num}")
            result[screen_num] = name
        
        return result
    
    def set_auto_refresh(self, enabled: bool, interval: float = 2.0):
        """
        Zet auto-refresh aan/uit
        
        Args:
            enabled: Auto-refresh aan (True) of uit (False)
            interval: Refresh interval in seconden
        """
        self.auto_refresh = enabled
        self.refresh_interval = interval
        
        status = "aan" if enabled else "uit"
        self.logger.info(f"Auto-refresh {status} (interval: {interval}s)")
    
    def is_auto_refresh_enabled(self) -> bool:
        """
        Check of auto-refresh aan staat
        
        Returns:
            True als aan
        """
        return self.auto_refresh
    
    def get_refresh_interval(self) -> float:
        """
        Verkrijg refresh interval
        
        Returns:
            Interval in seconden
        """
        return self.refresh_interval
    
    def render_screen_menu(self) -> str:
        """
        Genereer menu tekst met beschikbare schermen
        
        Returns:
            Menu string
        """
        menu = "\n" + "=" * 80 + "\n"
        menu += "SCHERM MENU\n"
        menu += "=" * 80 + "\n"
        
        # Toon beschikbare schermen
        for screen_num in sorted(self.screens.keys()):
            name = self.screen_names.get(screen_num, f"Scherm {screen_num}")
            current = " ◄ HUIDIG" if screen_num == self.current_screen else ""
            menu += f"{screen_num}. {name}{current}\n"
        
        menu += "-" * 80 + "\n"
        menu += "0. Afsluiten\n"
        menu += "R. Toggle auto-refresh"
        
        if self.auto_refresh:
            menu += f" (AAN - {self.refresh_interval}s)\n"
        else:
            menu += " (UIT)\n"
        
        menu += "=" * 80 + "\n"
        
        return menu
    
    def validate_screen_number(self, screen_number: int) -> bool:
        """
        Valideer of scherm nummer geldig is
        
        Args:
            screen_number: Te valideren scherm nummer
            
        Returns:
            True als geldig
        """
        return screen_number in self.screens
    
    def get_screen_count(self) -> int:
        """
        Verkrijg aantal geregistreerde schermen
        
        Returns:
            Aantal schermen
        """
        return len(self.screens)
    
    def clear_all_screens(self):
        """Verwijder alle geregistreerde schermen"""
        self.screens.clear()
        self.screen_names.clear()
        self.current_screen = 1
        self.logger.info("Alle schermen gewist")
    
    def render_navigation_help(self):
        """Render navigatie help tekst"""
        print("\n" + "-" * 80)
        print("NAVIGATIE:")
        print("  1-6: Wissel naar scherm")
        print("  0/Q: Afsluiten")
        print("  R: Toggle auto-refresh")
        print("-" * 80 + "\n")