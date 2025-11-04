"""
Telemetry Utilities voor F1 25 project
Helper functies voor rondetijd conversies en telemetry data verwerking
"""

import logging
from typing import Optional, Tuple, Dict, Any
from datetime import datetime

class TelemetryUtils:
    """
    Utility klasse voor telemetry data conversies en helpers
    """
    
    @staticmethod
    def convert_ms_to_seconds(milliseconds: int) -> float:
        """
        Converteer milliseconden naar seconden (float)
        
        Args:
            milliseconds: Tijd in milliseconden
            
        Returns:
            Tijd in seconden als float
        """
        if milliseconds == 0:
            return 0.0
        return milliseconds / 1000.0
    
    @staticmethod
    def convert_sector_time_to_seconds(ms_part: int, minutes_part: int) -> float:
        """
        Converteer F1 25 sector tijd formaat naar seconden
        
        Args:
            ms_part: Milliseconden deel (max 60000)
            minutes_part: Minuten deel
            
        Returns:
            Totale tijd in seconden als float
        """
        if ms_part == 0 and minutes_part == 0:
            return 0.0
            
        total_seconds = (minutes_part * 60) + (ms_part / 1000.0)
        return total_seconds
    
    @staticmethod
    def format_lap_time(seconds: float) -> str:
        """
        Format rondetijd in seconden naar leesbaar formaat (MM:SS.mmm)
        
        Args:
            seconds: Tijd in seconden
            
        Returns:
            Geformatteerde tijd string
        """
        if seconds <= 0:
            return "--:--.---"
        
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        
        if minutes > 0:
            return f"{minutes}:{remaining_seconds:06.3f}"
        else:
            return f"{remaining_seconds:.3f}s"
    
    @staticmethod
    def format_time_difference(time1: float, time2: float) -> str:
        """
        Format tijdsverschil tussen twee tijden
        
        Args:
            time1: Eerste tijd in seconden
            time2: Tweede tijd in seconden (referentie)
            
        Returns:
            Geformatteerd verschil (+X.xxx of -X.xxx)
        """
        if time1 <= 0 or time2 <= 0:
            return "-.---"
        
        difference = time1 - time2
        
        if abs(difference) < 0.001:  # Minder dan 1ms verschil
            return "0.000"
        
        sign = "+" if difference > 0 else ""
        return f"{sign}{difference:.3f}"
    
    @staticmethod
    def is_valid_lap_time(lap_time_ms: int, min_time_ms: int = 30000, max_time_ms: int = 300000) -> bool:
        """
        Check of een rondetijd geldig is (binnen redelijke grenzen)
        
        Args:
            lap_time_ms: Rondetijd in milliseconden
            min_time_ms: Minimum geldige tijd (default: 30 seconden)
            max_time_ms: Maximum geldige tijd (default: 5 minuten)
            
        Returns:
            True als de tijd geldig is, False anders
        """
        if lap_time_ms <= 0:
            return False
        
        return min_time_ms <= lap_time_ms <= max_time_ms
    
    @staticmethod
    def is_valid_sector_time(sector_ms: int, sector_minutes: int, max_sector_time_ms: int = 120000) -> bool:
        """
        Check of een sectortijd geldig is
        
        Args:
            sector_ms: Sector tijd milliseconden deel
            sector_minutes: Sector tijd minuten deel
            max_sector_time_ms: Maximum sectortijd (default: 2 minuten)
            
        Returns:
            True als de sectortijd geldig is, False anders
        """
        if sector_ms == 0 and sector_minutes == 0:
            return False
            
        total_ms = (sector_minutes * 60 * 1000) + sector_ms
        return 1000 <= total_ms <= max_sector_time_ms  # Minimum 1 seconde, maximum zoals ingesteld
    
    @staticmethod
    def get_track_name_from_id(track_id: int) -> str:
        """
        Converteer F1 25 track ID naar leesbare naam
        
        Args:
            track_id: Numerieke track ID uit F1 25
            
        Returns:
            Leesbare circuit naam
        """
        # F1 25 track mapping (gebaseerd op officiële F1 circuits)
        track_names = {
            0: "Melbourne (Australia)",
            1: "Bahrain",
            2: "China (Shanghai)", 
            3: "Baku (Azerbaijan)",
            4: "Miami",
            5: "Imola (Italy)",
            6: "Monaco",
            7: "Canada (Montreal)",
            8: "Spain (Barcelona)",
            9: "Austria (Red Bull Ring)",
            10: "Great Britain (Silverstone)",
            11: "Hungary",
            12: "Belgium (Spa)",
            13: "Netherlands (Zandvoort)",
            14: "Italy (Monza)",
            15: "Singapore",
            16: "Japan (Suzuka)",
            17: "Qatar",
            18: "USA (Austin)",
            19: "Mexico",
            20: "Brazil (Interlagos)",
            21: "Las Vegas",
            22: "Abu Dhabi",
            23: "Saudi Arabia (Jeddah)"
        }
        
        return track_names.get(track_id, f"Unknown Track ({track_id})")
    
    @staticmethod
    def get_driver_name_from_telemetry(driver_name_bytes: bytes) -> str:
        """
        Converteer driver naam uit telemetry packet naar string
        
        Args:
            driver_name_bytes: Raw bytes van driver naam uit telemetry
            
        Returns:
            Schone driver naam string
        """
        try:
            # Probeer UTF-8 decoding
            name = driver_name_bytes.decode('utf-8').strip()
            # Verwijder null bytes
            name = name.replace('\x00', '').strip()
            
            # Als naam leeg is of alleen whitespace, geef default naam
            if not name:
                return "Unknown Driver"
                
            return name
            
        except UnicodeDecodeError:
            # Als UTF-8 faalt, probeer latin-1
            try:
                name = driver_name_bytes.decode('latin-1').strip()
                name = name.replace('\x00', '').strip()
                return name if name else "Unknown Driver"
            except:
                return "Unknown Driver"
    
    @staticmethod
    def calculate_consistency(lap_times: list) -> Dict[str, float]:
        """
        Bereken consistentie statistieken van een lijst rondetijden
        
        Args:
            lap_times: Lijst van rondetijden in seconden
            
        Returns:
            Dictionary met consistentie metrics (average, std_dev, coefficient_variation)
        """
        if not lap_times or len(lap_times) < 2:
            return {
                'average': 0.0,
                'std_dev': 0.0,
                'coefficient_variation': 0.0,
                'count': len(lap_times) if lap_times else 0
            }
        
        # Filter out invalid times (0 or negative)
        valid_times = [t for t in lap_times if t > 0]
        
        if len(valid_times) < 2:
            return {
                'average': 0.0,
                'std_dev': 0.0,
                'coefficient_variation': 0.0,
                'count': len(valid_times)
            }
        
        # Calculate average
        average = sum(valid_times) / len(valid_times)
        
        # Calculate standard deviation
        variance = sum((t - average) ** 2 for t in valid_times) / len(valid_times)
        std_dev = variance ** 0.5
        
        # Calculate coefficient of variation (relative standard deviation)
        coefficient_variation = (std_dev / average) * 100 if average > 0 else 0.0
        
        return {
            'average': round(average, 3),
            'std_dev': round(std_dev, 3),
            'coefficient_variation': round(coefficient_variation, 2),
            'count': len(valid_times)
        }
    
    @staticmethod
    def get_session_type_name(session_type: int) -> str:
        """
        Converteer session type ID naar leesbare naam
        
        Args:
            session_type: Numerieke session type uit telemetry
            
        Returns:
            Leesbare session type naam
        """
        session_types = {
            0: "Unknown",
            1: "P1",
            2: "P2", 
            3: "P3",
            4: "Short Practice",
            5: "Q1",
            6: "Q2",
            7: "Q3",
            8: "Short Qualifying", 
            9: "OSQ",
            10: "R",
            11: "R2",
            12: "R3",
            13: "Time Trial"
        }
        
        return session_types.get(session_type, f"Unknown ({session_type})")


class LapDataProcessor:
    """
    Processor voor lap data uit F1 25 telemetry
    """
    
    def __init__(self):
        """Initialiseer lap data processor"""
        self.logger = logging.getLogger(__name__)
        self.utils = TelemetryUtils()
    
    def process_lap_data(self, lap_data: Any, driver_name: str, track_name: str) -> Optional[Dict[str, Any]]:
        """
        Verwerk lap data van een auto en return database-ready data
        
        Args:
            lap_data: LapData object uit telemetry packet
            driver_name: Naam van de bestuurder
            track_name: Naam van het circuit
            
        Returns:
            Dictionary met verwerkte lap data of None als ongeldig
        """
        try:
            # Check of er een geldige laatste rondetijd is
            if not hasattr(lap_data, 'last_lap_time_ms') or lap_data.last_lap_time_ms <= 0:
                return None
            
            # Check geldigheid van de rondetijd
            if not self.utils.is_valid_lap_time(lap_data.last_lap_time_ms):
                self.logger.debug(f"Ongeldige rondetijd: {lap_data.last_lap_time_ms}ms voor {driver_name}")
                return None
            
            # Converteer tijden naar seconden
            lap_time = self.utils.convert_ms_to_seconds(lap_data.last_lap_time_ms)
            
            # Verwerk sector tijden
            sector1_time = None
            sector2_time = None
            sector3_time = None
            
            if (hasattr(lap_data, 'sector1_time_ms_part') and hasattr(lap_data, 'sector1_time_minutes_part') and
                self.utils.is_valid_sector_time(lap_data.sector1_time_ms_part, lap_data.sector1_time_minutes_part)):
                sector1_time = self.utils.convert_sector_time_to_seconds(
                    lap_data.sector1_time_ms_part, lap_data.sector1_time_minutes_part
                )
            
            if (hasattr(lap_data, 'sector2_time_ms_part') and hasattr(lap_data, 'sector2_time_minutes_part') and
                self.utils.is_valid_sector_time(lap_data.sector2_time_ms_part, lap_data.sector2_time_minutes_part)):
                sector2_time = self.utils.convert_sector_time_to_seconds(
                    lap_data.sector2_time_ms_part, lap_data.sector2_time_minutes_part
                )
            
            # Check of lap invalid is (als dat veld bestaat)
            is_valid = True
            if hasattr(lap_data, 'current_lap_invalid'):
                is_valid = lap_data.current_lap_invalid == 0  # 0 = valid, 1 = invalid
            
            # Maak resultaat dictionary
            result = {
                'driver_name': driver_name,
                'lap_time': lap_time,
                'track_name': track_name,
                'sector1_time': sector1_time,
                'sector2_time': sector2_time,
                'sector3_time': sector3_time,
                'is_valid': is_valid,
                'session_date': datetime.now()
            }
            
            self.logger.debug(f"Lap data verwerkt voor {driver_name}: {self.utils.format_lap_time(lap_time)}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Fout bij verwerken lap data voor {driver_name}: {e}")
            return None