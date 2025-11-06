"""
F1 25 Telemetry System - Menu Controller
Controller voor menu navigatie tussen schermen met submenu ondersteuning
"""

import time
from typing import Optional, Callable, Dict, List, Tuple
from services import logger_service

class MenuController:
    """
    Controller voor menu en scherm navigatie met hiërarchische submenu's
    """
    
    def __init__(self):
        """Initialiseer menu controller"""
        self.logger = logger_service.get_logger('MenuController')
        self.current_screen = 1
        self.current_submenu = None  # Geen submenu geselecteerd
        self.screens: Dict[int, Callable] = {}
        self.screen_submenu_functions: Dict[int, Dict[int, Tuple[str, Callable]]] = {}
        self.running = False
        self.in_submenu = False
        
        # Initialiseer submenu structuur
        self._init_submenu_structure()
        
        self.logger.info("Menu controller geïnitialiseerd")
    
    def _init_submenu_structure(self):
        """Initialiseer submenu structuur voor alle schermen"""
        self.submenu_options = {
            1: {  # Overzicht/Leaderboard/Toernooi
                1: ("Practice Mode", None),
                2: ("Race Mode", None), 
                3: ("Toernooi", None),
                4: ("Position Chart", None)
            },
            2: {  # Invoerscherm + Toernooi Beheer
                1: ("Student Registratie", None),
                2: ("Simulator Selectie", None),
                3: ("Sessie Beheer", None),
                4: ("Toernooi Setup", None)
            },
            3: {  # Realtime Data Auto 1
                1: ("Dashboard", None),
                2: ("Fuel & ERS Management", None),
                3: ("Damage Monitoring", None),
                4: ("Setup Vergelijking", None),
                5: ("Tyre Management", None),
                6: ("Advanced Telemetry", None)
            },
            4: {  # Realtime Data Auto 2
                1: ("Dashboard", None),
                2: ("Fuel & ERS Management", None),
                3: ("Damage Monitoring", None),
                4: ("Setup Vergelijking", None),
                5: ("Tyre Management", None),
                6: ("Advanced Telemetry", None),
                7: ("Switch naar Auto 1", None)
            },
            5: {  # Race Strategy & Tyre Management
                1: ("Lap Time Comparison", None),
                2: ("Tyre Strategy Dashboard", None),
                3: ("Position & Strategy Analysis", None)
            },
            6: {  # Live Track Map + Telemetrie
                1: ("Circuit Layout", None),
                2: ("Live Telemetrie Overlay", None),
                3: ("Corner Analysis", None),
                4: ("Corner-by-corner Vergelijking", None),
                5: ("Slip Analysis", None)
            }
        }
    
    def register_screen(self, screen_number: int, screen_function: Callable):
        """
        Registreer hoofdscherm functie
        
        Args:
            screen_number: Scherm nummer (1-6)
            screen_function: Functie die scherm rendert
        """
        if 1 <= screen_number <= 6:
            self.screens[screen_number] = screen_function
            self.logger.info(f"Hoofdscherm {screen_number} geregistreerd")
        else:
            self.logger.warning(f"Ongeldig scherm nummer: {screen_number}")
    
    def register_submenu_function(self, screen_number: int, submenu_number: int, function: Callable):
        """
        Registreer submenu functie
        
        Args:
            screen_number: Hoofdscherm nummer (1-6)
            submenu_number: Submenu nummer
            function: Functie die submenu functionaliteit implementeert
        """
        if screen_number not in self.screen_submenu_functions:
            self.screen_submenu_functions[screen_number] = {}
        
        if screen_number in self.submenu_options and submenu_number in self.submenu_options[screen_number]:
            name = self.submenu_options[screen_number][submenu_number][0]
            self.submenu_options[screen_number][submenu_number] = (name, function)
            self.logger.info(f"Submenu functie geregistreerd: Scherm {screen_number}.{submenu_number} - {name}")
        else:
            self.logger.warning(f"Ongeldig submenu: {screen_number}.{submenu_number}")
    
    def set_screen(self, screen_number: int) -> bool:
        """
        Switch naar ander scherm (toont submenu)
        
        Args:
            screen_number: Scherm nummer (1-6)
            
        Returns:
            True als succesvol
        """
        if not (1 <= screen_number <= 6):
            self.logger.warning(f"Ongeldig scherm nummer: {screen_number}")
            return False
        
        self.current_screen = screen_number
        self.current_submenu = None
        self.in_submenu = True  # Ga naar submenu modus
        self.logger.info(f"Gewisseld naar scherm {screen_number} submenu")
        return True
    
    def set_submenu(self, submenu_number: int) -> bool:
        """
        Selecteer submenu optie
        
        Args:
            submenu_number: Submenu nummer
            
        Returns:
            True als succesvol
        """
        if (self.current_screen in self.submenu_options and 
            submenu_number in self.submenu_options[self.current_screen]):
            
            self.current_submenu = submenu_number
            self.in_submenu = False  # Verlaat submenu modus, ga naar functie
            name = self.submenu_options[self.current_screen][submenu_number][0]
            self.logger.info(f"Submenu geselecteerd: {self.current_screen}.{submenu_number} - {name}")
            return True
        else:
            self.logger.warning(f"Ongeldig submenu: {self.current_screen}.{submenu_number}")
            return False
    
    def back_to_main_menu(self):
        """Ga terug naar hoofdmenu"""
        self.in_submenu = False
        self.current_submenu = None
        self.logger.info("Terug naar hoofdmenu")
    
    def back_to_submenu(self):
        """Ga terug naar submenu van huidig scherm"""
        self.in_submenu = True
        self.current_submenu = None
        self.logger.info(f"Terug naar submenu van scherm {self.current_screen}")
    
    def get_current_screen(self) -> int:
        """Verkrijg huidig scherm nummer"""
        return self.current_screen
    
    def get_current_submenu(self) -> Optional[int]:
        """Verkrijg huidig submenu nummer"""
        return self.current_submenu
    
    def is_in_submenu_mode(self) -> bool:
        """Check of we in submenu selectie modus zijn"""
        return self.in_submenu
    
    def render_current_screen(self):
        """Render het huidige scherm of submenu"""
        if self.in_submenu:
            # Toon submenu
            return  # Menu wordt getoond door MenuView
        elif self.current_submenu is not None:
            # Render geselecteerde submenu functie
            if (self.current_screen in self.submenu_options and 
                self.current_submenu in self.submenu_options[self.current_screen]):
                
                name, function = self.submenu_options[self.current_screen][self.current_submenu]
                if function:
                    try:
                        function()
                    except Exception as e:
                        self.logger.error(f"Fout bij renderen submenu {self.current_screen}.{self.current_submenu}: {e}")
                        print(f"[ERROR] Kon '{name}' niet laden: {e}")
                else:
                    print(f"\n[INFO] '{name}' functie nog niet geïmplementeerd")
                    print("Deze functionaliteit wordt binnenkort toegevoegd.")
        else:
            # Render hoofdscherm (fallback)
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
        OUDE METHODE - Compatibiliteit met bestaande code
        Toon menu opties (nu met submenu ondersteuning)
        
        Returns:
            Menu string
        """
        if self.in_submenu:
            return self.get_submenu_text()
        else:
            return self.get_main_menu_text()
    
    def get_main_menu_text(self) -> str:
        """
        Verkrijg hoofdmenu tekst met status per scherm
        
        Returns:
            Menu string
        """
        menu = "\n" + "="*80 + "\n"
        menu += "F1 25 TELEMETRY SYSTEM - HOOFDMENU\n"
        menu += "="*80 + "\n"
        
        screen_info = [
            (1, "Overzicht / Leaderboard / Toernooi", 4),
            (2, "Invoerscherm + Toernooi Beheer", 4),
            (3, "Realtime Data Auto 1", 6),
            (4, "Realtime Data Auto 2", 7),
            (5, "Race Strategy & Tyre Management", 3),
            (6, "Live Track Map + Telemetrie Vergelijking", 5)
        ]
        
        for screen_num, name, total_functions in screen_info:
            # Tel beschikbare functies
            available = 0
            if screen_num in self.submenu_options:
                for _, (_, function) in self.submenu_options[screen_num].items():
                    if function:
                        available += 1
            
            status = f"({available}/{total_functions} functies)"
            menu += f"{screen_num}. {name} {status}\n"
        
        menu += "-"*80 + "\n"
        menu += "0. Afsluiten\n"
        menu += "="*80 + "\n"
        
        return menu
    
    def get_submenu_text(self) -> str:
        """
        Verkrijg submenu tekst voor huidig scherm
        
        Returns:
            Submenu string
        """
        if self.current_screen not in self.submenu_options:
            return "Geen submenu beschikbaar"
        
        screen_names = {
            1: "Overzicht / Leaderboard / Toernooi",
            2: "Invoerscherm + Toernooi Beheer", 
            3: "Realtime Data Auto 1",
            4: "Realtime Data Auto 2",
            5: "Race Strategy & Tyre Management",
            6: "Live Track Map + Telemetrie"
        }
        
        menu = "\n" + "="*80 + "\n"
        menu += f"SUBMENU - {screen_names.get(self.current_screen, f'SCHERM {self.current_screen}')}\n"
        menu += "="*80 + "\n"
        
        options = self.submenu_options[self.current_screen]
        available_count = 0
        total_count = len(options)
        
        for num in sorted(options.keys()):
            name, function = options[num]
            if function:
                status = " ✅ BESCHIKBAAR"
                available_count += 1
            else:
                status = " ❌ NOG NIET BESCHIKBAAR"
            menu += f"{self.current_screen}.{num} {name}{status}\n"
        
        menu += "-"*80 + "\n"
        menu += f"Status: {available_count}/{total_count} functies beschikbaar\n"
        menu += "-"*80 + "\n"
        menu += "B. Terug naar hoofdmenu\n"
        menu += "0. Afsluiten\n"
        menu += "="*80 + "\n"
        
        return menu
    
    def handle_input(self, choice: str) -> bool:
        """
        Verwerk menu/submenu keuze
        
        Args:
            choice: Gebruiker input
            
        Returns:
            True om door te gaan, False om te stoppen
        """
        if choice.upper() == '0' or choice.upper() == 'Q':
            self.logger.info("Afsluiten gekozen")
            return False
        
        if choice.upper() == 'B':
            if self.current_submenu is not None:
                # Van functie terug naar submenu
                self.back_to_submenu()
            elif self.in_submenu:
                # Van submenu terug naar hoofdmenu
                self.back_to_main_menu()
            else:
                print("Al in hoofdmenu")
            return True
        
        if self.in_submenu:
            # Verwerk submenu keuze
            try:
                submenu_num = int(choice)
                if submenu_num in self.submenu_options.get(self.current_screen, {}):
                    # Check of functie beschikbaar is
                    name, function = self.submenu_options[self.current_screen][submenu_num]
                    if function:
                        self.set_submenu(submenu_num)
                    else:
                        self.logger.warning(f"Functie niet beschikbaar: {self.current_screen}.{submenu_num}")
                        print(f"\n❌ '{name}' is nog niet geïmplementeerd!")
                        print("Deze functionaliteit wordt binnenkort toegevoegd.")
                        time.sleep(2)  # Korte pause zodat gebruiker bericht kan lezen
                else:
                    self.logger.warning(f"Ongeldige submenu keuze: {choice}")
                    print(f"Ongeldige submenu keuze: {choice}")
            except ValueError:
                self.logger.warning(f"Ongeldige submenu input: {choice}")
                print("Voer een geldig submenu nummer in")
        else:
            # Verwerk hoofdmenu keuze
            try:
                screen_num = int(choice)
                if 1 <= screen_num <= 6:
                    self.set_screen(screen_num)
                else:
                    self.logger.warning(f"Ongeldige hoofdmenu keuze: {choice}")
                    print("Kies een nummer tussen 1 en 6, of 0 om af te sluiten")
            except ValueError:
                self.logger.warning(f"Ongeldige hoofdmenu input: {choice}")
                print("Voer een geldig nummer in")
        
        return True