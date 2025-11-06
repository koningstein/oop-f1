"""
F1 25 Telemetry - Participants Parser
Parse Participants packet (ID 4) met driver en team informatie
"""

from dataclasses import dataclass
from typing import Optional, List
from .base_parser import BaseParser
from .packet_header import PacketHeader

@dataclass
class ParticipantData:
    """Data voor één participant/driver"""
    ai_controlled: bool
    driver_id: int
    network_id: int
    team_id: int
    my_team: bool
    race_number: int
    nationality: int
    name: str
    your_telemetry: bool
    show_online_names: bool
    tech_level: int
    platform: int
    colour1: int
    colour2: int
    colour3: int

@dataclass
class ParticipantsPacket:
    """Complete participants packet"""
    header: PacketHeader
    num_active_cars: int
    participants: List[ParticipantData]

class ParticipantsParser(BaseParser):
    """Parser voor Participants packets (ID 4)"""
    
    # Format voor één ParticipantData
    # aiControlled(1) + driverId(1) + networkId(1) + teamId(1) + myTeam(1) + 
    # raceNumber(1) + nationality(1) + name(32) + yourTelemetry(1) + 
    # showOnlineNames(1) + techLevel(2) + platform(1) + colours(3) = 47 bytes
    PARTICIPANT_FORMAT = "<BBBBBBBB32sBBHBBBB"
    
    def parse(self, header: PacketHeader, payload: bytes) -> Optional[ParticipantsPacket]:
        """
        Parse participants packet
        
        Args:
            header: Packet header
            payload: Packet payload
            
        Returns:
            ParticipantsPacket object of None
        """
        expected_size = 1 + (47 * 22)  # 1 byte voor num_active + 22 participants
        if not self.validate_payload_size(payload, expected_size):
            return None
        
        try:
            # Parse aantal actieve auto's
            num_active_cars = payload[0]
            
            if num_active_cars > 22:
                self.logger.warning(f"Ongeldig aantal actieve auto's: {num_active_cars}")
                num_active_cars = 22
            
            participants = []
            offset = 1
            
            # Parse alle 22 participants
            for car_idx in range(22):
                unpacked = self.unpack_safely(self.PARTICIPANT_FORMAT, payload, offset)
                if not unpacked:
                    self.logger.warning(f"Fout bij parsen participant {car_idx}")
                    break
                
                # Parse naam (32 bytes, null-terminated)
                name = self.parse_string(payload, offset + 7, 32)
                
                participant = ParticipantData(
                    ai_controlled=bool(unpacked[0]),
                    driver_id=unpacked[1],
                    network_id=unpacked[2],
                    team_id=unpacked[3],
                    my_team=bool(unpacked[4]),
                    race_number=unpacked[5],
                    nationality=unpacked[6],
                    name=name,
                    your_telemetry=bool(unpacked[8]),
                    show_online_names=bool(unpacked[9]),
                    tech_level=unpacked[10],
                    platform=unpacked[11],
                    colour1=unpacked[12],
                    colour2=unpacked[13],
                    colour3=unpacked[14]
                )
                
                participants.append(participant)
                offset += 47
            
            self.logger.debug(f"Parsed {len(participants)} participants, {num_active_cars} actief")
            
            return ParticipantsPacket(
                header=header,
                num_active_cars=num_active_cars,
                participants=participants
            )
            
        except Exception as e:
            self.logger.error(f"Participants parse fout: {e}")
            return None