"""
F1 25 Telemetry System - Data Validator
Validatie van telemetry data en input parameters
"""

from typing import Optional, Any
from services import logger_service

class DataValidator:
    """
    Validator voor telemetry data en input parameters
    """
    
    def __init__(self):
        """Initialiseer data validator"""
        self.logger = logger_service.get_logger('DataValidator')
    
    def validate_car_index(self, car_index: int) -> bool:
        """
        Valideer car index (0-21)
        
        Args:
            car_index: Car index
            
        Returns:
            True als valide
        """
        if not isinstance(car_index, int):
            self.logger.warning(f"Car index is geen integer: {type(car_index)}")
            return False
        
        if not 0 <= car_index <= 21:
            self.logger.warning(f"Car index buiten bereik: {car_index}")
            return False
        
        return True
    
    def validate_lap_time(self, lap_time_ms: int) -> bool:
        """
        Valideer lap tijd (redelijke range)
        
        Args:
            lap_time_ms: Lap tijd in milliseconden
            
        Returns:
            True als valide
        """
        if not isinstance(lap_time_ms, int):
            return False
        
        # Lap tijd tussen 1 seconde en 10 minuten
        if not 1000 <= lap_time_ms <= 600000:
            self.logger.warning(f"Lap tijd onrealistisch: {lap_time_ms}ms")
            return False
        
        return True
    
    def validate_sector_time(self, sector_time_ms: int) -> bool:
        """
        Valideer sector tijd (redelijke range)
        
        Args:
            sector_time_ms: Sector tijd in milliseconden
            
        Returns:
            True als valide
        """
        if not isinstance(sector_time_ms, int):
            return False
        
        # Sector tijd tussen 0.5 seconde en 3 minuten
        if not 500 <= sector_time_ms <= 180000:
            self.logger.warning(f"Sector tijd onrealistisch: {sector_time_ms}ms")
            return False
        
        return True
    
    def validate_speed(self, speed_kmh: int) -> bool:
        """
        Valideer snelheid
        
        Args:
            speed_kmh: Snelheid in km/h
            
        Returns:
            True als valide
        """
        if not isinstance(speed_kmh, int):
            return False
        
        # Snelheid tussen 0 en 400 km/h
        if not 0 <= speed_kmh <= 400:
            self.logger.warning(f"Snelheid buiten bereik: {speed_kmh} km/h")
            return False
        
        return True
    
    def validate_rpm(self, rpm: int) -> bool:
        """
        Valideer RPM
        
        Args:
            rpm: Engine RPM
            
        Returns:
            True als valide
        """
        if not isinstance(rpm, int):
            return False
        
        # RPM tussen 0 en 20000
        if not 0 <= rpm <= 20000:
            self.logger.warning(f"RPM buiten bereik: {rpm}")
            return False
        
        return True
    
    def validate_gear(self, gear: int) -> bool:
        """
        Valideer versnelling
        
        Args:
            gear: Versnelling (-1 = reverse, 0 = neutral, 1-8)
            
        Returns:
            True als valide
        """
        if not isinstance(gear, int):
            return False
        
        # Gear tussen -1 en 8
        if not -1 <= gear <= 8:
            self.logger.warning(f"Gear buiten bereik: {gear}")
            return False
        
        return True
    
    def validate_percentage(self, value: float) -> bool:
        """
        Valideer percentage waarde (0.0 - 1.0)
        
        Args:
            value: Waarde tussen 0.0 en 1.0
            
        Returns:
            True als valide
        """
        if not isinstance(value, (int, float)):
            return False
        
        if not 0.0 <= value <= 1.0:
            self.logger.warning(f"Percentage buiten bereik: {value}")
            return False
        
        return True
    
    def validate_temperature(self, temp_celsius: int) -> bool:
        """
        Valideer temperatuur
        
        Args:
            temp_celsius: Temperatuur in Celsius
            
        Returns:
            True als valide
        """
        if not isinstance(temp_celsius, int):
            return False
        
        # Temperatuur tussen -50 en 150 graden
        if not -50 <= temp_celsius <= 150:
            self.logger.warning(f"Temperatuur buiten bereik: {temp_celsius}°C")
            return False
        
        return True
    
    def validate_session_uid(self, session_uid: int) -> bool:
        """
        Valideer session UID
        
        Args:
            session_uid: Session unique identifier
            
        Returns:
            True als valide
        """
        if not isinstance(session_uid, int):
            self.logger.warning(f"Session UID is geen integer: {type(session_uid)}")
            return False
        
        if session_uid < 0:
            self.logger.warning(f"Session UID negatief: {session_uid}")
            return False
        
        return True
    
    def validate_track_id(self, track_id: int) -> bool:
        """
        Valideer track ID
        
        Args:
            track_id: Track identifier
            
        Returns:
            True als valide
        """
        if not isinstance(track_id, int):
            return False
        
        # Track IDs tussen 0 en 50 (met ruimte voor nieuwe tracks)
        if not 0 <= track_id <= 50:
            self.logger.warning(f"Track ID buiten bereik: {track_id}")
            return False
        
        return True
    
    def validate_lap_number(self, lap_number: int) -> bool:
        """
        Valideer lap nummer
        
        Args:
            lap_number: Lap nummer
            
        Returns:
            True als valide
        """
        if not isinstance(lap_number, int):
            return False
        
        # Lap nummer tussen 1 en 200
        if not 1 <= lap_number <= 200:
            self.logger.warning(f"Lap nummer buiten bereik: {lap_number}")
            return False
        
        return True
    
    def validate_lap_data(self, lap_data: dict) -> bool:
        """
        Valideer complete lap data dict
        
        Args:
            lap_data: Lap data dictionary
            
        Returns:
            True als alle velden valide zijn
        """
        required_fields = [
            'session_id', 'car_index', 'lap_number', 'lap_time_ms'
        ]
        
        # Check verplichte velden
        for field in required_fields:
            if field not in lap_data:
                self.logger.warning(f"Verplicht veld ontbreekt: {field}")
                return False
        
        # Valideer individuele velden
        if not self.validate_car_index(lap_data['car_index']):
            return False
        
        if not self.validate_lap_number(lap_data['lap_number']):
            return False
        
        if lap_data['lap_time_ms'] > 0:
            if not self.validate_lap_time(lap_data['lap_time_ms']):
                return False
        
        # Valideer sectortijden indien aanwezig
        if 'sector1_ms' in lap_data and lap_data['sector1_ms'] > 0:
            if not self.validate_sector_time(lap_data['sector1_ms']):
                return False
        
        if 'sector2_ms' in lap_data and lap_data['sector2_ms'] > 0:
            if not self.validate_sector_time(lap_data['sector2_ms']):
                return False
        
        if 'sector3_ms' in lap_data and lap_data['sector3_ms'] > 0:
            if not self.validate_sector_time(lap_data['sector3_ms']):
                return False
        
        return True
    
    def validate_telemetry_data(self, telemetry_data: dict) -> bool:
        """
        Valideer complete telemetry data dict
        
        Args:
            telemetry_data: Telemetry data dictionary
            
        Returns:
            True als alle velden valide zijn
        """
        required_fields = ['session_id', 'car_index']
        
        # Check verplichte velden
        for field in required_fields:
            if field not in telemetry_data:
                self.logger.warning(f"Verplicht veld ontbreekt: {field}")
                return False
        
        # Valideer car index
        if not self.validate_car_index(telemetry_data['car_index']):
            return False
        
        # Valideer optionele velden
        if 'speed' in telemetry_data:
            if not self.validate_speed(telemetry_data['speed']):
                return False
        
        if 'rpm' in telemetry_data:
            if not self.validate_rpm(telemetry_data['rpm']):
                return False
        
        if 'gear' in telemetry_data:
            if not self.validate_gear(telemetry_data['gear']):
                return False
        
        if 'throttle' in telemetry_data:
            if not self.validate_percentage(telemetry_data['throttle']):
                return False
        
        if 'brake' in telemetry_data:
            if not self.validate_percentage(telemetry_data['brake']):
                return False
        
        return True
    
    def sanitize_string(self, input_string: str, max_length: int = 100) -> str:
        """
        Sanitize string input (remove control characters, limit length)
        
        Args:
            input_string: Input string
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not isinstance(input_string, str):
            return ""
        
        # Remove control characters
        sanitized = ''.join(char for char in input_string if char.isprintable())
        
        # Trim to max length
        sanitized = sanitized[:max_length]
        
        return sanitized.strip()


# Singleton instance
data_validator = DataValidator()