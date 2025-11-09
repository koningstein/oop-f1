"""
F1 25 Telemetry System - Menu Controller
Beheert de menu navigatie, submenu's en de actieve 'live' status.
(Versie 2: Met 'is_live' logica)
"""
from typing import Dict, Callable, Tuple, Optional, Any
from services import logger_service
import time

class MenuController:
    """Beheert de menu navigatie en submenu's"""

    def __init__(self):
        self.logger = logger_service.get_logger('MenuController')
        self.screens: Dict[int, Callable] = {}
        self.screen_submenu_options: Dict[int, Dict[int, Tuple[str, Optional[Callable]]]] = {}

        self.current_screen: int = 1
        self.current_submenu: Optional[int] = None
        self.running: bool = False
        self.in_submenu: bool = False

        # --- NIEUW ---
        self.live_views = set()
        # --- EINDE NIEUW ---

        self._initialize_submenu_structure()
        self.logger.info("Menu controller geïnitialiseerd")

    def _initialize_submenu_structure(self):
        """Definieer de structuur van alle menu's"""
        self.screen_submenu_options = {
            1: {
                1: ("Practice Mode", None),
                2: ("Race Mode", None),
                3: ("Toernooi", None),
                4: ("Position Chart", None),
                5: ("Live Lap & Sector Times", None),
            },
            2: {
                # ... (andere schermen) ...
            },
            3: {
                1: ("Dashboard", None),
                2: ("Fuel & ERS Management", None),
            },
            # ... (andere schermen) ...
        }

    def register_screen(self, screen_number: int, render_function: Callable):
        """Registreer een hoofdscherm"""
        self.screens[screen_number] = render_function
        self.logger.info(f"Hoofdscherm {screen_number} geregistreerd")

    def register_submenu_function(self, screen_number: int, submenu_number: int,
                                  function: Callable, is_live: bool = False):
        """
        Registreer submenu functie en markeer 'live' status
        """
        if screen_number not in self.screen_submenu_options:
            self.screen_submenu_options[screen_number] = {}

        options = self.screen_submenu_options.get(screen_number, {})
        if submenu_number in options:
            name = options[submenu_number][0]
            self.screen_submenu_options[screen_number][submenu_number] = (name, function)
            self.logger.info(f"Submenu functie geregistreerd: Scherm {screen_number}.{submenu_number} - {name}")

            if is_live:
                self.live_views.add((screen_number, submenu_number))
                self.logger.info(f"  > Functie {screen_number}.{submenu_number} gemarkeerd als LIVE")
        else:
            self.logger.warning(f"Ongeldig submenu: {screen_number}.{submenu_number}")

    def get_submenu_options(self, screen_number: int) -> Dict[int, str]:
        """Haal de opties op voor het submenu van een scherm"""
        return {k: v[0] for k, v in self.screen_submenu_options.get(screen_number, {}).items()}

    def render_current_screen(self):
        """Render het huidige actieve scherm of functie"""
        if self.current_submenu is not None:
            # We zijn in een actieve functie (bv. 1.5)
            try:
                # Zoek de functie op
                name, func = self.screen_submenu_options[self.current_screen][self.current_submenu]
                if func:
                    func() # Roep de render() aan (bv. live_timing_view.render())
                else:
                    print(f"Functie {self.current_screen}.{self.current_submenu} niet gevonden.")
            except KeyError:
                print(f"Fout: Kan functie {self.current_screen}.{self.current_submenu} niet vinden.")
            except Exception as e:
                self.logger.error(f"Fout bij renderen functie {self.current_screen}.{self.current_submenu}: {e}", exc_info=True)
        else:
            # Render het hoofdscherm (overzicht)
            render_function = self.screens.get(self.current_screen)
            if render_function:
                render_function()

    def set_screen(self, screen_number: int):
        """Wissel naar een hoofdscherm en toon het submenu"""
        if screen_number in self.screens:
            self.current_screen = screen_number
            self.in_submenu = True
            self.current_submenu = None # We zijn nog niet in een functie
            self.logger.info(f"Gewisseld naar scherm {screen_number} submenu")
        else:
            self.logger.warning(f"Poging om naar ongeldig scherm {screen_number} te wisselen")

    def set_submenu(self, submenu_number: int):
        """Activeer een specifieke functie (bv. 1.5)"""
        options = self.screen_submenu_options.get(self.current_screen, {})
        if submenu_number in options:
            name, func = options[submenu_number]
            if func:
                self.current_submenu = submenu_number
                self.in_submenu = False # We zijn nu *in* de functie
                self.logger.info(f"Submenu geselecteerd: {self.current_screen}.{submenu_number} - {name}")
            else:
                self.logger.warning(f"Functie niet beschikbaar: {self.current_screen}.{submenu_number}")
                print(f"\n❌ '{name}' is nog niet geïmplementeerd!")
                time.sleep(2)
        else:
            self.logger.warning(f"Ongeldige submenu keuze: {submenu_number}")

    def handle_input(self, choice: str) -> bool:
        """Verwerk menu/submenu keuze"""
        if choice.upper() == '0' or choice.upper() == 'Q':
            self.logger.info("Afsluiten gekozen")
            return False

        if choice.upper() == 'B':
            if self.current_submenu is not None:
                self.back_to_submenu()
            elif self.in_submenu:
                self.back_to_main_menu()
            return True

        # 'R' wordt nu afgehandeld in de main.py loop
        if choice.upper() == 'R':
            return True

        if self.in_submenu:
            # Verwerk submenu keuze (bv. '5' kiezen in Scherm 1)
            try:
                self.set_submenu(int(choice))
            except ValueError:
                self.logger.warning(f"Ongeldige submenu input: {choice}")
                print("Voer een geldig submenu nummer in")
        else:
            # Verwerk hoofdmenu keuze (bv. '1' kiezen)
            try:
                screen_num = int(choice)
                if 1 <= screen_num <= 6:
                    self.set_screen(screen_num)
                else:
                    self.logger.warning(f"Ongeldige hoofdmenu keuze: {choice}")
            except ValueError:
                self.logger.warning(f"Ongeldige hoofdmenu input: {choice}")
                print("Voer een geldig nummer in")

        return True

    def back_to_submenu(self):
        """Ga van een functie (bv. 1.5) terug naar het submenu (bv. Scherm 1)"""
        self.current_submenu = None
        self.in_submenu = True

    def back_to_main_menu(self):
        """Ga van een submenu terug naar het hoofdmenu (1-6)"""
        self.in_submenu = False
        self.current_submenu = None

    def start(self):
        self.running = True
        self.logger.info("Menu controller gestart")

    def stop(self):
        self.running = False
        self.logger.info("Menu controller gestopt")

    # --- Helper methodes voor de View/Main loop ---
    def is_in_submenu_mode(self) -> bool:
        return self.in_submenu

    def get_current_screen(self) -> int:
        return self.current_screen

    def get_current_submenu(self) -> Optional[int]:
        return self.current_submenu

    def is_current_view_live(self) -> bool:
        """Checkt of de huidige geselecteerde functie (bv 1.5) een live-refresh view is."""
        if self.in_submenu or self.current_submenu is None:
            return False
        return (self.current_screen, self.current_submenu) in self.live_views