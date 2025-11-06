"""
F1 25 Telemetry System - Menu Controller
Controller voor menu navigatie tussen schermen
"""

from typing import Optional, Callable, Dict
from services import logger_service

class MenuController:
    """
    Controller voor menu en scherm navigatie
    """
    
    def __init__(self):
        """Initialiseer menu controller"""
        self.logger = logger_service.get_logger('MenuController')
        self.current_screen = 1
        self.screens: Dict[int, Callable] = {}
        self.running = False
        
        self.logger.info("Menu controller geïnitialiseerd")
    
    def register_screen(self, screen_number: int, screen_function: Callable):
        """
        Registreer scherm functie
        
        Args:
            screen_number: Scherm nummer (1-6)
            screen_function: Functie die scherm rendert
        """
        if 1 <= screen_number <= 6:
            self.screens[screen_number] = screen_function
            self.logger.info(f"Scherm {screen_number} geregistreerd")
        else:
            self.logger.warning(f"Ongeldig scherm nummer: {screen_number}")
    
    def set_screen(self, screen_number: int) -> bool:
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
        
        self.current_screen = screen_number
        self.logger.info(f"Gewisseld naar scherm {screen_number}")
        return True
    
    def get_current_screen(self) -> int:
        """
        Verkrijg huidig scherm nummer
        
        Returns:
            Scherm nummer
        """
        return self.current_screen
    
    def render_current_screen(self):
        """Render het huidige scherm"""
        if self.current_screen in self.screens:
            try:
                self.screens[self.current_screen]()
            except Exception as e:
                self.logger.error(f"Fout bij renderen scherm {self.current_screen}: {e}")
        else:
            self.logger.warning(f"Geen scherm functie voor scherm {self.current_screen}")
    
    def start(self):
        """Start menu controller"""
        self.running = True
        self.logger.info("Menu controller gestart")
    
    def stop(self):
        """Stop menu controller"""
        self.running = False
        self.logger.info("Menu controller gestopt")
    
    def is_running(self) -> bool:
        """Check of controller actief is"""
        return self.running
    
    def show_menu(self) -> str:
        """
        Toon menu opties
        
        Returns:
            Menu string
        """
        menu = "\n" + "="*60 + "\n"
        menu += "F1 25 TELEMETRY SYSTEM - MENU\n"
        menu += "="*60 + "\n"
        menu += f"Huidig scherm: {self.current_screen}\n"
        menu += "-"*60 + "\n"
        menu += "1. Overzicht\n"
        menu += "2. Timing & Sectors\n"
        menu += "3. Live Telemetrie\n"
        menu += "4. Klassement\n"
        menu += "5. Vergelijking\n"
        menu += "6. Sessie Historie\n"
        menu += "-"*60 + "\n"
        menu += "0. Afsluiten\n"
        menu += "="*60 + "\n"
        
        return menu
    
    def handle_input(self, choice: str) -> bool:
        """
        Verwerk menu keuze
        
        Args:
            choice: Gebruiker input
            
        Returns:
            True om door te gaan, False om te stoppen
        """
        if choice == '0':
            self.logger.info("Afsluiten gekozen")
            return False
        
        try:
            screen_num = int(choice)
            if 1 <= screen_num <= 6:
                self.set_screen(screen_num)
            else:
                self.logger.warning(f"Ongeldige keuze: {choice}")
                print("Kies een nummer tussen 1 en 6, of 0 om af te sluiten")
        except ValueError:
            self.logger.warning(f"Ongeldige input: {choice}")
            print("Voer een geldig nummer in")
        
        return True