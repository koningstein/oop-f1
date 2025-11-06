"""
F1 25 Telemetry System - Time Formatter
Utilities voor tijd conversies en formatting
"""

def ms_to_time_string(milliseconds: int) -> str:
    """
    Converteer milliseconden naar tijd string (mm:ss.mmm)
    
    Args:
        milliseconds: Tijd in milliseconden
        
    Returns:
        str: Geformateerde tijd string
    """
    if milliseconds == 0 or milliseconds > 3600000:  # > 1 uur = invalide
        return "--:--.---"
    
    total_seconds = milliseconds / 1000
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60
    
    return f"{minutes:02d}:{seconds:06.3f}"

def ms_to_sector_string(milliseconds: int) -> str:
    """
    Converteer milliseconden naar sector tijd string (ss.mmm of mm:ss.mmm)
    
    Args:
        milliseconds: Tijd in milliseconden
        
    Returns:
        str: Geformateerde sector tijd
    """
    if milliseconds == 0:
        return "-.---"
    
    if milliseconds >= 60000:  # >= 1 minuut
        return ms_to_time_string(milliseconds)
    
    seconds = milliseconds / 1000
    return f"{seconds:6.3f}"

def seconds_to_time_string(seconds: float) -> str:
    """
    Converteer seconden naar tijd string (mm:ss)
    
    Args:
        seconds: Tijd in seconden
        
    Returns:
        str: Geformateerde tijd string
    """
    if seconds <= 0:
        return "--:--"
    
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    
    return f"{minutes:02d}:{secs:02d}"

def format_gap(gap_ms: int) -> str:
    """
    Formatteer gap/delta tijd
    
    Args:
        gap_ms: Gap in milliseconden (kan negatief zijn)
        
    Returns:
        str: Geformateerde gap (bijv. "+1.234" of "-0.567")
    """
    if gap_ms == 0:
        return "0.000"
    
    sign = "+" if gap_ms > 0 else ""
    gap_seconds = gap_ms / 1000
    
    return f"{sign}{gap_seconds:.3f}"

def format_speed(speed_kmh: int) -> str:
    """
    Formatteer snelheid
    
    Args:
        speed_kmh: Snelheid in km/h
        
    Returns:
        str: Geformateerde snelheid
    """
    return f"{speed_kmh:3d} km/h"

def format_percentage(value: float) -> str:
    """
    Formatteer percentage (0.0 - 1.0 naar 0% - 100%)
    
    Args:
        value: Waarde tussen 0.0 en 1.0
        
    Returns:
        str: Percentage string
    """
    percentage = int(value * 100)
    return f"{percentage:3d}%"

def format_temperature(temp_celsius: int) -> str:
    """
    Formatteer temperatuur
    
    Args:
        temp_celsius: Temperatuur in Celsius
        
    Returns:
        str: Geformateerde temperatuur
    """
    return f"{temp_celsius:3d}°C"