"""
F1 25 Telemetry - Base Parser
Basis klasse voor alle packet parsers met gemeenschappelijke functionaliteit
"""

import struct
from abc import ABC, abstractmethod
from typing import Optional, Any
from .packet_header import PacketHeader
import logging

class BaseParser(ABC):
    """
    Abstract base class voor alle packet parsers
    Bevat gemeenschappelijke parsing functionaliteit
    """
    
    def __init__(self):
        """Initialiseer parser"""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def parse(self, header: PacketHeader, payload: bytes) -> Optional[Any]:
        """
        Parse packet payload
        Moet geïmplementeerd worden door subklassen
        
        Args:
            header: Parsed packet header
            payload: Packet data zonder header
            
        Returns:
            Parsed data object of None bij fout
        """
        pass
    
    def unpack_safely(self, format_string: str, data: bytes, offset: int = 0) -> Optional[tuple]:
        """
        Veilig unpack van binary data met error handling
        
        Args:
            format_string: Struct format string
            data: Binary data
            offset: Start offset in data
            
        Returns:
            Tuple met unpacked data of None bij fout
        """
        try:
            size = struct.calcsize(format_string)
            if offset + size > len(data):
                self.logger.warning(
                    f"Data te kort: verwacht {offset + size} bytes, kreeg {len(data)}"
                )
                return None
            
            return struct.unpack_from(format_string, data, offset)
        except struct.error as e:
            self.logger.error(f"Struct unpack error: {e}")
            return None
    
    def parse_string(self, data: bytes, offset: int, length: int) -> str:
        """
        Parse string van binary data (null-terminated)
        
        Args:
            data: Binary data
            offset: Start offset
            length: Maximum lengte van string
            
        Returns:
            Decoded string
        """
        try:
            string_bytes = data[offset:offset + length]
            # Zoek null terminator
            null_pos = string_bytes.find(b'\x00')
            if null_pos >= 0:
                string_bytes = string_bytes[:null_pos]
            return string_bytes.decode('utf-8', errors='ignore')
        except Exception as e:
            self.logger.warning(f"String parse fout: {e}")
            return ""
    
    def validate_car_index(self, car_index: int) -> bool:
        """
        Valideer of car index binnen bereik is
        
        Args:
            car_index: Index van auto (0-21)
            
        Returns:
            bool: True als valide
        """
        return 0 <= car_index <= 21
    
    def validate_payload_size(self, payload: bytes, expected_size: int) -> bool:
        """
        Valideer of payload de verwachte grootte heeft
        
        Args:
            payload: Packet payload
            expected_size: Verwachte grootte in bytes
            
        Returns:
            bool: True als grootte correct is
        """
        if len(payload) < expected_size:
            self.logger.warning(
                f"Payload te klein: verwacht {expected_size} bytes, kreeg {len(payload)}"
            )
            return False
        return True
    
    def ms_to_time_string(self, milliseconds: int) -> str:
        """
        Converteer milliseconden naar tijd string (mm:ss.mmm)
        
        Args:
            milliseconds: Tijd in milliseconden
            
        Returns:
            str: Geformateerde tijd string
        """
        if milliseconds == 0 or milliseconds > 3600000:  # > 1 uur
            return "--:--.---"
        
        total_seconds = milliseconds / 1000
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        
        return f"{minutes:02d}:{seconds:06.3f}"
    
    def parse_array(self, format_string: str, data: bytes, offset: int, count: int) -> list:
        """
        Parse array van structs
        
        Args:
            format_string: Struct format voor één item
            data: Binary data
            offset: Start offset
            count: Aantal items
            
        Returns:
            List met unpacked items
        """
        item_size = struct.calcsize(format_string)
        items = []
        
        for i in range(count):
            item_offset = offset + (i * item_size)
            unpacked = self.unpack_safely(format_string, data, item_offset)
            if unpacked:
                items.append(unpacked)
            else:
                self.logger.warning(f"Fout bij parsen array item {i}")
                break
        
        return items