"""
F1 25 Telemetry - Overige Packets
Bevat CarSetups, FinalClassification, SessionHistory, TyreSets en TimeTrial packets
"""

import struct
from dataclasses import dataclass
from typing import List
from packet_header import PacketHeader
from packet_types import MAX_CARS, MAX_TYRE_STINTS, MAX_TYRE_SETS, TyreCompound, ResultStatus

@dataclass
class CarSetupData:
    """
    Setup data voor 1 auto
    """
    front_wing: int
    rear_wing: int
    on_throttle: int  # Differential adjustment on throttle (percentage)
    off_throttle: int  # Differential adjustment off throttle (percentage)
    front_camber: float
    rear_camber: float
    front_toe: float
    rear_toe: float
    front_suspension: int
    rear_suspension: int
    front_anti_roll_bar: int
    rear_anti_roll_bar: int
    front_suspension_height: int
    rear_suspension_height: int
    brake_pressure: int  # percentage
    brake_bias: int  # percentage
    rear_left_tyre_pressure: float
    rear_right_tyre_pressure: float
    front_left_tyre_pressure: float
    front_right_tyre_pressure: float
    ballast: int
    fuel_load: float

class CarSetupsPacket:
    """
    Packet ID: 5 - Car Setups
    Frequentie: 2 per seconde
    
    Car setup details voor alle auto's
    In multiplayer zie je alleen je eigen setup
    """
    
    def __init__(self, header: PacketHeader, data: bytes):
        self.header = header
        self.car_setups: List[CarSetupData] = []
        
        offset = 29
        
        # Format voor CarSetupData
        fmt = '<BBBBffffffffBBBBBBBBffffBf'
        size = struct.calcsize(fmt)
        
        for i in range(MAX_CARS):
            if offset + size <= len(data):
                unpacked = struct.unpack(fmt, data[offset:offset+size])
                self.car_setups.append(CarSetupData(*unpacked))
                offset += size
    
    def get_player_setup(self) -> CarSetupData:
        """Krijg setup van speler"""
        return self.car_setups[self.header.player_car_index]
    
    def get_car_setup(self, car_index: int) -> CarSetupData:
        """Krijg setup van specifieke auto"""
        if 0 <= car_index < len(self.car_setups):
            return self.car_setups[car_index]
        raise IndexError(f"Car index {car_index} buiten bereik")

@dataclass
class FinalClassificationData:
    """
    Finale classificatie data voor 1 rijder
    """
    position: int  # Eindpositie
    num_laps: int  # Aantal voltooide rondes
    grid_position: int  # Startpositie
    points: int  # Aantal punten
    num_pit_stops: int  # Aantal pitstops
    result_status: int  # 0=invalid, 1=inactive, 2=active, 3=finished, 4=DNF, 5=DSQ, 6=not classified, 7=retired
    result_reason: int  # Reden voor result (nieuw in F1 25)
    best_lap_time_ms: int  # Beste rondetijd in milliseconden
    total_race_time: float  # Totale race tijd in seconden (zonder straffen)
    penalties_time: int  # Totale straffen in seconden
    num_penalties: int  # Aantal straffen
    num_tyre_stints: int  # Aantal band stints
    tyre_stints_actual: List[int]  # Echte banden gebruikt (8 stints max)
    tyre_stints_visual: List[int]  # Visuele banden (8 stints max)
    tyre_stints_end_laps: List[int]  # Ronde nummers waar stints eindigen
    
    def get_result_status_name(self) -> str:
        """Krijg result status naam"""
        try:
            return ResultStatus(self.result_status).name
        except ValueError:
            return f"UNKNOWN_{self.result_status}"
    
    def get_best_lap_time_str(self) -> str:
        """Krijg beste rondetijd als string (MM:SS.mmm)"""
        if self.best_lap_time_ms == 0:
            return "--:--.---"
        total_seconds = self.best_lap_time_ms / 1000
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:06.3f}"
    
    def get_total_race_time_str(self) -> str:
        """Krijg totale race tijd als string"""
        if self.total_race_time == 0:
            return "--:--:--.---"
        hours = int(self.total_race_time // 3600)
        minutes = int((self.total_race_time % 3600) // 60)
        seconds = self.total_race_time % 60
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:06.3f}"
        return f"{minutes}:{seconds:06.3f}"

class FinalClassificationPacket:
    """
    Packet ID: 8 - Final Classification
    Frequentie: Einde van race
    
    Finale classificatie bevestiging aan einde van race
    """
    
    def __init__(self, header: PacketHeader, data: bytes):
        self.header = header
        offset = 29
        
        # Aantal auto's in classificatie
        self.num_cars = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        
        self.classification_data: List[FinalClassificationData] = []
        
        for i in range(MAX_CARS):
            if offset + 45 <= len(data):
                # Parse basis data
                position = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                num_laps = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                grid_position = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                points = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                num_pit_stops = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                result_status = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                result_reason = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                best_lap_time_ms = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                total_race_time = struct.unpack('<d', data[offset:offset+8])[0]
                offset += 8
                penalties_time = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                num_penalties = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                num_tyre_stints = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                
                # Tyre stints (3 arrays van 8 bytes)
                tyre_stints_actual = list(struct.unpack('<BBBBBBBB', data[offset:offset+8]))
                offset += 8
                tyre_stints_visual = list(struct.unpack('<BBBBBBBB', data[offset:offset+8]))
                offset += 8
                tyre_stints_end_laps = list(struct.unpack('<BBBBBBBB', data[offset:offset+8]))
                offset += 8
                
                classification = FinalClassificationData(
                    position, num_laps, grid_position, points, num_pit_stops,
                    result_status, result_reason, best_lap_time_ms, total_race_time,
                    penalties_time, num_penalties, num_tyre_stints,
                    tyre_stints_actual, tyre_stints_visual, tyre_stints_end_laps
                )
                self.classification_data.append(classification)
    
    def get_podium(self) -> List[FinalClassificationData]:
        """Krijg top 3 (podium)"""
        podium = []
        for classification in self.classification_data[:self.num_cars]:
            if classification.position <= 3 and classification.result_status == ResultStatus.FINISHED:
                podium.append(classification)
        return sorted(podium, key=lambda x: x.position)
    
    def get_points_scorers(self) -> List[FinalClassificationData]:
        """Krijg alle rijders die punten hebben gescoord"""
        return [c for c in self.classification_data[:self.num_cars] if c.points > 0]

@dataclass
class LapHistoryData:
    """
    Lap geschiedenis data voor 1 ronde
    """
    lap_time_ms: int
    sector1_time_ms_part: int
    sector1_time_minutes_part: int
    sector2_time_ms_part: int
    sector2_time_minutes_part: int
    sector3_time_ms_part: int
    sector3_time_minutes_part: int
    lap_valid_bit_flags: int
    
    def get_lap_time_str(self) -> str:
        """Krijg rondetijd als string"""
        if self.lap_time_ms == 0:
            return "--:--.---"
        total_seconds = self.lap_time_ms / 1000
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:06.3f}"

@dataclass
class TyreStintHistoryData:
    """
    Band stint geschiedenis
    """
    end_lap: int
    tyre_actual_compound: int
    tyre_visual_compound: int
    
    def get_compound_name(self) -> str:
        """Krijg compound naam"""
        try:
            return TyreCompound(self.tyre_actual_compound).name
        except ValueError:
            return f"UNKNOWN_{self.tyre_actual_compound}"

class SessionHistoryPacket:
    """
    Packet ID: 11 - Session History
    Frequentie: Op aanvraag (via MFD panel)
    
    Lap en band data voor sessie
    """
    
    def __init__(self, header: PacketHeader, data: bytes):
        self.header = header
        offset = 29
        
        # Car index voor deze geschiedenis
        self.car_idx = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        
        # Aantal laps
        self.num_laps = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        
        # Aantal tyre stints
        self.num_tyre_stints = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        
        # Best lap time lap num
        self.best_lap_time_lap_num = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        
        # Best sector 1/2/3 lap nums
        self.best_sector1_lap_num = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        self.best_sector2_lap_num = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        self.best_sector3_lap_num = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        
        # Lap history data (max 100 laps)
        self.lap_history_data: List[LapHistoryData] = []
        for i in range(100):
            if offset + 11 <= len(data):
                lap_time_ms = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                s1_ms = struct.unpack('<H', data[offset:offset+2])[0]
                offset += 2
                s1_min = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                s2_ms = struct.unpack('<H', data[offset:offset+2])[0]
                offset += 2
                s2_min = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                s3_ms = struct.unpack('<H', data[offset:offset+2])[0]
                offset += 2
                s3_min = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                lap_valid = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                
                self.lap_history_data.append(LapHistoryData(
                    lap_time_ms, s1_ms, s1_min, s2_ms, s2_min, s3_ms, s3_min, lap_valid
                ))
        
        # Tyre stint history (max 8 stints)
        self.tyre_stints_history_data: List[TyreStintHistoryData] = []
        for i in range(8):
            if offset + 3 <= len(data):
                end_lap = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                actual = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                visual = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                
                self.tyre_stints_history_data.append(TyreStintHistoryData(
                    end_lap, actual, visual
                ))
    
    def get_valid_laps(self) -> List[LapHistoryData]:
        """Krijg alleen geldige rondes"""
        return [lap for lap in self.lap_history_data[:self.num_laps] if lap.lap_valid_bit_flags & 0x01]

@dataclass
class TyreSetData:
    """
    Data voor 1 set banden
    """
    actual_tyre_compound: int
    visual_tyre_compound: int
    wear: int  # percentage
    available: int  # 0 = niet beschikbaar, 1 = beschikbaar
    recommended_session: int
    life_span: int  # laps
    usable_life: int  # laps
    lap_delta_time: int  # milliseconds
    fitted: int  # 0 = niet gemonteerd, 1 = gemonteerd
    
    def get_compound_name(self) -> str:
        """Krijg compound naam"""
        try:
            return TyreCompound(self.actual_tyre_compound).name
        except ValueError:
            return f"UNKNOWN_{self.actual_tyre_compound}"
    
    def is_fitted(self) -> bool:
        """Check of deze set gemonteerd is"""
        return self.fitted == 1
    
    def is_available(self) -> bool:
        """Check of deze set beschikbaar is"""
        return self.available == 1

class TyreSetsPacket:
    """
    Packet ID: 12 - Tyre Sets
    Frequentie: Op aanvraag
    
    Extended tyre set data
    """
    
    def __init__(self, header: PacketHeader, data: bytes):
        self.header = header
        offset = 29
        
        # Car index
        self.car_idx = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        
        # Tyre sets (20 sets max: 13 dry + 7 wet)
        self.tyre_set_data: List[TyreSetData] = []
        
        fmt = '<BBBBBHHHB'
        size = struct.calcsize(fmt)
        
        for i in range(MAX_TYRE_SETS):
            if offset + size <= len(data):
                unpacked = struct.unpack(fmt, data[offset:offset+size])
                self.tyre_set_data.append(TyreSetData(*unpacked))
                offset += size
        
        # Fitted index
        if offset + 1 <= len(data):
            self.fitted_idx = struct.unpack('<B', data[offset:offset+1])[0]
    
    def get_fitted_tyres(self) -> TyreSetData:
        """Krijg huidige gemonteerde banden"""
        if 0 <= self.fitted_idx < len(self.tyre_set_data):
            return self.tyre_set_data[self.fitted_idx]
        return None
    
    def get_available_sets(self) -> List[TyreSetData]:
        """Krijg alle beschikbare band sets"""
        return [tyre_set for tyre_set in self.tyre_set_data if tyre_set.is_available()]

class TimeTrialPacket:
    """
    Packet ID: 14 - Time Trial
    Frequentie: Rate as specified in menus
    
    Time trial specifieke data
    """
    
    def __init__(self, header: PacketHeader, data: bytes):
        self.header = header
        offset = 29
        
        # Personal best data
        self.personal_best_lap_time_ms = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        self.personal_best_sector1_ms = struct.unpack('<H', data[offset:offset+2])[0]
        offset += 2
        self.personal_best_sector2_ms = struct.unpack('<H', data[offset:offset+2])[0]
        offset += 2
        self.personal_best_sector3_ms = struct.unpack('<H', data[offset:offset+2])[0]
        offset += 2
        
        # Rival data
        self.rival_lap_time_ms = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        self.rival_sector1_ms = struct.unpack('<H', data[offset:offset+2])[0]
        offset += 2
        self.rival_sector2_ms = struct.unpack('<H', data[offset:offset+2])[0]
        offset += 2
        self.rival_sector3_ms = struct.unpack('<H', data[offset:offset+2])[0]
        offset += 2
    
    def get_pb_time_str(self) -> str:
        """Krijg personal best tijd als string"""
        if self.personal_best_lap_time_ms == 0:
            return "--:--.---"
        total_seconds = self.personal_best_lap_time_ms / 1000
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:06.3f}"
    
    def get_rival_time_str(self) -> str:
        """Krijg rival tijd als string"""
        if self.rival_lap_time_ms == 0:
            return "--:--.---"
        total_seconds = self.rival_lap_time_ms / 1000
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:06.3f}"
    
    def get_delta_to_rival_ms(self) -> int:
        """Krijg delta t.o.v. rival in milliseconden (negatief = sneller)"""
        if self.personal_best_lap_time_ms == 0 or self.rival_lap_time_ms == 0:
            return 0
        return self.personal_best_lap_time_ms - self.rival_lap_time_ms