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
    """
    Dataclass for participant data.
    (Versie 3: Correcte F1 25 velden MET default waarden)
    """
    # Velden uit jouw F1 25 implementatie
    ai_controlled: bool = False
    driver_id: int = 0
    network_id: int = 0
    team_id: int = 0
    my_team: bool = False
    race_number: int = 0
    nationality: int = 0
    name: str = ""
    your_telemetry: bool = False
    show_online_names: bool = False
    tech_level: int = 0
    platform: int = 0  # Nieuw in F1 25
    colour1: int = 0  # Nieuw in F1 25
    colour2: int = 0  # Nieuw in F1 25
    colour3: int = 0  # Nieuw in F1 25

    # Jouw correcte PACKET_FORMAT en LEN
    PACKET_FORMAT = "<?BBB?B B 32s B? HBBBB"  # 48 bytes
    PACKET_LEN = 48

    @staticmethod
    def from_bytes(data: bytes) -> 'ParticipantData':
        """
        Unpackt bytes naar een ParticipantData object
        (Deze code komt 1:1 uit jouw bronbestand)
        """
        try:
            (
                ai_controlled, driver_id, network_id, team_id, my_team,
                race_number, nationality, name_bytes, your_telemetry,
                show_online_names, tech_level, platform, colour1, colour2, colour3
            ) = struct.unpack(ParticipantData.PACKET_FORMAT, data)

            # Decodeer de naam
            name = name_bytes.decode('utf-8').rstrip('\x00')

            return ParticipantData(
                ai_controlled=ai_controlled,
                driver_id=driver_id,
                network_id=network_id,
                team_id=team_id,
                my_team=my_team,
                race_number=race_number,
                nationality=nationality,
                name=name,
                your_telemetry=your_telemetry,
                show_online_names=show_online_names,
                tech_level=tech_level,
                platform=platform,
                colour1=colour1,
                colour2=colour2,
                colour3=colour3
            )
        except struct.error as e:
            # Vang unpack error op als data corrupt of te kort is
            print(f"[FOUT] Kon ParticipantData niet unpacken: {e}")
            return ParticipantData()  # Retourneer een leeg object

    def get_name(self) -> str:
        """
        Retourneer de naam van de deelnemer (veilig).
        (Deze code komt 1:1 uit jouw bronbestand)
        """
        return self.name

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