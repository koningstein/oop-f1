"""
Telemetry Database Integratie voor F1 25 project
Integreert telemetry data met database opslag van rondetijden
"""

import logging
import time
from typing import Optional, Dict, Any, Set, Callable
from datetime import datetime, timedelta
from threading import Lock
from lap_time_database import lap_db
from telemetry_utils import LapDataProcessor, TelemetryUtils

class TelemetryDatabaseIntegration:
    """
    Hoofdklasse voor integratie tussen telemetry en database
    """
    
    def __init__(self, auto_save: bool = True, save_interval: float = 1.0):
        """
        Initialiseer telemetry database integratie
        
        Args:
            auto_save: Automatisch opslaan van rondetijden (default: True)
            save_interval: Minimum interval tussen opslag van rondetijden in seconden (default: 1.0)
        """
        self.logger = logging.getLogger(__name__)
        self.auto_save = auto_save
        self.save_interval = save_interval
        
        # Database en utilities
        self.lap_database = lap_db
        self.lap_processor = LapDataProcessor()
        self.utils = TelemetryUtils()
        
        # Tracking van laatste opgeslagen tijden per driver
        self._last_saved_times: Dict[str, Dict[str, Any]] = {}
        self._save_lock = Lock()
        
        # Callback functies voor events
        self._lap_completed_callbacks: Set[Callable] = set()
        self._new_best_time_callbacks: Set[Callable] = set()
        
        # Sessie informatie
        self._current_track: Optional[str] = None
        self._current_session_type: Optional[str] = None
        self._session_start_time: Optional[datetime] = None
        
        self.logger.info(f"TelemetryDatabaseIntegration geïnitialiseerd - Auto save: {auto_save}")
    
    def set_session_info(self, track_name: str, session_type: str = "Practice"):
        """
        Stel huidige sessie informatie in
        
        Args:
            track_name: Naam van het circuit
            session_type: Type sessie (Practice, Qualifying, Race, etc.)
        """
        self._current_track = track_name
        self._current_session_type = session_type
        self._session_start_time = datetime.now()
        
        # Reset laatste opgeslagen tijden voor nieuwe sessie
        with self._save_lock:
            self._last_saved_times.clear()
        
        self.logger.info(f"Sessie gestart - Track: {track_name}, Type: {session_type}")
    
    def process_lap_data_packet(self, lap_packet: Any, participants_packet: Any = None) -> Dict[str, Any]:
        """
        Verwerk een lap data packet en sla nieuwe rondetijden op
        
        Args:
            lap_packet: LapDataPacket uit telemetry
            participants_packet: ParticipantsPacket voor driver namen (optioneel)
            
        Returns:
            Dictionary met verwerkte informatie
        """
        if not self._current_track:
            self.logger.warning("Geen track informatie - stel eerst sessie info in met set_session_info()")
            return {}
        
        results = {
            'new_lap_times': [],
            'updated_drivers': [],
            'errors': []
        }
        
        try:
            # Verwerk elke auto in het packet
            for car_index, lap_data in enumerate(lap_packet.lap_data):
                if not lap_data:
                    continue
                
                # Krijg driver naam
                driver_name = self._get_driver_name(car_index, participants_packet)
                if not driver_name or driver_name == "Unknown Driver":
                    continue
                
                # Check of er een nieuwe rondetijd is om op te slaan
                if self._should_save_lap_time(driver_name, lap_data):
                    lap_result = self._save_lap_time(driver_name, lap_data)
                    if lap_result:
                        results['new_lap_times'].append(lap_result)
                        results['updated_drivers'].append(driver_name)
                        
                        # Check voor nieuwe beste tijd
                        self._check_new_best_time(lap_result)
            
        except Exception as e:
            error_msg = f"Fout bij verwerken lap data packet: {e}"
            self.logger.error(error_msg)
            results['errors'].append(error_msg)
        
        return results
    
    def _get_driver_name(self, car_index: int, participants_packet: Any = None) -> str:
        """
        Krijg driver naam voor een auto index
        
        Args:
            car_index: Index van de auto
            participants_packet: ParticipantsPacket (optioneel)
            
        Returns:
            Driver naam of fallback naam
        """
        try:
            if participants_packet and hasattr(participants_packet, 'participants'):
                if car_index < len(participants_packet.participants):
                    participant = participants_packet.participants[car_index]
                    if hasattr(participant, 'name'):
                        name = self.utils.get_driver_name_from_telemetry(participant.name)
                        if name and name != "Unknown Driver":
                            return name
            
            # Fallback naar generieke naam
            return f"Driver_{car_index + 1}"
            
        except Exception as e:
            self.logger.debug(f"Fout bij ophalen driver naam voor index {car_index}: {e}")
            return f"Driver_{car_index + 1}"
    
    def _should_save_lap_time(self, driver_name: str, lap_data: Any) -> bool:
        """
        Check of een rondetijd opgeslagen moet worden
        
        Args:
            driver_name: Naam van de driver
            lap_data: LapData object
            
        Returns:
            True als rondetijd opgeslagen moet worden
        """
        if not self.auto_save:
            return False
        
        if not hasattr(lap_data, 'last_lap_time_ms') or lap_data.last_lap_time_ms <= 0:
            return False
        
        # Check minimum tijd tussen opslag
        current_time = time.time()
        
        with self._save_lock:
            if driver_name in self._last_saved_times:
                last_save_time = self._last_saved_times[driver_name].get('timestamp', 0)
                last_lap_time = self._last_saved_times[driver_name].get('lap_time_ms', 0)
                
                # Check tijd interval en of het een nieuwe rondetijd is
                if (current_time - last_save_time < self.save_interval or 
                    last_lap_time == lap_data.last_lap_time_ms):
                    return False
        
        return True
    
    def _save_lap_time(self, driver_name: str, lap_data: Any) -> Optional[Dict[str, Any]]:
        """
        Sla een rondetijd op in de database
        
        Args:
            driver_name: Naam van de driver
            lap_data: LapData object
            
        Returns:
            Dictionary met opgeslagen lap info of None
        """
        try:
            # Verwerk lap data
            processed_data = self.lap_processor.process_lap_data(
                lap_data, driver_name, self._current_track
            )
            
            if not processed_data:
                return None
            
            # Sla op in database
            lap_id = self.lap_database.save_lap_time(**processed_data)
            
            if lap_id:
                # Update laatste opgeslagen tijd
                with self._save_lock:
                    self._last_saved_times[driver_name] = {
                        'timestamp': time.time(),
                        'lap_time_ms': lap_data.last_lap_time_ms,
                        'lap_id': lap_id
                    }
                
                # Maak resultaat
                result = processed_data.copy()
                result['lap_id'] = lap_id
                result['lap_time_formatted'] = self.utils.format_lap_time(processed_data['lap_time'])
                
                # Trigger callbacks
                self._trigger_lap_completed_callbacks(result)
                
                return result
            
            return None
            
        except Exception as e:
            self.logger.error(f"Fout bij opslaan rondetijd voor {driver_name}: {e}")
            return None
    
    def _check_new_best_time(self, lap_result: Dict[str, Any]):
        """
        Check of er een nieuwe beste tijd is neergezet
        
        Args:
            lap_result: Dictionary met lap resultaat
        """
        try:
            if not lap_result.get('is_valid', True):
                return
            
            # Krijg huidige beste tijd
            best_lap = self.lap_database.get_best_lap_time(self._current_track)
            
            # Check of dit een nieuwe beste tijd is
            if (not best_lap or 
                lap_result['lap_time'] < best_lap['lap_time'] or
                best_lap['id'] == lap_result['lap_id']):
                
                # Trigger nieuwe beste tijd callbacks
                self._trigger_new_best_time_callbacks(lap_result)
                
                self.logger.info(f"Nieuwe beste tijd! {lap_result['driver_name']}: {lap_result['lap_time_formatted']} op {self._current_track}")
        
        except Exception as e:
            self.logger.error(f"Fout bij checken nieuwe beste tijd: {e}")
    
    def manual_save_lap_time(self, driver_name: str, lap_time: float, 
                           sector1: Optional[float] = None, sector2: Optional[float] = None, 
                           sector3: Optional[float] = None, is_valid: bool = True) -> Optional[int]:
        """
        Handmatig een rondetijd opslaan
        
        Args:
            driver_name: Naam van de driver
            lap_time: Rondetijd in seconden
            sector1: Sector 1 tijd in seconden (optioneel)
            sector2: Sector 2 tijd in seconden (optioneel)
            sector3: Sector 3 tijd in seconden (optioneel)
            is_valid: Of de rondetijd geldig is
            
        Returns:
            ID van opgeslagen record of None
        """
        if not self._current_track:
            self.logger.error("Geen track informatie - stel eerst sessie info in")
            return None
        
        try:
            lap_id = self.lap_database.save_lap_time(
                driver_name=driver_name,
                lap_time=lap_time,
                track_name=self._current_track,
                sector1_time=sector1,
                sector2_time=sector2,
                sector3_time=sector3,
                is_valid=is_valid
            )
            
            if lap_id:
                self.logger.info(f"Handmatige rondetijd opgeslagen - {driver_name}: {self.utils.format_lap_time(lap_time)}")
            
            return lap_id
            
        except Exception as e:
            self.logger.error(f"Fout bij handmatig opslaan rondetijd: {e}")
            return None
    
    def get_current_leaderboard(self, limit: int = 20) -> list:
        """
        Krijg huidige leaderboard voor de actieve track
        
        Args:
            limit: Maximum aantal resultaten
            
        Returns:
            Lijst met leaderboard data
        """
        if not self._current_track:
            return []
        
        return self.lap_database.get_leaderboard(self._current_track, limit)
    
    def get_driver_stats(self, driver_name: str) -> Dict[str, Any]:
        """
        Krijg statistieken voor een specifieke driver
        
        Args:
            driver_name: Naam van de driver
            
        Returns:
            Dictionary met driver statistieken
        """
        if not self._current_track:
            return {}
        
        try:
            # Krijg alle rondetijden voor deze driver op deze track
            lap_times = self.lap_database.get_lap_times_for_driver(driver_name, self._current_track)
            
            if not lap_times:
                return {'driver_name': driver_name, 'total_laps': 0}
            
            # Bereken statistieken
            times_list = [lap['lap_time'] for lap in lap_times]
            consistency = self.utils.calculate_consistency(times_list)
            
            best_lap = min(lap_times, key=lambda x: x['lap_time'])
            
            return {
                'driver_name': driver_name,
                'total_laps': len(lap_times),
                'best_lap_time': best_lap['lap_time'],
                'best_lap_formatted': self.utils.format_lap_time(best_lap['lap_time']),
                'average_time': consistency['average'],
                'average_formatted': self.utils.format_lap_time(consistency['average']),
                'consistency_std_dev': consistency['std_dev'],
                'consistency_coefficient': consistency['coefficient_variation'],
                'last_lap': lap_times[0] if lap_times else None
            }
            
        except Exception as e:
            self.logger.error(f"Fout bij ophalen driver stats voor {driver_name}: {e}")
            return {'driver_name': driver_name, 'error': str(e)}
    
    # Callback systeem voor events
    def add_lap_completed_callback(self, callback: Callable):
        """Voeg callback toe voor wanneer een rondetijd voltooid is"""
        self._lap_completed_callbacks.add(callback)
    
    def remove_lap_completed_callback(self, callback: Callable):
        """Verwijder lap completed callback"""
        self._lap_completed_callbacks.discard(callback)
    
    def add_new_best_time_callback(self, callback: Callable):
        """Voeg callback toe voor nieuwe beste tijden"""
        self._new_best_time_callbacks.add(callback)
    
    def remove_new_best_time_callback(self, callback: Callable):
        """Verwijder nieuwe beste tijd callback"""
        self._new_best_time_callbacks.discard(callback)
    
    def _trigger_lap_completed_callbacks(self, lap_result: Dict[str, Any]):
        """Trigger alle lap completed callbacks"""
        for callback in self._lap_completed_callbacks.copy():
            try:
                callback(lap_result)
            except Exception as e:
                self.logger.error(f"Fout in lap completed callback: {e}")
    
    def _trigger_new_best_time_callbacks(self, lap_result: Dict[str, Any]):
        """Trigger alle nieuwe beste tijd callbacks"""
        for callback in self._new_best_time_callbacks.copy():
            try:
                callback(lap_result)
            except Exception as e:
                self.logger.error(f"Fout in nieuwe beste tijd callback: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        self._lap_completed_callbacks.clear()
        self._new_best_time_callbacks.clear()
        self.logger.info("TelemetryDatabaseIntegration opgeruimd")


# Globale integratie instantie
telemetry_db_integration = TelemetryDatabaseIntegration()