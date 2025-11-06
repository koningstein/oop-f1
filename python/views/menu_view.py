"""
F1 25 Telemetry System - Menu View
Hoofdmenu weergave en navigatie
"""

import os
import time
from controllers import MenuController
from services import logger_service

class MenuView:
    """View voor het hoofdmenu"""
    
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
        """Toon hoofdmenu"""
        print(self.menu_controller.show_menu())
    
    def get_user_input(self) -> str:
        """
        Haal gebruiker input op
        
        Returns:
            Gebruiker keuze als string
        """
        return input("Kies een optie: ").strip()
    
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