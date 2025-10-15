"""
F1 25 Telemetry - Motion Packets
Bevat Motion en MotionEx packet parsers (realtime motion data)
"""

import struct
from dataclasses import dataclass
from typing import List, Tuple
from packet_header import PacketHeader
from packet_types import MAX_CARS

@dataclass
class CarMotionData:
    """
    Motion data voor 1 auto
    
    Attributes:
        world_position_*: Wereld positie X/Y/Z
        world_velocity_*: Wereld snelheid X/Y/Z
        world_forward_dir_*: Voorwaartse richting (normalized)
        world_right_dir_*: Rechter richting (normalized)
        g_force_*: G-krachten lateral/longitudinal/vertical
        yaw: Yaw hoek
        pitch: Pitch hoek
        roll: Roll hoek
    """
    world_position_x: float
    world_position_y: float
    world_position_z: float
    world_velocity_x: float
    world_velocity_y: float
    world_velocity_z: float
    world_forward_dir_x: int
    world_forward_dir_y: int
    world_forward_dir_z: int
    world_right_dir_x: int
    world_right_dir_y: int
    world_right_dir_z: int
    g_force_lateral: float
    g_force_longitudinal: float
    g_force_vertical: float
    yaw: float
    pitch: float
    roll: float
    
    @classmethod
    def from_bytes(cls, data: bytes, offset: int) -> Tuple['CarMotionData', int]:
        """Parse CarMotionData uit bytes"""
        fmt = '<ffffffhhhhhhffffff'
        size = struct.calcsize(fmt)
        unpacked = struct.unpack(fmt, data[offset:offset+size])
        return cls(*unpacked), size

class MotionPacket:
    """
    Packet ID: 0 - Motion Data
    Frequentie: Elke frame (alleen tijdens speler control)
    
    Bevat alle motion data voor speler's auto
    """
    
    def __init__(self, header: PacketHeader, data: bytes):
        self.header = header
        self.car_motion_data: List[CarMotionData] = []
        
        offset = 29  # Na header
        
        # Parse motion data voor alle auto's
        for i in range(MAX_CARS):
            car_data, size = CarMotionData.from_bytes(data, offset)
            self.car_motion_data.append(car_data)
            offset += size
    
    def get_player_data(self) -> CarMotionData:
        """Krijg motion data van speler"""
        return self.car_motion_data[self.header.player_car_index]
    
    def get_car_data(self, car_index: int) -> CarMotionData:
        """Krijg motion data van specifieke auto"""
        if 0 <= car_index < MAX_CARS:
            return self.car_motion_data[car_index]
        raise IndexError(f"Car index {car_index} buiten bereik (0-{MAX_CARS-1})")

class MotionExPacket:
    """
    Packet ID: 13 - Extended Motion Data (alleen speler auto)
    Frequentie: Elke frame
    
    Extra motion data zoals wielsnelheden, slip ratios, veren, etc.
    """
    
    def __init__(self, header: PacketHeader, data: bytes):
        self.header = header
        offset = 29
        
        # Alle arrays zijn in volgorde: RL, RR, FL, FR
        
        # Suspension (4x3 floats = 12 floats)
        self.suspension_position = struct.unpack('<ffff', data[offset:offset+16])
        offset += 16
        self.suspension_velocity = struct.unpack('<ffff', data[offset:offset+16])
        offset += 16
        self.suspension_acceleration = struct.unpack('<ffff', data[offset:offset+16])
        offset += 16
        
        # Wheel data (4x floats per type)
        self.wheel_speed = struct.unpack('<ffff', data[offset:offset+16])
        offset += 16
        self.wheel_slip_ratio = struct.unpack('<ffff', data[offset:offset+16])
        offset += 16
        self.wheel_slip_angle = struct.unpack('<ffff', data[offset:offset+16])
        offset += 16
        self.wheel_lat_force = struct.unpack('<ffff', data[offset:offset+16])
        offset += 16
        self.wheel_long_force = struct.unpack('<ffff', data[offset:offset+16])
        offset += 16
        
        # Single values
        self.height_of_cog_above_ground = struct.unpack('<f', data[offset:offset+4])[0]
        offset += 4
        
        # Local velocity
        self.local_velocity_x = struct.unpack('<f', data[offset:offset+4])[0]
        offset += 4
        self.local_velocity_y = struct.unpack('<f', data[offset:offset+4])[0]
        offset += 4
        self.local_velocity_z = struct.unpack('<f', data[offset:offset+4])[0]
        offset += 4
        
        # Angular velocity
        self.angular_velocity_x = struct.unpack('<f', data[offset:offset+4])[0]
        offset += 4
        self.angular_velocity_y = struct.unpack('<f', data[offset:offset+4])[0]
        offset += 4
        self.angular_velocity_z = struct.unpack('<f', data[offset:offset+4])[0]
        offset += 4
        
        # Angular acceleration
        self.angular_acceleration_x = struct.unpack('<f', data[offset:offset+4])[0]
        offset += 4
        self.angular_acceleration_y = struct.unpack('<f', data[offset:offset+4])[0]
        offset += 4
        self.angular_acceleration_z = struct.unpack('<f', data[offset:offset+4])[0]
        offset += 4
        
        # Front wheels angle
        self.front_wheels_angle = struct.unpack('<f', data[offset:offset+4])[0]
        offset += 4
        
        # Wheel vertical forces
        self.wheel_vert_force = struct.unpack('<ffff', data[offset:offset+16])
        offset += 16
        
        # Front camber (nieuw in F1 25)
        self.front_left_camber = struct.unpack('<f', data[offset:offset+4])[0]
        offset += 4
        self.front_right_camber = struct.unpack('<f', data[offset:offset+4])[0]
        offset += 4
        
        # Chassis pitch (nieuw in F1 25)
        self.chassis_pitch = struct.unpack('<f', data[offset:offset+4])[0]
    
    def get_wheel_data_str(self, wheel_idx: int) -> str:
        """
        Krijg alle wheel data voor een wiel als string
        
        Args:
            wheel_idx: 0=RL, 1=RR, 2=FL, 3=FR
        """
        wheel_names = ["RL", "RR", "FL", "FR"]
        return (f"{wheel_names[wheel_idx]}: "
                f"Speed={self.wheel_speed[wheel_idx]:.1f}, "
                f"Slip={self.wheel_slip_ratio[wheel_idx]:.3f}, "
                f"Force={self.wheel_vert_force[wheel_idx]:.0f}N")