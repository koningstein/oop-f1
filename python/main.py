"""
F1 25 Telemetry System - Main Application
(Versie 6: Gecorrigeerde run() loop logica)
"""

# --- SYSTEEM IMPORT FIX ---
import sys
import os
import time

# Voeg de 'python' map (project root) toe aan het pad
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --- EINDE SYSTEEM IMPORT FIX ---

from typing import Optional

# Non-blocking input (Windows-specifiek)
try:
    import msvcrt
except ImportError:
    msvcrt = None

from services import logger_service, UDPListener
from controllers import TelemetryController, MenuController, DataProcessor
from views import MenuView, Screen1Overview, Screen2Timing, Screen3Telemetry
from views import Screen4Standings, Screen5Comparison, Screen6History

# Importeer de specifieke views voor Scherm 1
from views.screen1_features.live_timing_view import LiveTimingView
from views.screen1_features.practice_view import PracticeView
from views.screen1_features.race_view import RaceView
from views.screen1_features.tournament_view import TournamentView
from views.screen1_features.position_chart_view import PositionChartView

class F1TelemetryApp:
    """Hoofd applicatie klasse met submenu ondersteuning"""

    def __init__(self):
        self.logger = logger_service.get_logger('MainApp')
        self.logger.info("F1 25 Telemetry System wordt gestart...")

        self.telemetry_controller = TelemetryController()
        self.menu_controller = MenuController()
        self.data_processor = DataProcessor(self.telemetry_controller)
        self.udp_listener = UDPListener(
            packet_handler=self.data_processor.process_packet
        )
        self.menu_view = MenuView(self.menu_controller)

        # Hoofdschermen
        self.screen1 = Screen1Overview(self.telemetry_controller)
        self.screen2 = Screen2Timing(self.telemetry_controller)
        self.screen3 = Screen3Telemetry(self.telemetry_controller)
        self.screen4 = Screen4Standings(self.telemetry_controller)
        self.screen5 = Screen5Comparison(self.telemetry_controller)
        self.screen6 = Screen6History(self.telemetry_controller)

        # Views voor Scherm 1
        self.live_timing_view = LiveTimingView(self.telemetry_controller)
        self.practice_view = PracticeView(self.telemetry_controller)
        self.race_view = RaceView(self.telemetry_controller)
        self.tournament_view = TournamentView(self.telemetry_controller)
        self.position_chart_view = PositionChartView(self.telemetry_controller)

        self.menu_controller.register_screen(1, self.screen1.render)
        self.menu_controller.register_screen(2, self.screen2.render)
        self.menu_controller.register_screen(3, self.screen3.render)
        self.menu_controller.register_screen(4, self.screen4.render)
        self.menu_controller.register_screen(5, self.screen5.render)
        self.menu_controller.register_screen(6, self.screen6.render)

        self._register_submenu_functions()
        self.running = False

    def _register_submenu_functions(self):
        """Registreer alle submenu functies"""
        self.menu_controller.register_submenu_function(1, 1, self.practice_view.render, is_live=True)
        self.menu_controller.register_submenu_function(1, 2, self.race_view.render, is_live=True)
        self.menu_controller.register_submenu_function(1, 3, self.tournament_view.render, is_live=False)
        self.menu_controller.register_submenu_function(1, 4, self.position_chart_view.render, is_live=False)
        self.menu_controller.register_submenu_function(1, 5, self.live_timing_view.render, is_live=True)

        self.menu_controller.register_submenu_function(3, 1, self.demo_dashboard, is_live=False)
        self.menu_controller.register_submenu_function(3, 2, self.demo_fuel_ers, is_live=False)

    def demo_dashboard(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n[DEMO] Scherm 3.1 - Dashboard")

    def demo_fuel_ers(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n[DEMO] Scherm 3.2 - Fuel & ERS")

    def get_non_blocking_input(self) -> Optional[str]:
        if not msvcrt: return None
        if msvcrt.kbhit():
            key = msvcrt.getch()
            try:
                if key == b'\r': return None
                return key.decode('utf-8')
            except UnicodeDecodeError: return None
        return None

    def start(self):
        try:
            self.menu_view.show_welcome()
            self.udp_listener.start()
            time.sleep(0.5)
            if not self.udp_listener.is_running():
                raise Exception("UDP listener kon niet worden gestart")
            self.menu_controller.start()
            self.running = True
            self.logger.info("Applicatie succesvol gestart")
            self.run()
        except KeyboardInterrupt:
            self.logger.info("Applicatie onderbroken door gebruiker (Ctrl+C)")
            self.stop()
        except Exception as e:
            self.logger.error(f"Fout bij starten applicatie: {e}", exc_info=True)
            self.menu_view.show_error(f"Kon applicatie niet starten: {e}")
            self.stop()
            sys.exit(1)

    # --- GECORRIGEERDE run() METHODE ---
    def run(self):
        """Main application loop met automatische live-view detectie."""

        last_refresh_time = time.time()
        refresh_interval = 1.0  # Refresh interval voor live views

        while self.running:
            try:
                choice = None
                # Check de status AAN HET BEGIN van de loop
                is_live_view_active = self.menu_controller.is_current_view_live()

                if is_live_view_active:
                    # --- LIVE VIEW MODUS (NON-BLOCKING) ---
                    choice = self.get_non_blocking_input()

                    current_time = time.time()
                    if (current_time - last_refresh_time) < refresh_interval:
                        if not choice:
                            time.sleep(0.05) # Voorkom 100% CPU load
                            continue

                    last_refresh_time = current_time

                    self.menu_controller.render_current_screen() # Render de live view
                    self.menu_view.show_status(self.udp_listener)
                    self.menu_view.show_menu() # Toont "Actie (B=terug...)"
                    print(f"  AUTO-REFRESH AAN. Druk 'B' (terug) of '0' (afsluiten)...")

                else:
                    # --- NORMAAL MENU MODUS (BLOCKING) ---
                    self.menu_controller.render_current_screen() # Render het menu
                    self.menu_view.show_status(self.udp_listener)
                    self.menu_view.show_menu() # Toont het menu (1-6 of 1.1-1.5)
                    choice = self.menu_view.get_user_input()

                if not choice:
                    continue

                # --- VERWERK DE INPUT ---
                continue_running = self.menu_controller.handle_input(choice)

                if not continue_running:
                    self.running = False
                    break

                # --- GECORRIGEERDE LOGICA ---
                # Na het verwerken van de input, check de *NIEUWE* status.
                is_NOW_live = self.menu_controller.is_current_view_live()

                # Als we NIET in een live view zijn, EN we zijn in een functie
                # (niet een menu), DAN is het een statisch scherm.
                if not is_NOW_live and \
                   not self.menu_controller.is_in_submenu_mode() and \
                   self.menu_controller.get_current_submenu() is not None:

                    print("\nStatisch scherm. Druk ENTER om terug te gaan...")
                    input()
                    # Na 'enter', ga automatisch terug
                    self.menu_controller.back_to_submenu()

                # Als de view NU wel live is, doet de loop niets
                # en gaat naar de *volgende iteratie*, waar
                # 'is_live_view_active' bovenaan True zal zijn.

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