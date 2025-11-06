"""
F1 25 Telemetry System - Data Processor
Verwerkt en berekent data voor analyse
"""

from typing import List, Dict, Any, Optional
from services import logger_service

class DataProcessor:
    """
    Processor voor data berekeningen en analyses
    """
    
    def __init__(self):
        """Initialiseer data processor"""
        self.logger = logger_service.get_logger('DataProcessor')
    
    def calculate_lap_delta(self, lap_time_ms: int, reference_time_ms: int) -> int:
        """
        Bereken delta tussen twee lap tijden
        
        Args:
            lap_time_ms: Lap tijd in milliseconden
            reference_time_ms: Referentie tijd in milliseconden
            
        Returns:
            Delta in milliseconden (positief = langzamer)
        """
        return lap_time_ms - reference_time_ms
    
    def calculate_sector_delta(self, sector_ms: int, best_sector_ms: int) -> int:
        """
        Bereken sector delta
        
        Args:
            sector_ms: Sector tijd
            best_sector_ms: Beste sector tijd
            
        Returns:
            Delta in milliseconden
        """
        if sector_ms == 0 or best_sector_ms == 0:
            return 0
        return sector_ms - best_sector_ms
    
    def calculate_theoretical_best(self, sectors: Dict[str, Optional[int]]) -> Optional[int]:
        """
        Bereken theoretische beste lap uit beste sectoren
        
        Args:
            sectors: Dict met sector1, sector2, sector3 in ms
            
        Returns:
            Theoretische beste tijd in ms of None
        """
        s1 = sectors.get('sector1')
        s2 = sectors.get('sector2')
        s3 = sectors.get('sector3')
        
        if all([s1, s2, s3]):
            return s1 + s2 + s3
        
        return None
    
    def calculate_pace(self, lap_times: List[int], exclude_outliers: bool = True) -> Optional[float]:
        """
        Bereken gemiddelde pace uit lap tijden
        
        Args:
            lap_times: List met lap tijden in ms
            exclude_outliers: Sluit outliers uit (in/out laps)
            
        Returns:
            Gemiddelde lap tijd in ms of None
        """
        if not lap_times:
            return None
        
        valid_times = [t for t in lap_times if t > 0]
        
        if not valid_times:
            return None
        
        if exclude_outliers and len(valid_times) > 2:
            # Verwijder snelste en langzaamste
            sorted_times = sorted(valid_times)
            valid_times = sorted_times[1:-1]
        
        return sum(valid_times) / len(valid_times)
    
    def calculate_consistency(self, lap_times: List[int]) -> Optional[float]:
        """
        Bereken consistentie (standaard deviatie)
        
        Args:
            lap_times: List met lap tijden in ms
            
        Returns:
            Standaard deviatie in ms of None
        """
        if len(lap_times) < 2:
            return None
        
        valid_times = [t for t in lap_times if t > 0]
        
        if len(valid_times) < 2:
            return None
        
        # Bereken gemiddelde
        mean = sum(valid_times) / len(valid_times)
        
        # Bereken standaard deviatie
        variance = sum((x - mean) ** 2 for x in valid_times) / len(valid_times)
        std_dev = variance ** 0.5
        
        return std_dev
    
    def find_best_lap(self, laps: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Vind beste lap uit lijst
        
        Args:
            laps: List met lap dicts
            
        Returns:
            Beste lap dict of None
        """
        valid_laps = [lap for lap in laps if lap.get('is_valid') and lap.get('lap_time_ms', 0) > 0]
        
        if not valid_laps:
            return None
        
        return min(valid_laps, key=lambda x: x['lap_time_ms'])
    
    def find_best_sectors(self, laps: List[Dict[str, Any]]) -> Dict[str, Optional[int]]:
        """
        Vind beste sector tijden uit lijst van laps
        
        Args:
            laps: List met lap dicts
            
        Returns:
            Dict met beste sector tijden
        """
        result = {
            'sector1': None,
            'sector2': None,
            'sector3': None
        }
        
        # Sector 1
        valid_s1 = [lap['sector1_ms'] for lap in laps 
                    if lap.get('sector1_valid') and lap.get('sector1_ms', 0) > 0]
        if valid_s1:
            result['sector1'] = min(valid_s1)
        
        # Sector 2
        valid_s2 = [lap['sector2_ms'] for lap in laps 
                    if lap.get('sector2_valid') and lap.get('sector2_ms', 0) > 0]
        if valid_s2:
            result['sector2'] = min(valid_s2)
        
        # Sector 3
        valid_s3 = [lap['sector3_ms'] for lap in laps 
                    if lap.get('sector3_valid') and lap.get('sector3_ms', 0) > 0]
        if valid_s3:
            result['sector3'] = min(valid_s3)
        
        return result
    
    def calculate_gap_to_leader(self, lap_time_ms: int, leader_time_ms: int) -> str:
        """
        Formatteer gap naar leider
        
        Args:
            lap_time_ms: Eigen lap tijd
            leader_time_ms: Leider lap tijd
            
        Returns:
            Geformateerde gap string
        """
        if lap_time_ms <= 0 or leader_time_ms <= 0:
            return "-"
        
        gap_ms = lap_time_ms - leader_time_ms
        
        if gap_ms == 0:
            return "0.000"
        
        gap_seconds = gap_ms / 1000
        return f"+{gap_seconds:.3f}"
    
    def calculate_tire_degradation(self, lap_times: List[int], window_size: int = 5) -> Optional[float]:
        """
        Bereken bandslijtage trend (lap tijd toename per lap)
        
        Args:
            lap_times: List met lap tijden in ms
            window_size: Aantal laps voor trend berekening
            
        Returns:
            Gemiddelde toename in ms per lap of None
        """
        if len(lap_times) < window_size:
            return None
        
        # Gebruik laatste X laps
        recent_laps = lap_times[-window_size:]
        valid_laps = [t for t in recent_laps if t > 0]
        
        if len(valid_laps) < 2:
            return None
        
        # Simpele lineaire trend
        total_increase = valid_laps[-1] - valid_laps[0]
        avg_increase_per_lap = total_increase / (len(valid_laps) - 1)
        
        return avg_increase_per_lap
    
    def is_improving(self, lap_times: List[int], window_size: int = 3) -> bool:
        """
        Check of lap tijden verbeteren
        
        Args:
            lap_times: List met lap tijden
            window_size: Aantal laps om te vergelijken
            
        Returns:
            True als tijden verbeteren
        """
        if len(lap_times) < window_size + 1:
            return False
        
        recent = lap_times[-window_size:]
        previous = lap_times[-(window_size + 1):-1]
        
        recent_avg = sum(recent) / len(recent)
        previous_avg = sum(previous) / len(previous)
        
        return recent_avg < previous_avg
    
    def calculate_sector_percentages(self, sector1_ms: int, sector2_ms: int, 
                                    sector3_ms: int) -> Dict[str, float]:
        """
        Bereken sector percentages van totale lap tijd
        
        Args:
            sector1_ms, sector2_ms, sector3_ms: Sector tijden
            
        Returns:
            Dict met percentages per sector
        """
        total = sector1_ms + sector2_ms + sector3_ms
        
        if total == 0:
            return {'sector1': 0, 'sector2': 0, 'sector3': 0}
        
        return {
            'sector1': (sector1_ms / total) * 100,
            'sector2': (sector2_ms / total) * 100,
            'sector3': (sector3_ms / total) * 100
        }