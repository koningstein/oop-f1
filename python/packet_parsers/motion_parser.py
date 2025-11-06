"""
F1 25 Telemetry - Motion Parser
Parse Motion packets (ID 0) en Motion Ex packets (ID 13)
"""

from dataclasses import dataclass
from typing import Optional, List
from .base_parser import BaseParser
from .packet_header import PacketHeader

@dataclass
class CarMotionData:
    """Motion data voor één auto"""
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

@dataclass
class MotionPacket:
    """Complete motion packet"""
    header: PacketHeader
    car_motion_data: List[CarMotionData]

@dataclass
class MotionExData:
    """Extended motion data voor speler auto"""
    suspension_position: List[float]  # [RL, RR, FL, FR]
    suspension_velocity: List[float]  # [RL, RR, FL, FR]
    suspension_acceleration: List[float]  # [RL, RR, FL, FR]
    wheel_speed: List[float]  # [RL, RR, FL, FR]
    wheel_slip_ratio: List[float]  # [RL, RR, FL, FR]
    wheel_slip_angle: List[float]  # [RL, RR, FL, FR]
    wheel_lat_force: List[float]  # [RL, RR, FL, FR]
    wheel_long_force: List[float]  # [RL, RR, FL, FR]
    height_of_cog_above_ground: float
    local_velocity_x: float
    local_velocity_y: float
    local_velocity_z: float
    angular_velocity_x: float
    angular_velocity_y: float
    angular_velocity_z: float
    angular_acceleration_x: float
    angular_acceleration_y: float
    angular_acceleration_z: float
    front_wheels_angle: float
    vertical_force: List[float]  # [RL, RR, FL, FR]
    front_aero_height: float
    rear_aero_height: float
    front_roll_angle: float
    rear_roll_angle: float
    chassis_yaw: float
    chassis_pitch: float
    wheel_camber: List[float]  # [RL, RR, FL, FR]
    wheel_camber_gain: List[float]  # [RL, RR, FL, FR]

@dataclass
class MotionExPacket:
    """Complete motion ex packet"""
    header: PacketHeader
    motion_ex_data: MotionExData

class MotionParser(BaseParser):
    """Parser voor Motion packets (ID 0)"""
    
    # Format voor één CarMotionData (60 bytes)
    # worldPosition[3](12) + worldVelocity[3](12) + worldForwardDir[3](6) +
    # worldRightDir[3](6) + gForce[3](12) + yaw(4) + pitch(4) + roll(4) = 60
    MOTION_FORMAT = "<ffffffhhhhhh fff fff"
    
    def parse(self, header: PacketHeader, payload: bytes) -> Optional[MotionPacket]:
        """
        Parse motion packet
        
        Args:
            header: Packet header
            payload: Packet payload
            
        Returns:
            MotionPacket object of None
        """
        expected_size = 60 * 22  # 22 cars
        if not self.validate_payload_size(payload, expected_size):
            return None
        
        try:
            motion_data = []
            offset = 0
            
            # Parse motion data voor alle 22 auto's
            for car_idx in range(22):
                unpacked = self.unpack_safely(self.MOTION_FORMAT, payload, offset)
                if not unpacked:
                    self.logger.warning(f"Fout bij parsen motion data auto {car_idx}")
                    break
                
                motion = CarMotionData(
                    world_position_x=unpacked[0],
                    world_position_y=unpacked[1],
                    world_position_z=unpacked[2],
                    world_velocity_x=unpacked[3],
                    world_velocity_y=unpacked[4],
                    world_velocity_z=unpacked[5],
                    world_forward_dir_x=unpacked[6],
                    world_forward_dir_y=unpacked[7],
                    world_forward_dir_z=unpacked[8],
                    world_right_dir_x=unpacked[9],
                    world_right_dir_y=unpacked[10],
                    world_right_dir_z=unpacked[11],
                    g_force_lateral=unpacked[12],
                    g_force_longitudinal=unpacked[13],
                    g_force_vertical=unpacked[14],
                    yaw=unpacked[15],
                    pitch=unpacked[16],
                    roll=unpacked[17]
                )
                
                motion_data.append(motion)
                offset += 60
            
            return MotionPacket(
                header=header,
                car_motion_data=motion_data
            )
            
        except Exception as e:
            self.logger.error(f"Motion parse fout: {e}")
            return None

class MotionExParser(BaseParser):
    """Parser voor Motion Ex packets (ID 13)"""
    
    def parse(self, header: PacketHeader, payload: bytes) -> Optional[MotionExPacket]:
        """
        Parse motion ex packet (extended motion data voor speler auto)
        
        Args:
            header: Packet header
            payload: Packet payload
            
        Returns:
            MotionExPacket object of None
        """
        if not self.validate_payload_size(payload, 217):
            return None
        
        try:
            offset = 0
            
            # Parse suspension position (4 floats)
            suspension_position = []
            for _ in range(4):
                val = self.unpack_safely("<f", payload, offset)
                suspension_position.append(val[0] if val else 0.0)
                offset += 4
            
            # Parse suspension velocity (4 floats)
            suspension_velocity = []
            for _ in range(4):
                val = self.unpack_safely("<f", payload, offset)
                suspension_velocity.append(val[0] if val else 0.0)
                offset += 4
            
            # Parse suspension acceleration (4 floats)
            suspension_acceleration = []
            for _ in range(4):
                val = self.unpack_safely("<f", payload, offset)
                suspension_acceleration.append(val[0] if val else 0.0)
                offset += 4
            
            # Parse wheel speed (4 floats)
            wheel_speed = []
            for _ in range(4):
                val = self.unpack_safely("<f", payload, offset)
                wheel_speed.append(val[0] if val else 0.0)
                offset += 4
            
            # Parse wheel slip ratio (4 floats)
            wheel_slip_ratio = []
            for _ in range(4):
                val = self.unpack_safely("<f", payload, offset)
                wheel_slip_ratio.append(val[0] if val else 0.0)
                offset += 4
            
            # Parse wheel slip angle (4 floats)
            wheel_slip_angle = []
            for _ in range(4):
                val = self.unpack_safely("<f", payload, offset)
                wheel_slip_angle.append(val[0] if val else 0.0)
                offset += 4
            
            # Parse wheel lat force (4 floats)
            wheel_lat_force = []
            for _ in range(4):
                val = self.unpack_safely("<f", payload, offset)
                wheel_lat_force.append(val[0] if val else 0.0)
                offset += 4
            
            # Parse wheel long force (4 floats)
            wheel_long_force = []
            for _ in range(4):
                val = self.unpack_safely("<f", payload, offset)
                wheel_long_force.append(val[0] if val else 0.0)
                offset += 4
            
            # Parse rest van data
            rest_data = self.unpack_safely("<fffffffffffffffff", payload, offset)
            if not rest_data:
                return None
            
            # Parse vertical force (4 floats) - offset 144
            vertical_force = []
            offset = 144
            for _ in range(4):
                val = self.unpack_safely("<f", payload, offset)
                vertical_force.append(val[0] if val else 0.0)
                offset += 4
            
            # Parse aero heights en roll angles
            aero_data = self.unpack_safely("<ffffff", payload, offset)
            offset += 24
            
            # Parse wheel camber (4 floats)
            wheel_camber = []
            for _ in range(4):
                val = self.unpack_safely("<f", payload, offset)
                wheel_camber.append(val[0] if val else 0.0)
                offset += 4
            
            # Parse wheel camber gain (4 floats)
            wheel_camber_gain = []
            for _ in range(4):
                val = self.unpack_safely("<f", payload, offset)
                wheel_camber_gain.append(val[0] if val else 0.0)
                offset += 4
            
            motion_ex = MotionExData(
                suspension_position=suspension_position,
                suspension_velocity=suspension_velocity,
                suspension_acceleration=suspension_acceleration,
                wheel_speed=wheel_speed,
                wheel_slip_ratio=wheel_slip_ratio,
                wheel_slip_angle=wheel_slip_angle,
                wheel_lat_force=wheel_lat_force,
                wheel_long_force=wheel_long_force,
                height_of_cog_above_ground=rest_data[0],
                local_velocity_x=rest_data[1],
                local_velocity_y=rest_data[2],
                local_velocity_z=rest_data[3],
                angular_velocity_x=rest_data[4],
                angular_velocity_y=rest_data[5],
                angular_velocity_z=rest_data[6],
                angular_acceleration_x=rest_data[7],
                angular_acceleration_y=rest_data[8],
                angular_acceleration_z=rest_data[9],
                front_wheels_angle=rest_data[10],
                vertical_force=vertical_force,
                front_aero_height=aero_data[0] if aero_data else 0.0,
                rear_aero_height=aero_data[1] if aero_data else 0.0,
                front_roll_angle=aero_data[2] if aero_data else 0.0,
                rear_roll_angle=aero_data[3] if aero_data else 0.0,
                chassis_yaw=aero_data[4] if aero_data else 0.0,
                chassis_pitch=aero_data[5] if aero_data else 0.0,
                wheel_camber=wheel_camber,
                wheel_camber_gain=wheel_camber_gain
            )
            
            return MotionExPacket(
                header=header,
                motion_ex_data=motion_ex
            )
            
        except Exception as e:
            self.logger.error(f"Motion Ex parse fout: {e}")
            return None