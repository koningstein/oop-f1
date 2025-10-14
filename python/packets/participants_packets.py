"""
F1 25 Telemetry - Participants & Lobby Packets
Bevat Participants en LobbyInfo packet parsers
"""

import struct
from dataclasses import dataclass
from typing import List, Tuple
from packet_header import PacketHeader
from packet_types import MAX_CARS, TeamID, MAX_PARTICIPANT_NAME_LENGTH

@dataclass
class ParticipantData:
    """
    Data voor 1 deelnemer
    """
    ai_controlled: int  # 0 = human, 1 = AI
    driver_id: int  # 255 als network human
    network_id: int
    team_id: int
    my_team: int  # 1 = My Team, 0 = anders
    race_number: int
    nationality: int
    name: str
    your_telemetry: int  # 0 = restricted, 1 = public
    show_online_names: int  # 0 = off, 1 = on
    tech_level: int
    platform: int  # 1=Steam, 3=PS, 4=Xbox, 6=Origin, 255=unknown
    num_colours: int
    livery_colours: List[Tuple[int, int, int]]  # RGB values
    
    def get_team_name(self) -> str:
        """Krijg team naam"""
        try:
            return TeamID(self.team_id).name
        except ValueError:
            return f"UNKNOWN_TEAM_{self.team_id}"
    
    def is_human(self) -> bool:
        """Check of deelnemer een mens is"""
        return self.ai_controlled == 0
    
    def get_platform_name(self) -> str:
        """Krijg platform naam"""
        platforms = {
            1: "Steam",
            3: "PlayStation",
            4: "Xbox",
            6: "Origin",
            255: "Unknown"
        }
        return platforms.get(self.platform, f"Unknown_{self.platform}")

class ParticipantsPacket:
    """
    Packet ID: 4 - Participants Data
    Frequentie: Elke 5 seconden
    
    Lijst van deelnemers in sessie (vooral relevant voor multiplayer)
    """
    
    def __init__(self, header: PacketHeader, data: bytes):
        self.header = header
        offset = 29
        
        # Aantal actieve auto's
        self.num_active_cars = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        
        self.participants: List[ParticipantData] = []
        
        for i in range(MAX_CARS):
            if offset + 56 <= len(data):
                # Parse participant data
                ai_controlled = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                driver_id = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                network_id = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                team_id = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                my_team = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                race_number = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                nationality = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                
                # Naam (32 bytes UTF-8)
                name_bytes = data[offset:offset+32]
                name = name_bytes.decode('utf-8', errors='ignore').rstrip('\x00')
                offset += 32
                
                your_telemetry = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                show_online_names = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                tech_level = struct.unpack('<H', data[offset:offset+2])[0]
                offset += 2
                ready_status = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                
                lobby_player = LobbyInfoData(
                    ai_controlled, team_id, nationality, platform,
                    name, car_number, your_telemetry, show_online_names,
                    tech_level, ready_status
                )
                self.lobby_players.append(lobby_player)
    
    def get_ready_players(self) -> List[Tuple[int, LobbyInfoData]]:
        """
        Krijg alle spelers die ready zijn
        
        Returns:
            List van (player_index, LobbyInfoData) tuples
        """
        ready = []
        for i in range(self.num_players):
            if i < len(self.lobby_players) and self.lobby_players[i].is_ready():
                ready.append((i, self.lobby_players[i]))
        return ready
    
    def get_not_ready_players(self) -> List[Tuple[int, LobbyInfoData]]:
        """
        Krijg alle spelers die nog niet ready zijn
        
        Returns:
            List van (player_index, LobbyInfoData) tuples
        """
        not_ready = []
        for i in range(self.num_players):
            if i < len(self.lobby_players) and not self.lobby_players[i].is_ready() and not self.lobby_players[i].is_spectating():
                not_ready.append((i, self.lobby_players[i]))
        return not_ready
    
    def all_players_ready(self) -> bool:
        """Check of alle spelers ready zijn (exclusief spectators)"""
        for i in range(self.num_players):
            if i < len(self.lobby_players):
                player = self.lobby_players[i]
                if not player.is_spectating() and not player.is_ready():
                    return False
        return True
    
    def __str__(self):
        ready = len(self.get_ready_players())
        not_ready = len(self.get_not_ready_players())
        return f"LobbyInfo(players={self.num_players}, ready={ready}, not_ready={not_ready})"
                tech_level = struct.unpack('<H', data[offset:offset+2])[0]
                offset += 2
                platform = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                num_colours = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                
                # Livery colours (4 RGB sets)
                livery_colours = []
                for c in range(4):
                    r = struct.unpack('<B', data[offset:offset+1])[0]
                    offset += 1
                    g = struct.unpack('<B', data[offset:offset+1])[0]
                    offset += 1
                    b = struct.unpack('<B', data[offset:offset+1])[0]
                    offset += 1
                    livery_colours.append((r, g, b))
                
                participant = ParticipantData(
                    ai_controlled, driver_id, network_id, team_id,
                    my_team, race_number, nationality, name,
                    your_telemetry, show_online_names, tech_level,
                    platform, num_colours, livery_colours
                )
                self.participants.append(participant)
    
    def get_player_participant(self) -> ParticipantData:
        """Krijg participant data van speler"""
        return self.participants[self.header.player_car_index]
    
    def get_human_players(self) -> List[Tuple[int, ParticipantData]]:
        """
        Krijg alle menselijke spelers
        
        Returns:
            List van (car_index, ParticipantData) tuples
        """
        humans = []
        for i in range(self.num_active_cars):
            if i < len(self.participants) and self.participants[i].is_human():
                humans.append((i, self.participants[i]))
        return humans
    
    def get_ai_drivers(self) -> List[Tuple[int, ParticipantData]]:
        """
        Krijg alle AI rijders
        
        Returns:
            List van (car_index, ParticipantData) tuples
        """
        ai_drivers = []
        for i in range(self.num_active_cars):
            if i < len(self.participants) and not self.participants[i].is_human():
                ai_drivers.append((i, self.participants[i]))
        return ai_drivers
    
    def __str__(self):
        humans = len(self.get_human_players())
        ai = len(self.get_ai_drivers())
        return f"Participants(total={self.num_active_cars}, humans={humans}, AI={ai})"

@dataclass
class LobbyInfoData:
    """
    Data voor 1 speler in lobby
    """
    ai_controlled: int
    team_id: int  # 255 als geen team geselecteerd
    nationality: int
    platform: int
    name: str
    car_number: int
    your_telemetry: int
    show_online_names: int
    tech_level: int
    ready_status: int  # 0=not ready, 1=ready, 2=spectating
    
    def get_team_name(self) -> str:
        """Krijg team naam"""
        if self.team_id == 255:
            return "NO_TEAM"
        try:
            return TeamID(self.team_id).name
        except ValueError:
            return f"UNKNOWN_TEAM_{self.team_id}"
    
    def is_ready(self) -> bool:
        """Check of speler klaar is"""
        return self.ready_status == 1
    
    def is_spectating(self) -> bool:
        """Check of speler aan het spectaten is"""
        return self.ready_status == 2
    
    def get_platform_name(self) -> str:
        """Krijg platform naam"""
        platforms = {
            1: "Steam",
            3: "PlayStation",
            4: "Xbox",
            6: "Origin",
            255: "Unknown"
        }
        return platforms.get(self.platform, f"Unknown_{self.platform}")

class LobbyInfoPacket:
    """
    Packet ID: 9 - Lobby Info
    Frequentie: 2 per seconde (in lobby)
    
    Details over spelers in multiplayer lobby
    """
    
    def __init__(self, header: PacketHeader, data: bytes):
        self.header = header
        offset = 29
        
        # Aantal spelers
        self.num_players = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        
        self.lobby_players: List[LobbyInfoData] = []
        
        for i in range(MAX_CARS):
            if offset + 43 <= len(data):
                ai_controlled = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                team_id = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                nationality = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                platform = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                
                # Naam (32 bytes UTF-8)
                name_bytes = data[offset:offset+32]
                name = name_bytes.decode('utf-8', errors='ignore').rstrip('\x00')
                offset += 32
                
                car_number = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                your_telemetry = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                show_online_names = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1