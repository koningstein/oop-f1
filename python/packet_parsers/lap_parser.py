"""
F1 25 Telemetry - Lap Data Parser
Parse Lap Data packet (ID 2) met rondetijden en sector informatie
"""

from dataclasses import dataclass
from typing import Optional, List
from .base_parser import BaseParser
from .packet_header import PacketHeader

@dataclass
class LapData:
    """
    Dataclass for the lap data of one car.
    (Versie 2: Met default waarden om leeg te initialiseren)
    """
    last_lap_time_ms: int = 0
    current_lap_time_ms: int = 0
    sector1_time_ms: int = 0
    sector1_time_minutes: int = 0
    sector2_time_ms: int = 0
    sector2_time_minutes: int = 0
    delta_to_car_in_front_ms: int = 0
    delta_to_race_leader_ms: int = 0
    lap_distance: float = 0.0
    total_distance: float = 0.0
    safety_car_delta: float = 0.0
    car_position: int = 0
    current_lap_num: int = 0
    pit_status: int = 0
    num_pit_stops: int = 0
    sector: int = 0
    current_lap_invalid: int = 0
    penalties: int = 0
    total_warnings: int = 0
    corner_cutting_warnings: int = 0
    num_unserved_drive_through_pens: int = 0
    num_unserved_stop_go_pens: int = 0
    grid_position: int = 0
    driver_status: int = 0
    result_status: int = 0
    pit_lane_timer_active: int = 0
    pit_lane_time_in_lane_ms: int = 0
    pit_stop_timer_ms: int = 0
    pit_stop_should_serve_pen: int = 0
    speed_trap_fastest_speed: float = 0.0 # Nieuw in F1 25
    speed_trap_fastest_lap: int = 0       # Nieuw in F1 25

    PACKET_FORMAT = "<IIHHIHIIffBBBBBBBBBBBBBBBBBBffB"
    PACKET_LEN = 88 # 88 bytes
    
    def get_sector1_time_ms(self) -> int:
        """Bereken totale sector 1 tijd in milliseconden"""
        return (self.sector1_time_minutes * 60000) + self.sector1_time_ms
    
    def get_sector2_time_ms(self) -> int:
        """Bereken totale sector 2 tijd in milliseconden"""
        return (self.sector2_time_minutes * 60000) + self.sector2_time_ms
    
    def get_sector3_time_ms(self) -> int:
        """
        Bereken sector 3 tijd (rondetijd - sector1 - sector2)
        Returns 0 als niet berekend kan worden
        """
        if self.last_lap_time_ms == 0:
            return 0
        s1 = self.get_sector1_time_ms()
        s2 = self.get_sector2_time_ms()
        s3 = self.last_lap_time_ms - s1 - s2
        return max(0, s3)  # Voorkom negatieve waarden

@dataclass
class LapDataPacket:
    """Complete lap data packet"""
    header: PacketHeader
    lap_data: List[LapData]
    time_trial_pb_car_idx: int
    time_trial_rival_car_idx: int

class LapDataParser(BaseParser):
    """Parser voor Lap Data packets (ID 2)"""
    
    # Format voor één LapData (50 bytes)
    LAP_DATA_FORMAT = "<IIHBHBhHfffBBBBBBBBBBBBBBBBHHBfB"
    
    def parse(self, header: PacketHeader, payload: bytes) -> Optional[LapDataPacket]:
        """
        Parse lap data packet
        
        Args:
            header: Packet header
            payload: Packet payload
            
        Returns:
            LapDataPacket object of None
        """
        expected_size = 50 * 22 + 2  # 22 cars + 2 bytes voor time trial
        if not self.validate_payload_size(payload, expected_size):
            return None
        
        try:
            lap_data_list = []
            offset = 0
            
            # Parse data voor alle 22 auto's
            for car_idx in range(22):
                unpacked = self.unpack_safely(self.LAP_DATA_FORMAT, payload, offset)
                if not unpacked:
                    self.logger.warning(f"Fout bij parsen lap data voor auto {car_idx}")
                    break
                
                lap_data = LapData(
                    last_lap_time_ms=unpacked[0],
                    current_lap_time_ms=unpacked[1],
                    sector1_time_ms=unpacked[2],
                    sector1_time_minutes=unpacked[3],
                    sector2_time_ms=unpacked[4],
                    sector2_time_minutes=unpacked[5],
                    delta_to_car_in_front_ms=unpacked[6],
                    delta_to_race_leader_ms=unpacked[7],
                    lap_distance=unpacked[8],
                    total_distance=unpacked[9],
                    safety_car_delta=unpacked[10],
                    car_position=unpacked[11],
                    current_lap_num=unpacked[12],
                    pit_status=unpacked[13],
                    num_pit_stops=unpacked[14],
                    sector=unpacked[15],
                    current_lap_invalid=bool(unpacked[16]),
                    penalties=unpacked[17],
                    total_warnings=unpacked[18],
                    corner_cutting_warnings=unpacked[19],
                    num_unserved_drive_through_pens=unpacked[20],
                    num_unserved_stop_go_pens=unpacked[21],
                    grid_position=unpacked[22],
                    driver_status=unpacked[23],
                    result_status=unpacked[24],
                    pit_lane_timer_active=bool(unpacked[25]),
                    pit_lane_time_in_lane_ms=unpacked[26],
                    pit_stop_timer_ms=unpacked[27],
                    pit_stop_should_serve_pen=bool(unpacked[28]),
                    speed_trap_fastest_speed=unpacked[29],
                    speed_trap_fastest_lap=unpacked[30]
                )
                
                lap_data_list.append(lap_data)
                offset += 50
            
            # Parse time trial indices
            time_trial_data = self.unpack_safely("<BB", payload, offset)
            time_trial_pb_car_idx = time_trial_data[0] if time_trial_data else 255
            time_trial_rival_car_idx = time_trial_data[1] if time_trial_data else 255
            
            return LapDataPacket(
                header=header,
                lap_data=lap_data_list,
                time_trial_pb_car_idx=time_trial_pb_car_idx,
                time_trial_rival_car_idx=time_trial_rival_car_idx
            )
            
        except Exception as e:
            self.logger.error(f"Lap data parse fout: {e}")
            return None