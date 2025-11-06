"""
F1 25 Telemetry - Session History Parser
Parse Session History packet (ID 11) met lap en sector validatie
"""

from dataclasses import dataclass
from typing import Optional, List
from .base_parser import BaseParser
from .packet_header import PacketHeader

@dataclass
class LapHistoryData:
    """Historische lap data met sector validatie"""
    lap_time_ms: int
    sector1_time_ms: int
    sector1_time_minutes: int
    sector2_time_ms: int
    sector2_time_minutes: int
    sector3_time_ms: int
    sector3_time_minutes: int
    lap_valid_bit_flags: int
    
    def is_sector1_valid(self) -> bool:
        """Check of sector 1 valide is via bit flag"""
        return bool(self.lap_valid_bit_flags & 0x01)
    
    def is_sector2_valid(self) -> bool:
        """Check of sector 2 valide is via bit flag"""
        return bool(self.lap_valid_bit_flags & 0x02)
    
    def is_sector3_valid(self) -> bool:
        """Check of sector 3 valide is via bit flag"""
        return bool(self.lap_valid_bit_flags & 0x04)
    
    def is_lap_valid(self) -> bool:
        """Check of volledige lap valide is"""
        return self.lap_valid_bit_flags == 0x07  # Alle 3 bits aan
    
    def get_sector1_total_ms(self) -> int:
        """Totale sector 1 tijd in ms"""
        return (self.sector1_time_minutes * 60000) + self.sector1_time_ms
    
    def get_sector2_total_ms(self) -> int:
        """Totale sector 2 tijd in ms"""
        return (self.sector2_time_minutes * 60000) + self.sector2_time_ms
    
    def get_sector3_total_ms(self) -> int:
        """Totale sector 3 tijd in ms"""
        return (self.sector3_time_minutes * 60000) + self.sector3_time_ms

@dataclass
class TyreStintHistoryData:
    """Tyre stint history"""
    end_lap: int
    tyre_actual_compound: int
    tyre_visual_compound: int

@dataclass
class SessionHistoryData:
    """Complete session history voor één auto"""
    header: PacketHeader
    car_idx: int
    num_laps: int
    num_tyre_stints: int
    best_lap_time_lap_num: int
    best_sector1_lap_num: int
    best_sector2_lap_num: int
    best_sector3_lap_num: int
    lap_history_data: List[LapHistoryData]
    tyre_stints_history_data: List[TyreStintHistoryData]

class SessionHistoryParser(BaseParser):
    """Parser voor Session History packets (ID 11)"""
    
    # Format voor één LapHistoryData (14 bytes)
    LAP_HISTORY_FORMAT = "<IHBHBHBB"
    
    # Format voor één TyreStintHistoryData (3 bytes)
    TYRE_STINT_FORMAT = "<BBB"
    
    def parse(self, header: PacketHeader, payload: bytes) -> Optional[SessionHistoryData]:
        """
        Parse session history packet
        
        Args:
            header: Packet header
            payload: Packet payload
            
        Returns:
            SessionHistoryData object of None
        """
        if not self.validate_payload_size(payload, 1431):
            return None
        
        try:
            # Parse header info (7 bytes)
            header_data = self.unpack_safely("<BBBBBBB", payload, 0)
            if not header_data:
                return None
            
            car_idx = header_data[0]
            num_laps = header_data[1]
            num_tyre_stints = header_data[2]
            best_lap_time_lap_num = header_data[3]
            best_sector1_lap_num = header_data[4]
            best_sector2_lap_num = header_data[5]
            best_sector3_lap_num = header_data[6]
            
            # Valideer car index
            if not self.validate_car_index(car_idx):
                self.logger.warning(f"Ongeldige car_idx: {car_idx}")
                return None
            
            # Parse lap history (max 100 laps)
            lap_history = []
            offset = 7
            
            for lap_num in range(100):
                lap_data = self.unpack_safely(self.LAP_HISTORY_FORMAT, payload, offset)
                if lap_data and lap_num < num_laps:
                    lap_history.append(LapHistoryData(
                        lap_time_ms=lap_data[0],
                        sector1_time_ms=lap_data[1],
                        sector1_time_minutes=lap_data[2],
                        sector2_time_ms=lap_data[3],
                        sector2_time_minutes=lap_data[4],
                        sector3_time_ms=lap_data[5],
                        sector3_time_minutes=lap_data[6],
                        lap_valid_bit_flags=lap_data[7]
                    ))
                offset += 14
            
            # Parse tyre stints (max 8 stints)
            tyre_stints = []
            
            for stint_num in range(8):
                stint_data = self.unpack_safely(self.TYRE_STINT_FORMAT, payload, offset)
                if stint_data and stint_num < num_tyre_stints:
                    tyre_stints.append(TyreStintHistoryData(
                        end_lap=stint_data[0],
                        tyre_actual_compound=stint_data[1],
                        tyre_visual_compound=stint_data[2]
                    ))
                offset += 3
            
            return SessionHistoryData(
                header=header,
                car_idx=car_idx,
                num_laps=num_laps,
                num_tyre_stints=num_tyre_stints,
                best_lap_time_lap_num=best_lap_time_lap_num,
                best_sector1_lap_num=best_sector1_lap_num,
                best_sector2_lap_num=best_sector2_lap_num,
                best_sector3_lap_num=best_sector3_lap_num,
                lap_history_data=lap_history,
                tyre_stints_history_data=tyre_stints
            )
            
        except Exception as e:
            self.logger.error(f"Session history parse fout: {e}")
            return None