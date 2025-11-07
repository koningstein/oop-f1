"""
F1 25 Telemetry System - Telemetry Controller
Beheert de state van alle live telemetry data
"""
import threading
from typing import Optional
from services import logger_service

# --- GECORRIGEERDE IMPORT ---
# We importeren nu de 'LapData' structuur (niet het hele pakket)
try:
    from packet_parsers.packet_types import LapData
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

    # --- METHODE VOOR SCHERM 1 (Fix voor 'get_active_session_id') ---
    
    def get_current_session_id(self) -> Optional[int]:
        """
        Haalt het ID van de huidige actieve sessie op.
        (Aanname: delegeert naar SessionModel)
        """
        try:
            # --- AANGENOMEN METHODE ---
            # We proberen nu een andere methode, gebaseerd op je modelnaam
            # Pas 'get_current_session' aan als deze methode anders heet
            current_session = self.session_model.get_current_session()
            if current_session:
                # Aanname: de sessie heeft een 'id' attribuut
                return current_session.id
            return None
        except AttributeError as e:
            # Vangt de fout af als de methode niet bestaat
            self.logger.error(f"Fout bij ophalen session_id: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Onverwachte fout bij ophalen session_id: {e}")
            return None

    # ... (Hier komen je andere controller-methodes) ...