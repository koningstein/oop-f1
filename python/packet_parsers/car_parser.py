"""
F1 25 Telemetry - Car Telemetry Parser
Parse Car Telemetry packet (ID 6) met live telemetrie data
"""

from dataclasses import dataclass
from typing import Optional, List
from .base_parser import BaseParser
from .packet_header import PacketHeader

@dataclass
class CarTelemetryData:
    """Live telemetrie data voor één auto"""
    speed: int
    throttle: float
    steer: float
    brake: float
    clutch: int
    gear: int
    engine_rpm: int
    drs: bool
    rev_lights_percent: int
    rev_lights_bit_value: int
    brakes_temperature: List[int]  # [RL, RR, FL, FR]
    tyres_surface_temperature: List[int]  # [RL, RR, FL, FR]
    tyres_inner_temperature: List[int]  # [RL, RR, FL, FR]
    engine_temperature: int
    tyres_pressure: List[float]  # [RL, RR, FL, FR]
    surface_type: List[int]  # [RL, RR, FL, FR]

@dataclass
class CarTelemetryPacket:
    """Complete car telemetry packet"""
    header: PacketHeader
    car_telemetry_data: List[CarTelemetryData]
    mfd_panel_index: int
    mfd_panel_index_secondary_player: int
    suggested_gear: int

class CarTelemetryParser(BaseParser):
    """Parser voor Car Telemetry packets (ID 6)"""
    
    # Format voor één CarTelemetryData (60 bytes)
    # speed(2) + throttle(4) + steer(4) + brake(4) + clutch(1) + gear(1) + 
    # engineRPM(2) + drs(1) + revLightsPercent(1) + revLightsBitValue(2) +
    # brakes[4](8) + tyresSurface[4](8) + tyresInner[4](8) + engineTemp(2) +
    # tyresPressure[4](16) + surfaceType[4](4) = 60 bytes
    TELEMETRY_FORMAT = "<HfffBbHBBHHHHHHHHHHHHffffBBBB"
    
    def parse(self, header: PacketHeader, payload: bytes) -> Optional[CarTelemetryPacket]:
        """
        Parse car telemetry packet
        
        Args:
            header: Packet header
            payload: Packet payload
            
        Returns:
            CarTelemetryPacket object of None
        """
        expected_size = (60 * 22) + 3  # 22 cars + 3 bytes voor MFD panel data
        if not self.validate_payload_size(payload, expected_size):
            return None
        
        try:
            telemetry_data = []
            offset = 0
            
            # Parse telemetrie voor alle 22 auto's
            for car_idx in range(22):
                unpacked = self.unpack_safely(self.TELEMETRY_FORMAT, payload, offset)
                if not unpacked:
                    self.logger.warning(f"Fout bij parsen telemetrie auto {car_idx}")
                    break
                
                telemetry = CarTelemetryData(
                    speed=unpacked[0],
                    throttle=unpacked[1],
                    steer=unpacked[2],
                    brake=unpacked[3],
                    clutch=unpacked[4],
                    gear=unpacked[5],
                    engine_rpm=unpacked[6],
                    drs=bool(unpacked[7]),
                    rev_lights_percent=unpacked[8],
                    rev_lights_bit_value=unpacked[9],
                    brakes_temperature=[unpacked[10], unpacked[11], unpacked[12], unpacked[13]],
                    tyres_surface_temperature=[unpacked[14], unpacked[15], unpacked[16], unpacked[17]],
                    tyres_inner_temperature=[unpacked[18], unpacked[19], unpacked[20], unpacked[21]],
                    engine_temperature=unpacked[22],
                    tyres_pressure=[unpacked[23], unpacked[24], unpacked[25], unpacked[26]],
                    surface_type=[unpacked[27], unpacked[28], unpacked[29], unpacked[30]]
                )
                
                telemetry_data.append(telemetry)
                offset += 60
            
            # Parse MFD panel data
            mfd_data = self.unpack_safely("<BBb", payload, offset)
            if not mfd_data:
                mfd_data = (0, 0, 0)
            
            return CarTelemetryPacket(
                header=header,
                car_telemetry_data=telemetry_data,
                mfd_panel_index=mfd_data[0],
                mfd_panel_index_secondary_player=mfd_data[1],
                suggested_gear=mfd_data[2]
            )
            
        except Exception as e:
            self.logger.error(f"Car telemetry parse fout: {e}")
            return None