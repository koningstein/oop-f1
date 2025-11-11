"""
F1 25 Telemetry System - Main Application
(Versie 9.3: Logbestand legen bij start + V9.2 Injecties)
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

# --- AANPASSING V9.3: LOGBESTAND LEGEN ---
# Regel dat de telemetry.log leeg gemaakt wordt zodra main.py gestart wordt
try:
    # Bouw het pad naar het logbestand (relatief aan deze main.py)
    log_file_path = os.path.join(project_root, 'logs', 'telemetry.log')

    # Controleer of de 'logs' map bestaat, zo niet, maak hem aan
    log_dir = os.path.dirname(log_file_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"[MAIN_INIT] Log map aangemaakt op: {log_dir}", file=sys.stdout)

    # Open het bestand in 'write' modus ('w') om het te legen (truncate)
    # Als het bestand niet bestaat, wordt het hierdoor ook aangemaakt.
    with open(log_file_path, 'w') as f:
        pass  # Het bestand is nu leeg of aangemaakt

except IOError as e:
    # Dit print naar de console, aangezien de logger nog niet actief is
    print(f"[MAIN_INIT] WAARSCHUWING: Kon logbestand {log_file_path} niet legen: {e}", file=sys.stderr)
except Exception as e:
    print(f"[MAIN_INIT] FATALE FOUT bij voorbereiden logbestand: {e}", file=sys.stderr)
    sys.exit(1)  # We stoppen als de logs niet kunnen worden voorbereid
# --- EINDE AANPASSING V9.3 ---


from typing import Optional

# Non-blocking input (Windows-specifiek)
try:
    import msvcrt
except ImportError:
    msvcrt = None

# NU pas importeren we de logger_service, die het (nu lege) bestand zal gebruiken
from services import logger_service, UDPListener
from controllers import TelemetryController, MenuController, DataProcessor, SessionController

from views import MenuView, Screen1Overview, Screen2Timing, Screen3Telemetry
from views import Screen4Standings, Screen5Comparison, Screen6History

# Importeer de specifieke views voor Scherm 1
from views.screen1_features.live_timing_view import LiveTimingView
from views.screen1_features.practice_view import PracticeView
from views.screen1_features.race_view import RaceView
from views.screen1_features.tournament_view import TournamentView
from views.screen1_features.position_chart_view import PositionChartView

# --- DATABASE INITIALISATIE ---
try:
    from models.database import database

    # De logger service is nu beschikbaar
    db_init_logger = logger_service.get_logger('DatabaseInit')
    if not database._pool:
        db_init_logger.critical("Database pool (database._pool) is None NA import.")
        raise Exception("Database pool kon niet worden geïnitialiseerd (None).")

    db_init_logger.info("Database Singleton succesvol geïmporteerd en pool is actief.")

except Exception as db_init_e:
    print(f"FATALE FOUT bij initialiseren database: {db_init_e}", file=sys.stderr)
    # Probeer ook naar de logger te schrijven, als die al draait
    try:
        logger_service.get_logger('MainApp').error(f"FATALE FOUT DB init: {db_init_e}", exc_info=True)
    except:
        pass
    print("Controleer je MySQL server en de DATABASE instellingen in config.py.", file=sys.stderr)
    sys.exit(1)


# --- EINDE DATABASE INITIALISATIE ---


class F1TelemetryApp:
    """Hoofd applicatie klasse met submenu ondersteuning"""

    def __init__(self):
        self.logger = logger_service.get_logger('MainApp')
        self.logger.info("F1 25 Telemetry System wordt gestart...")
        self.logger.info("Logbestand succesvol geleegd (V9.3 init)")

        # --- AANGEPAST (V9.2): Controllers initialiseren ---
        self.session_controller = SessionController()
        self.telemetry_controller = TelemetryController(session_controller=self.session_controller)
        self.menu_controller = MenuController()

        # Nu de DataProcessor, en *injecteer* beide controllers
        self.data_processor = DataProcessor(
            telemetry_controller=self.telemetry_controller,
            session_controller=self.session_controller
        )
        # --- EINDE AANGEPAST ---

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
            except UnicodeDecodeError:
                return None
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

    # --- GECORRIGEERDE run() METHODE (jouw V6) ---
    def run(self):
        """Main application loop met automatische live-view detectie."""
        last_refresh_time = time.time()
        refresh_interval = 1.0
        while self.running:
            try:
                choice = None
                is_live_view_active = self.menu_controller.is_current_view_live()
                if is_live_view_active:
                    choice = self.get_non_blocking_input()
                    current_time = time.time()
                    if (current_time - last_refresh_time) < refresh_interval:
                        if not choice:
                            time.sleep(0.05)
                            continue
                    last_refresh_time = current_time
                    self.menu_controller.render_current_screen()
                    self.menu_view.show_status(self.udp_listener)
                    self.menu_view.show_menu()
                    print(f"  AUTO-REFRESH AAN. Druk 'B' (terug) of '0' (afsluiten)...")
                else:
                    self.menu_controller.render_current_screen()
                    self.menu_view.show_status(self.udp_listener)
                    self.menu_view.show_menu()
                    choice = self.menu_view.get_user_input()
                if not choice:
                    continue
                continue_running = self.menu_controller.handle_input(choice)
                if not continue_running:
                    self.running = False
                    break
                is_NOW_live = self.menu_controller.is_current_view_live()
                if not is_NOW_live and \
                        not self.menu_controller.is_in_submenu_mode() and \
                        self.menu_controller.get_current_submenu() is not None:
                    print("\nStatisch scherm. Druk ENTER om terug te gaan...")
                    input()
                    self.menu_controller.back_to_submenu()
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

    # --- MAIN FUNCTIE DB CHECK ---
    if not database._pool:
        print("FATALE FOUT: Database pool kon niet worden geverifieerd in main().", file=sys.stderr)
        sys.exit(1)
    # --- EINDE CHECK ---

    app = F1TelemetryApp()
    app.start()


if __name__ == "__main__":
    main()