"""
F1 25 Telemetry System - Main Application
Techniek College Rotterdam - Software Developer MBO-4

Hoofdprogramma voor F1 25 telemetry systeem met submenu ondersteuning
Start alle componenten en runt de main loop
"""

import sys
import time
from services import logger_service, UDPListener
from controllers import TelemetryController, MenuController
from views import MenuView, Screen1Overview, Screen2Timing, Screen3Telemetry
from views import Screen4Standings, Screen5Comparison, Screen6History
from packet_parsers import PacketID

class F1TelemetryApp:
    """Hoofd applicatie klasse met submenu ondersteuning"""
    
    def __init__(self):
        """Initialiseer applicatie"""
        self.logger = logger_service.get_logger('MainApp')
        self.logger.info("F1 25 Telemetry System wordt gestart...")
        
        # Controllers
        self.telemetry_controller = TelemetryController()
        self.menu_controller = MenuController()
        
        # UDP Listener
        self.udp_listener = UDPListener()
        
        # Views
        self.menu_view = MenuView(self.menu_controller)
        
        # Schermen initialiseren
        self.screen1 = Screen1Overview(self.telemetry_controller)
        self.screen2 = Screen2Timing(self.telemetry_controller)
        self.screen3 = Screen3Telemetry(self.telemetry_controller)
        self.screen4 = Screen4Standings(self.telemetry_controller)
        self.screen5 = Screen5Comparison(self.telemetry_controller)
        self.screen6 = Screen6History(self.telemetry_controller)
        
        # Registreer schermen bij menu controller
        self.menu_controller.register_screen(1, self.screen1.render)
        self.menu_controller.register_screen(2, self.screen2.render)
        self.menu_controller.register_screen(3, self.screen3.render)
        self.menu_controller.register_screen(4, self.screen4.render)
        self.menu_controller.register_screen(5, self.screen5.render)
        self.menu_controller.register_screen(6, self.screen6.render)
        
        # Registreer enkele demo submenu functies
        self._register_demo_submenu_functions()
        
        self.running = False
    
    def _register_demo_submenu_functions(self):
        """Registreer demo submenu functies"""
        # Scherm 1 functies
        self.menu_controller.register_submenu_function(1, 1, self.demo_practice_mode)
        self.menu_controller.register_submenu_function(1, 2, self.demo_race_mode)
        
        # Scherm 3 functies  
        self.menu_controller.register_submenu_function(3, 1, self.demo_dashboard)
        self.menu_controller.register_submenu_function(3, 2, self.demo_fuel_ers)
        
        # Meer functies kunnen hier worden toegevoegd...
    
    # Demo submenu functies
    def demo_practice_mode(self):
        """Demo Practice Mode functie"""
        print("\n" + "="*60)
        print("PRACTICE MODE - LEADERBOARD + CONSISTENTIE ANALYSE")
        print("="*60)
        print("Demo data:")
        print("1. Lewis Hamilton    - 1:23.456  [Consistentie: 98%]")
        print("2. Max Verstappen    - 1:23.789  [Consistentie: 96%]") 
        print("3. Student Marcel    - 1:24.123  [Consistentie: 89%]")
        print("-"*60)
        print("Deze functie toont:")
        print("- Rondetijden leaderboard")
        print("- Consistentie analyse per rijder")
        print("- Best lap times")
        print("="*60)
    
    def demo_race_mode(self):
        """Demo Race Mode functie"""
        print("\n" + "="*60)
        print("RACE MODE - LIVE KLASSEMENT + DELTA'S")
        print("="*60)
        print("Live posities:")
        print("P1  Lewis Hamilton    [+0.000]")
        print("P2  Max Verstappen    [+2.156]") 
        print("P3  Student Marcel    [+8.945]")
        print("-"*60)
        print("Deze functie toont:")
        print("- Live race klassement")
        print("- Delta's tussen rijders")
        print("- Gap naar leider")
        print("="*60)
    
    def demo_dashboard(self):
        """Demo Dashboard functie"""
        print("\n" + "="*60)
        print("DASHBOARD - LIVE TELEMETRIE AUTO 1")
        print("="*60)
        print("Speed:    287 km/h       RPM:      8245")
        print("Gear:     6              Throttle: 98%")
        print("Brake:    0%             Steer:    +12°")
        print("DRS:      OPEN           ERS:      87%")
        print("-"*60)
        print("Deze functie toont:")
        print("- Real-time speed, RPM, gear")
        print("- Throttle/brake inputs")
        print("- Steering angle")
        print("- DRS en ERS status")
        print("="*60)
    
    def demo_fuel_ers(self):
        """Demo Fuel & ERS Management functie"""
        print("\n" + "="*60)
        print("FUEL & ERS MANAGEMENT - AUTO 1")
        print("="*60)
        print("Fuel Remaining:  34.5 kg")
        print("Laps Remaining:  +12 laps") 
        print("Fuel per Lap:    2.8 kg/lap")
        print("ERS Store:       87%")
        print("ERS Deploy:      Auto Mode")
        print("-"*60)
        print("Deze functie toont:")
        print("- Real-time brandstof verbruik")
        print("- Geschatte laps remaining")
        print("- ERS deployment strategie")
        print("- Fuel saving tips")
        print("="*60)
    
    def start(self):
        """Start de applicatie"""
        try:
            # Toon welkomst
            self.menu_view.show_welcome()
            
            # Start UDP listener
            self.udp_listener.start()
            time.sleep(0.5)  # Geef listener tijd om te starten
            
            if not self.udp_listener.is_running():
                raise Exception("UDP listener kon niet worden gestart")
            
            # Start menu controller
            self.menu_controller.start()
            self.running = True
            
            self.logger.info("Applicatie succesvol gestart")
            
            # Main loop
            self.run()
            
        except KeyboardInterrupt:
            self.logger.info("Applicatie onderbroken door gebruiker (Ctrl+C)")
            self.stop()
        except Exception as e:
            self.logger.error(f"Fout bij starten applicatie: {e}", exc_info=True)
            self.menu_view.show_error(f"Kon applicatie niet starten: {e}")
            self.stop()
            sys.exit(1)
    
    def run(self):
        """Main application loop met submenu ondersteuning"""
        auto_refresh = False
        last_refresh = time.time()
        
        while self.running:
            try:
                # Render huidig scherm
                self.menu_controller.render_current_screen()
                
                # Toon status
                self.menu_view.show_status(self.udp_listener)
                
                # Toon menu (kan hoofdmenu of submenu zijn)
                self.menu_view.show_menu()
                
                # Check auto-refresh
                if auto_refresh:
                    print("Auto-refresh actief (druk R om uit te schakelen)")
                    print()
                    
                    # Wacht kort en refresh
                    time.sleep(2.0)
                    
                    # Check voor input met timeout (niet geïmplementeerd in basic versie)
                    continue
                
                # Haal gebruiker input op
                choice = self.menu_view.get_user_input()
                
                # Verwerk input met nieuwe submenu logica
                continue_running = self.menu_controller.handle_input(choice)
                
                if not continue_running:
                    self.running = False
                    break
                
                # Special commands
                if choice.upper() == 'R':
                    auto_refresh = not auto_refresh
                    status = "aan" if auto_refresh else "uit"
                    print(f"Auto-refresh {status}")
                    time.sleep(1)
                
                # Kleine pause voor submenu functies
                if not self.menu_controller.is_in_submenu_mode() and self.menu_controller.get_current_submenu() is not None:
                    print("\nDruk ENTER om door te gaan...")
                    input()
                
            except KeyboardInterrupt:
                self.logger.info("Onderbroken door gebruiker")
                self.running = False
                break
            except Exception as e:
                self.logger.error(f"Fout in main loop: {e}", exc_info=True)
                self.menu_view.show_error(f"Onverwachte fout: {e}")
                time.sleep(2)
        
        self.stop()
    
    def stop(self):
        """Stop de applicatie"""
        if hasattr(self, 'udp_listener'):
            self.udp_listener.stop()
        
        if hasattr(self, 'menu_controller'):
            self.menu_controller.stop()
        
        self.running = False
        self.logger.info("F1 25 Telemetry System gestopt")

def main():
    """Main entry point"""
    app = F1TelemetryApp()
    app.start()

if __name__ == "__main__":
    main()