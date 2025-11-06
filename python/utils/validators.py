"""
F1 25 Telemetry System - Validators
Utility functies voor input validatie
"""

from typing import Any

def is_valid_car_index(car_index: Any) -> bool:
    """
    Check of car index geldig is (0-21)
    
    Args:
        car_index: Car index waarde
        
    Returns:
        True als geldig
    """
    if not isinstance(car_index, int):
        return False
    return 0 <= car_index <= 21

def is_valid_lap_number(lap_number: Any) -> bool:
    """
    Check of lap nummer geldig is (1-200)
    
    Args:
        lap_number: Lap nummer
        
    Returns:
        True als geldig
    """
    if not isinstance(lap_number, int):
        return False
    return 1 <= lap_number <= 200

def is_valid_speed(speed: Any) -> bool:
    """
    Check of snelheid geldig is (0-400 km/h)
    
    Args:
        speed: Snelheid in km/h
        
    Returns:
        True als geldig
    """
    if not isinstance(speed, (int, float)):
        return False
    return 0 <= speed <= 400

def is_valid_rpm(rpm: Any) -> bool:
    """
    Check of RPM geldig is (0-20000)
    
    Args:
        rpm: Engine RPM
        
    Returns:
        True als geldig
    """
    if not isinstance(rpm, int):
        return False
    return 0 <= rpm <= 20000

def is_valid_gear(gear: Any) -> bool:
    """
    Check of versnelling geldig is (-1 tot 8)
    
    Args:
        gear: Versnelling (-1=R, 0=N, 1-8)
        
    Returns:
        True als geldig
    """
    if not isinstance(gear, int):
        return False
    return -1 <= gear <= 8

def is_valid_percentage(value: Any) -> bool:
    """
    Check of percentage waarde geldig is (0.0-1.0)
    
    Args:
        value: Percentage waarde
        
    Returns:
        True als geldig
    """
    if not isinstance(value, (int, float)):
        return False
    return 0.0 <= value <= 1.0

def is_valid_temperature(temp: Any) -> bool:
    """
    Check of temperatuur geldig is (-50 tot 150°C)
    
    Args:
        temp: Temperatuur in Celsius
        
    Returns:
        True als geldig
    """
    if not isinstance(temp, (int, float)):
        return False
    return -50 <= temp <= 150

def is_valid_session_uid(session_uid: Any) -> bool:
    """
    Check of session UID geldig is (> 0)
    
    Args:
        session_uid: Session unique identifier
        
    Returns:
        True als geldig
    """
    if not isinstance(session_uid, int):
        return False
    return session_uid > 0

def is_valid_track_id(track_id: Any) -> bool:
    """
    Check of track ID geldig is (0-50)
    
    Args:
        track_id: Track identifier
        
    Returns:
        True als geldig
    """
    if not isinstance(track_id, int):
        return False
    return 0 <= track_id <= 50

def is_valid_session_type(session_type: Any) -> bool:
    """
    Check of session type geldig is (0-13)
    
    Args:
        session_type: Session type ID
        
    Returns:
        True als geldig
    """
    if not isinstance(session_type, int):
        return False
    return 0 <= session_type <= 13

def is_valid_lap_time(lap_time_ms: Any) -> bool:
    """
    Check of lap tijd redelijk is (1s - 10min)
    
    Args:
        lap_time_ms: Lap tijd in milliseconden
        
    Returns:
        True als geldig
    """
    if not isinstance(lap_time_ms, int):
        return False
    return 1000 <= lap_time_ms <= 600000

def is_valid_sector_time(sector_time_ms: Any) -> bool:
    """
    Check of sector tijd redelijk is (0.5s - 3min)
    
    Args:
        sector_time_ms: Sector tijd in milliseconden
        
    Returns:
        True als geldig
    """
    if not isinstance(sector_time_ms, int):
        return False
    return 500 <= sector_time_ms <= 180000

def is_positive_integer(value: Any) -> bool:
    """
    Check of waarde een positief integer is
    
    Args:
        value: Te checken waarde
        
    Returns:
        True als positief integer
    """
    if not isinstance(value, int):
        return False
    return value > 0

def is_non_negative_integer(value: Any) -> bool:
    """
    Check of waarde een non-negatief integer is (>= 0)
    
    Args:
        value: Te checken waarde
        
    Returns:
        True als non-negatief integer
    """
    if not isinstance(value, int):
        return False
    return value >= 0

def is_valid_string(value: Any, min_length: int = 0, max_length: int = 1000) -> bool:
    """
    Check of waarde een geldige string is
    
    Args:
        value: Te checken waarde
        min_length: Minimale lengte
        max_length: Maximale lengte
        
    Returns:
        True als geldige string
    """
    if not isinstance(value, str):
        return False
    return min_length <= len(value) <= max_length

def is_valid_boolean(value: Any) -> bool:
    """
    Check of waarde een boolean is
    
    Args:
        value: Te checken waarde
        
    Returns:
        True als boolean
    """
    return isinstance(value, bool)

def validate_range(value: Any, min_value: float, max_value: float) -> bool:
    """
    Check of waarde binnen bereik valt
    
    Args:
        value: Te checken waarde
        min_value: Minimum waarde
        max_value: Maximum waarde
        
    Returns:
        True als binnen bereik
    """
    if not isinstance(value, (int, float)):
        return False
    return min_value <= value <= max_value

def sanitize_driver_name(name: str) -> str:
    """
    Sanitize driver naam (verwijder ongewenste characters)
    
    Args:
        name: Driver naam
        
    Returns:
        Gesanitizede naam
    """
    if not isinstance(name, str):
        return ""
    
    # Verwijder control characters en behoud alleen printable
    sanitized = ''.join(char for char in name if char.isprintable())
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    # Maximum lengte
    if len(sanitized) > 50:
        sanitized = sanitized[:50]
    
    return sanitized

def validate_packet_id(packet_id: Any) -> bool:
    """
    Check of packet ID geldig is (0-15)
    
    Args:
        packet_id: Packet ID
        
    Returns:
        True als geldig
    """
    if not isinstance(packet_id, int):
        return False
    return 0 <= packet_id <= 15