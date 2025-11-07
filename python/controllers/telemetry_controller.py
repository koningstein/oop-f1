"""
F1 25 Telemetry System - Telemetry Controller
Beheert de state van alle live telemetry data
"""
import threading
from typing import Optional
from services import logger_service

# --- GECORRIGEERDE IMPORT ---
# Importeer de 'LapData' dataclass
try:
    # Aanname: je 'oud2/lap_packets.py' heet nu 'packet_parsers/lap_parser.py'
    from packet_parsers.lap_parser import LapData
except ImportError:
    print("[ERROR] Kon LapData structuur niet importeren. Functionaliteit 1.5 zal falen.")
    class LapData:
        pass

# Importeer de Models, gebaseerd op je logbestanden
try:
    from models.session_model import SessionModel
    from models.driver_model import DriverModel
    from models.lap_model import LapModel
except ImportError:
    print("[ERROR] Kon SessionModel, DriverModel of LapModel niet importeren.")
    # Placeholders
    class SessionModel: pass
    class DriverModel: pass
    class LapModel: pass


class TelemetryController:
    """
    Beheert de opslag en toegang tot alle telemetry data.
    Deze klasse is thread-safe.
    """
    
    def __init__(self):
        """Initialiseer de Telemetry Controller"""
        self.logger = logger_service.get_logger('TelemetryController')
        
        # Initialiseer de models die je in je structuur gebruikt
        self.session_model = SessionModel()
        self.driver_model = DriverModel()
        self.lap_model = LapModel()
        
        # --- LOGICA VOOR SCHERM 1.5 ---
        self.player_lap_data: Optional[LapData] = None
        self._lock = threading.Lock()
        
        self.logger.info("Telemetry Controller geïnitialiseerd")

    # --- Setters (aangeroepen door DataProcessor) ---

    def update_lap_data(self, lap_data: LapData):
        """
        Update de huidige ronde data voor de speler.
        Aangeroepen vanuit de DataProcessor thread.
        
        Args:
            lap_data: De LapData struct voor de speler.
        """
        with self._lock:
            self.player_lap_data = lap_data
            
        # Hier kun je de data ook doorgeven aan je database model
        # self.lap_model.update_live_lap(lap_data)
        

    # --- Getters (aangeroepen door Views) ---

    def get_player_lap_data(self) -> Optional[LapData]:
        """
        Haal de huidige ronde data voor de speler op (thread-safe).
        Aangeroepen vanuit de View/Main thread (voor Scherm 1.5).
        
        Returns:
            De LapData struct, of None als er nog geen data is.
        """
        with self._lock:
            return self.player_lap_data

    # --- METHODE VOOR SCHERM 1 ---
    
    def get_current_session_id(self) -> Optional[int]:
        """
        Haalt het ID van de huidige actieve sessie op.
        (Placeholder)
        """
        # Log de waarschuwing (dit voorkomt de crash van vorig log)
        if not hasattr(self, '_session_id_warning_logged'):
            self.logger.warning("TelemetryController.get_current_session_id aangeroepen (placeholder).")
            self.logger.warning("Screen1Overview.py moet worden bijgewerkt.")
            self._session_id_warning_logged = True # Log maar één keer
        
        # Return None om crashes te voorkomen
        return None

    # ... (Hier komen je andere controller-methodes) ...