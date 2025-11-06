"""
F1 25 Telemetry System - Main Application
Techniek College Rotterdam - Software Developer MBO-4

Hoofdprogramma voor F1 25 telemetry systeem
Start alle componenten en runt de main loop
"""

import sys
import time
from services import setup_logger, get_logger, UDPListener
from controllers import TelemetryController, MenuController
from views import MenuView, Screen1Overview, Screen2Timing, Screen3Telemetry
from views import Screen4Standings, Screen5Comparison, Screen6History
from parsers import PacketID

class F1TelemetryApp:
    """Hoofd applicatie klasse"""
    
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
        
        # Registreer packet handlers
        self._register_packet_handlers()
        
        self.running = False
        self.logger.info("Applicatie initialisatie compleet")
    
    def _register_packet_handlers(self):
        """Registreer alle packet handlers bij UDP listener"""
        self.udp_listener.register_handler(
            PacketID.SESSION,
            self.telemetry_controller.handle_session_packet
        )
        self.udp_listener.register_handler(
            PacketID.LAP_DATA,
            self.telemetry_controller.handle_lap_data_packet
        )
        self.udp_listener.register_handler(
            PacketID.SESSION_HISTORY,
            self.telemetry_controller.handle_session_history_packet
        )
        self.udp_listener.register_handler(
            PacketID.PARTICIPANTS,
            self.telemetry_controller.handle_participants_packet
        )
        self.udp_listener.register_handler(
            PacketID.CAR_TELEMETRY,
            self.telemetry_controller.handle_car_telemetry_packet
        )
        
        self.logger.info("Packet handlers geregistreerd")
    
    def start(self):
        """Start de applicatie"""
        try:
            # Toon welkomst scherm
            self.menu_view.show_welcome()
            
            # Start UDP listener
            self.logger.info("UDP listener wordt gestart...")
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
        """Main application loop"""
        auto_refresh = False
        last_refresh = time.time()
        
        while self.running:
            try:
                # Render huidig scherm
                self.menu_controller.render_current_screen()
                
                # Toon status
                self.menu_view.show_status(self.udp_listener)
                
                # Toon menu
                self.menu_view.show_menu()
                
                # Check auto-refresh
                if auto_refresh:
                    print("Auto-refresh actief (druk R om uit te schakelen)")
                    print()
                    
                    # Wacht kort en refresh
                    time.sleep(2.0)
                    
                    # Check voor input (non-blocking zou beter zijn, maar simpel voor nu)
                    continue
                
                # Vraag gebruiker input
                choice = self.menu_view.get_user_input()
                
                # Speciale commando's
                if choice.lower() == 'r':
                    auto_refresh = not auto_refresh
                    continue
                elif choice.lower() == 'q' or choice == '0':
                    choice = '0'
                
                # Verwerk menu keuze
                should_continue = self.menu_controller.handle_input(choice)
                
                if not should_continue:
                    self.running = False
                    break
                
            except KeyboardInterrupt:
                self.logger.info("Ctrl+C gedetecteerd")
                self.running = False
                break
            except Exception as e:
                self.logger.error(f"Fout in main loop: {e}", exc_info=True)
                self.menu_view.show_error(f"Er is een fout opgetreden: {e}")
                self.menu_view.pause()
    
    def stop(self):
        """Stop de applicatie netjes"""
        self.logger.info("Applicatie wordt afgesloten...")
        
        self.running = False
        
        # Stop menu controller
        if self.menu_controller:
            self.menu_controller.stop()
        
        # Stop UDP listener
        if self.udp_listener and self.udp_listener.is_running():
            self.logger.info("UDP listener wordt gestopt...")
            self.udp_listener.stop()
        
        self.logger.info("Applicatie afgesloten")
        print("\nTot ziens!")


def main():
    """Main entry point"""
    print("=" * 80)
    print(" " * 20 + "F1 25 TELEMETRY SYSTEM")
    print(" " * 15 + "Techniek College Rotterdam")
    print("=" * 80)
    print()
    
    try:
        app = F1TelemetryApp()
        app.start()
    except Exception as e:
        print(f"\n[FATAL ERROR] Kon applicatie niet starten: {e}")
        logger_service.get_logger('Main').error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()