"""
F1 25 Telemetry - Lap Data Packets
Bevat LapData en LapPositions packet parsers
"""

import struct
from dataclasses import dataclass
from typing import List
from packet_header import PacketHeader
from packet_types import MAX_CARS, PitStatus, DriverStatus, ResultStatus

@dataclass
class LapData:
    """
    Lap data voor 1 auto
    
    Bevat rondetijden, sector tijden, positie, etc.
    """
    last_lap_time_ms: int
    current_lap_time_ms: int
    sector1_time_ms: int
    sector1_time_minutes: int
    sector2_time_ms: int
    sector2_time_minutes: int
    delta_to_car_in_front_ms: int
    delta_to_car_in_front_minutes: int
    delta_to_race_leader_ms: int
    delta_to_race_leader_minutes: int
    lap_distance: float
    total_distance: float
    safety_car_delta: float
    car_position: int
    current_lap_num: int
    pit_status: int
    num_pit_stops: int
    sector: int
    current_lap_invalid: int
    penalties: int
    total_warnings: int
    corner_cutting_warnings: int
    num_unserved_drive_through_pens: int
    num_unserved_stop_go_pens: int
    grid_position: int
    driver_status: int
    result_status: int
    pit_lane_timer_active: int
    pit_lane_time_in_lane_ms: int
    pit_stop_timer_ms: int
    pit_stop_should_serve_pen: int
    
    def get_last_lap_time_str(self) -> str:
        """Krijg laatste rondetijd als string (MM:SS.mmm)"""
        if self.last_lap_time_ms == 0:
            return "--:--.---"
        total_seconds = self.last_lap_time_ms / 1000
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:06.3f}"
    
    def get_current_lap_time_str(self) -> str:
        """Krijg huidige rondetijd als string"""
        if self.current_lap_time_ms == 0:
            return "--:--.---"
        total_seconds = self.current_lap_time_ms / 1000
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:06.3f}"
    
    def is_in_pit(self) -> bool:
        """Check of auto in pit is"""
        return self.pit_status in [PitStatus.PITTING, PitStatus.IN_PIT_AREA]
    
    def get_driver_status_name(self) -> str:
        """Krijg driver status naam"""
        try:
            return DriverStatus(self.driver_status).name
        except ValueError:
            return f"UNKNOWN_{self.driver_status}"
    
    def get_result_status_name(self) -> str:
        """Krijg result status naam"""
        try:
            return ResultStatus(self.result_status).name
        except ValueError:
            return f"UNKNOWN_{self.result_status}"


class LapDataPacket:
    """
    Packet ID: 2 - Lap Data
    Frequentie: Rate as specified in menus
    
    Data over alle rondetijden van auto's in sessie
    """
    
    def __init__(self, header: PacketHeader, data: bytes):
        self.header = header
        self.lap_data: List[LapData] = []
        
        offset = 29
        # Format string: EXACT 31 velden
        # II = 2, HBHBHBHB = 8, fff = 3, 15xB = 15, HHB = 3
        # Totaal: 2+8+3+15+3 = 31
        fmt = '<IIHBHBHBHBfffBBBBBBBBBBBBBBBHHB'
        size = struct.calcsize(fmt)
        
        # Parse lap data voor alle auto's
        for i in range(MAX_CARS):
            if offset + size <= len(data):
                unpacked = struct.unpack(fmt, data[offset:offset+size])
                self.lap_data.append(LapData(*unpacked))
                offset += size
        
        # Time trial data (optioneel)
        if offset + 2 <= len(data):
            self.time_trial_pb_car_idx = struct.unpack('<B', data[offset:offset+1])[0]
            offset += 1
            self.time_trial_rival_car_idx = struct.unpack('<B', data[offset:offset+1])[0]
    
    def get_player_lap_data(self) -> LapData:
        """Krijg lap data van speler"""
        return self.lap_data[self.header.player_car_index]
    
    def get_car_lap_data(self, car_index: int) -> LapData:
        """Krijg lap data van specifieke auto"""
        if 0 <= car_index < len(self.lap_data):
            return self.lap_data[car_index]
        raise IndexError(f"Car index {car_index} buiten bereik")
    
    def get_leaderboard(self) -> List[tuple]:
        """
        Krijg leaderboard (gesorteerd op positie)
        
        Returns:
            List van (car_index, LapData) tuples gesorteerd op positie
        """
        leaderboard = []
        for i, lap_data in enumerate(self.lap_data):
            if lap_data.result_status in [ResultStatus.ACTIVE, ResultStatus.FINISHED]:
                leaderboard.append((i, lap_data))
        
        # Sorteer op positie
        leaderboard.sort(key=lambda x: x[1].car_position)
        return leaderboard


class LapPositionsPacket:
    """
    Packet ID: 15 - Lap Positions
    Frequentie: Bij elke ronde
    
    Posities van alle rijders aan start van elke ronde voor chart
    """
    
    def __init__(self, header: PacketHeader, data: bytes):
        self.header = header
        offset = 29
        
        # Aantal rondes in data
        self.num_laps = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        
        # Start lap index
        self.lap_start = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        
        # Position data - max 50 laps x 22 cars
        self.positions = []
        
        for lap in range(50):
            lap_positions = []
            for car in range(MAX_CARS):
                if offset + 1 <= len(data):
                    position = struct.unpack('<B', data[offset:offset+1])[0]
                    lap_positions.append(position)
                    offset += 1
                else:
                    lap_positions.append(0)
            self.positions.append(lap_positions)
    
    def get_position_at_lap_start(self, car_index: int, lap_number: int) -> int:
        """
        Krijg positie van auto aan start van ronde
        
        Args:
            car_index: Index van auto (0-21)
            lap_number: Ronde nummer (1-based)
            
        Returns:
            Positie (1-based), 0 als geen data
        """
        lap_idx = lap_number - 1 - self.lap_start
        if 0 <= lap_idx < len(self.positions) and 0 <= car_index < MAX_CARS:
            return self.positions[lap_idx][car_index]
        return 0
    
    def get_position_history(self, car_index: int) -> List[int]:
        """
        Krijg positie geschiedenis van auto
        
        Args:
            car_index: Index van auto (0-21)
            
        Returns:
            List van posities per ronde (0 = geen data)
        """
        history = []
        for lap in range(self.num_laps):
            if lap < len(self.positions):
                history.append(self.positions[lap][car_index])
        return history
    
    def __str__(self):
        return f"LapPositions(num_laps={self.num_laps}, lap_start={self.lap_start})"