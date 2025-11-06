"""
F1 25 Telemetry System - Menu View
Hoofdmenu weergave en navigatie met submenu ondersteuning
"""

import os
import time
from controllers import MenuController
from services import logger_service

class MenuView:
    """View voor het hoofdmenu en submenu's"""
    
    def __init__(self, menu_controller: MenuController):
        """
        Initialiseer menu view
        
        Args:
            menu_controller: Menu controller instance
        """
        self.logger = logger_service.get_logger('MenuView')
        self.menu_controller = menu_controller
    
    def show_welcome(self):
        """Toon welkomst scherm"""
        self.clear_screen()
        print("=" * 80)
        print()
        print(" " * 20 + "F1 25 TELEMETRY SYSTEM")
        print(" " * 15 + "Techniek College Rotterdam")
        print()
        print("=" * 80)
        print()
        print("  Welkom bij het F1 25 Telemetry System!")
        print()
        print("  Dit systeem ontvangt live telemetry data van F1 25 en toont:")
        print("  - Rondetijden en sectortijden")
        print("  - Live telemetrie (snelheid, RPM, inputs)")
        print("  - Klassementen en vergelijkingen")
        print("  - Sessie historie")
        print()
        print("  Zorg dat UDP telemetry aan staat in F1 25:")
        print("  Game Options > Settings > Telemetry Settings")
        print("  - UDP Telemetry: On")
        print("  - UDP Port: 20777")
        print()
        print("=" * 80)
        print()
        input("  Druk op ENTER om te starten...")
    
    def show_menu(self):
        """
        OUDE METHODE - Behoud compatibiliteit 
        Toon juiste menu (hoofdmenu of submenu)
        """
        if self.menu_controller.is_in_submenu_mode():
            print(self.menu_controller.get_submenu_text())
        elif self.menu_controller.get_current_submenu() is not None:
            # Toon functie header
            screen = self.menu_controller.get_current_screen()
            submenu = self.menu_controller.get_current_submenu()
            name, _ = self.menu_controller.submenu_options[screen][submenu]
            
            print("\n" + "="*80)
            print(f"ACTIEF: SCHERM {screen}.{submenu} - {name.upper()}")
            print("="*80)
            print()
            print("Druk 'B' voor terug naar submenu, '0' voor afsluiten")
            print("-"*80)
        else:
            print(self.menu_controller.show_menu())  # Gebruik oude methode
    
    def get_user_input(self) -> str:
        """
        Haal gebruiker input op
        
        Returns:
            Gebruiker keuze als string
        """
        if self.menu_controller.is_in_submenu_mode():
            prompt = f"Kies submenu optie voor scherm {self.menu_controller.get_current_screen()}: "
        elif self.menu_controller.get_current_submenu() is not None:
            prompt = "Actie (B=terug, 0=quit): "
        else:
            prompt = "Kies een optie: "
        
        return input(prompt).strip()
    
    def show_status(self, udp_listener):
        """
        Toon status informatie
        
        Args:
            udp_listener: UDP listener instance
        """
        stats = udp_listener.get_stats()
        
        print("\n[ STATUS ]")
        print(f"  UDP Listener: {'ACTIEF' if stats['running'] else 'GESTOPT'}")
        print(f"  Packets ontvangen: {stats['packets_received']}")
        print(f"  Packets verwerkt: {stats['packets_processed']}")
        if stats['packets_errors'] > 0:
            print(f"  Errors: {stats['packets_errors']}")
        
        # Toon huidige navigatie status
        current_screen = self.menu_controller.get_current_screen()
        current_submenu = self.menu_controller.get_current_submenu()
        
        print(f"\n[ NAVIGATIE ]")
        print(f"  Huidig scherm: {current_screen}")
        
        if self.menu_controller.is_in_submenu_mode():
            print(f"  Status: In submenu selectie")
        elif current_submenu is not None:
            name, _ = self.menu_controller.submenu_options[current_screen][current_submenu]
            print(f"  Actieve functie: {current_screen}.{current_submenu} - {name}")
        else:
            print(f"  Status: Hoofdmenu")
    
    def show_error(self, message: str):
        """
        Toon error bericht
        
        Args:
            message: Error bericht
        """
        print(f"\n[ERROR] {message}\n")
    
    def show_info(self, message: str):
        """
        Toon info bericht
        
        Args:
            message: Info bericht
        """
        print(f"\n[INFO] {message}\n")
    
    def show_navigation_help(self):
        """Toon navigatie help"""
        print("\n" + "="*80)
        print("NAVIGATIE HULP")
        print("="*80)
        print("HOOFDMENU:")
        print("  1-6: Selecteer scherm (opent submenu)")
        print("  0/Q: Afsluiten")
        print()
        print("SUBMENU:")
        print("  1-7: Selecteer functie (afhankelijk van scherm)")
        print("  B: Terug naar hoofdmenu")
        print("  0: Afsluiten")
        print()
        print("IN FUNCTIE:")
        print("  B: Terug naar submenu")
        print("  0: Afsluiten")
        print("="*80)
    
    def clear_screen(self):
        """Clear console scherm"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def pause(self, seconds: float = 2.0):
        """
        Pauzeer voor X seconden
        
        Args:
            seconds: Aantal seconden
        """
        time.sleep(seconds)
    
    def show_submenu_details(self, screen_number: int):
        """
        Toon details van submenu voor een scherm
        
        Args:
            screen_number: Scherm nummer
        """
        if screen_number not in self.menu_controller.submenu_options:
            print(f"Geen submenu beschikbaar voor scherm {screen_number}")
            return
        
        screen_names = {
            1: "Overzicht / Leaderboard / Toernooi",
            2: "Invoerscherm + Toernooi Beheer",
            3: "Realtime Data Auto 1", 
            4: "Realtime Data Auto 2",
            5: "Race Strategy & Tyre Management",
            6: "Live Track Map + Telemetrie"
        }
        
        print(f"\n=== SCHERM {screen_number}: {screen_names.get(screen_number)} ===")
        
        options = self.menu_controller.submenu_options[screen_number]
        for num in sorted(options.keys()):
            name, function = options[num]
            status = "✓ BESCHIKBAAR" if function else "⚠ NOG NIET BESCHIKBAAR"
            print(f"  {screen_number}.{num} {name} - {status}")
        print()