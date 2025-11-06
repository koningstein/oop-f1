"""
F1 25 Telemetry - Packet Header Parser
Parse de header van elk UDP packet
"""

import struct
from dataclasses import dataclass
from typing import Optional
from parsers.packet_types import PACKET_FORMAT_2025, GAME_YEAR

@dataclass
class PacketHeader:
    """
    Packet Header structuur (29 bytes)
    Elke packet begint met deze header
    """
    packet_format: int          # 2025 voor F1 25
    game_year: int             # 25
    game_major_version: int    # Major version
    game_minor_version: int    # Minor version
    packet_version: int        # Versie van dit packet type
    packet_id: int             # Type packet (0-15)
    session_uid: int           # Unieke sessie identifier
    session_time: float        # Sessie tijd in seconden
    frame_identifier: int      # Frame nummer
    overall_frame_identifier: int  # Overall frame (gaat niet terug na flashback)
    player_car_index: int      # Index van speler auto (0-21)
    secondary_player_car_index: int  # Tweede speler (splitscreen), 255 = geen
    
    # Header format: "<HBBBBBQfIIBB" = 29 bytes
    HEADER_FORMAT = "<HBBBBBQfIIBB"
    HEADER_SIZE = 29
    
    @classmethod
    def from_bytes(cls, data: bytes) -> Optional['PacketHeader']:
        """
        Parse header van raw bytes
        
        Args:
            data: Raw packet data (minimaal 29 bytes)
            
        Returns:
            PacketHeader object of None bij fout
        """
        if len(data) < cls.HEADER_SIZE:
            return None
        
        try:
            unpacked = struct.unpack(cls.HEADER_FORMAT, data[:cls.HEADER_SIZE])
            
            return cls(
                packet_format=unpacked[0],
                game_year=unpacked[1],
                game_major_version=unpacked[2],
                game_minor_version=unpacked[3],
                packet_version=unpacked[4],
                packet_id=unpacked[5],
                session_uid=unpacked[6],
                session_time=unpacked[7],
                frame_identifier=unpacked[8],
                overall_frame_identifier=unpacked[9],
                player_car_index=unpacked[10],
                secondary_player_car_index=unpacked[11]
            )
        except struct.error:
            return None
    
    def is_valid(self) -> bool:
        """
        Controleer of header valide is voor F1 25
        
        Returns:
            bool: True als header correct is
        """
        return (
            self.packet_format == PACKET_FORMAT_2025 and
            self.game_year == GAME_YEAR and
            0 <= self.packet_id <= 15 and
            0 <= self.player_car_index <= 21
        )
    
    def get_payload(self, data: bytes) -> bytes:
        """
        Verkrijg packet data zonder header
        
        Args:
            data: Volledige packet data
            
        Returns:
            bytes: Payload zonder header
        """
        return data[self.HEADER_SIZE:]
    
    def __repr__(self) -> str:
        """String representatie voor debugging"""
        return (
            f"PacketHeader(id={self.packet_id}, "
            f"session={self.session_uid}, "
            f"time={self.session_time:.2f}s, "
            f"player_car={self.player_car_index})"
        )