"""
F1 25 Telemetry - Packet Header
Bevat de PacketHeader klasse die in elk packet zit
"""

import struct
from dataclasses import dataclass
from packet_types import PacketID

@dataclass
class PacketHeader:
    """
    Header die in elk packet zit (29 bytes)
    
    Attributes:
        packet_format: 2025 voor F1 25
        game_year: Laatste 2 cijfers van jaar (25)
        game_major_version: Major version (X.00)
        game_minor_version: Minor version (1.XX)
        packet_version: Versie van dit packet type
        packet_id: Packet type ID (zie PacketID enum)
        session_uid: Unieke sessie identifier
        session_time: Sessie timestamp in seconden
        frame_identifier: Frame nummer
        overall_frame_identifier: Overall frame nummer (gaat niet terug na flashback)
        player_car_index: Index van speler in array
        secondary_player_car_index: Index tweede speler (splitscreen), 255 als geen tweede speler
    """
    packet_format: int
    game_year: int
    game_major_version: int
    game_minor_version: int
    packet_version: int
    packet_id: int
    session_uid: int
    session_time: float
    frame_identifier: int
    overall_frame_identifier: int
    player_car_index: int
    secondary_player_car_index: int
    
    @classmethod
    def from_bytes(cls, data: bytes):
        """
        Parse header uit bytes
        
        Args:
            data: Byte array met minimaal 29 bytes
            
        Returns:
            PacketHeader instance
        """
        # Format: <HBBBBBQfIIBB = 29 bytes
        # < = little endian
        # H = uint16, B = uint8, Q = uint64, f = float, I = uint32
        unpacked = struct.unpack('<HBBBBBQfIIBB', data[:29])
        return cls(*unpacked)
    
    def is_valid(self) -> bool:
        """
        Controleer of header geldig is voor F1 25
        
        Returns:
            True als packet format 2025 is
        """
        return self.packet_format == 2025
    
    def get_packet_type_name(self) -> str:
        """
        Krijg leesbare naam van packet type
        
        Returns:
            Naam van packet type (bijv. "MOTION", "SESSION")
        """
        try:
            return PacketID(self.packet_id).name
        except ValueError:
            return f"UNKNOWN_{self.packet_id}"
    
    def __str__(self):
        return (f"PacketHeader(type={self.get_packet_type_name()}, "
                f"session_time={self.session_time:.2f}s, "
                f"frame={self.frame_identifier}, "
                f"player_idx={self.player_car_index})")
    
    def __repr__(self):
        return self.__str__()