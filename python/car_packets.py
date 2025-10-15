"""
F1 25 Telemetry - Car Packets
Bevat CarTelemetry, CarStatus en CarDamage packet parsers
"""

import struct
from dataclasses import dataclass
from typing import List, Tuple
from packet_header import PacketHeader
from packet_types import MAX_CARS, TyreCompound, SurfaceType

@dataclass
class CarTelemetryData:
    """
    Telemetrie data voor 1 auto
    
    Realtime data zoals snelheid, RPM, temperaturen, etc.
    """
    speed: int
    throttle: float
    steer: float
    brake: float
    clutch: int
    gear: int
    engine_rpm: int
    drs: int
    rev_lights_percent: int
    rev_lights_bit_value: int
    brakes_temperature: Tuple[int, int, int, int]  # RL, RR, FL, FR
    tyres_surface_temperature: Tuple[int, int, int, int]
    tyres_inner_temperature: Tuple[int, int, int, int]
    engine_temperature: int
    tyres_pressure: Tuple[float, float, float, float]
    surface_type: Tuple[int, int, int, int]
    
    def get_surface_type_names(self) -> List[str]:
        """Krijg oppervlakte type namen voor alle wielen"""
        names = []
        for surface in self.surface_type:
            try:
                names.append(SurfaceType(surface).name)
            except ValueError:
                names.append(f"UNKNOWN_{surface}")
        return names

class CarTelemetryPacket:
    """
    Packet ID: 6 - Car Telemetry
    Frequentie: Rate as specified in menus
    
    Telemetrie data voor alle auto's
    """
    
    def __init__(self, header: PacketHeader, data: bytes):
        self.header = header
        self.car_telemetry_data: List[CarTelemetryData] = []
        
        offset = 29
        
        for i in range(MAX_CARS):
            # Parse basis telemetrie data
            fmt = '<HfffbBHBBH'
            base_size = struct.calcsize(fmt)
            base_data = struct.unpack(fmt, data[offset:offset+base_size])
            offset += base_size
            
            # Rem temperaturen (4x uint16)
            brakes_temp = struct.unpack('<HHHH', data[offset:offset+8])
            offset += 8
            
            # Band oppervlakte temperaturen (4x uint8)
            tyres_surface = struct.unpack('<BBBB', data[offset:offset+4])
            offset += 4
            
            # Band binnen temperaturen (4x uint8)
            tyres_inner = struct.unpack('<BBBB', data[offset:offset+4])
            offset += 4
            
            # Motor temperatuur
            engine_temp = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            
            # Band druk (4x float)
            tyres_pressure = struct.unpack('<ffff', data[offset:offset+16])
            offset += 16
            
            # Oppervlakte types (4x uint8)
            surface_type = struct.unpack('<BBBB', data[offset:offset+4])
            offset += 4
            
            telemetry = CarTelemetryData(
                *base_data,
                brakes_temp,
                tyres_surface,
                tyres_inner,
                engine_temp,
                tyres_pressure,
                surface_type
            )
            self.car_telemetry_data.append(telemetry)
        
        # MFD panel index en secondary player
        if offset + 2 <= len(data):
            self.mfd_panel_index = struct.unpack('<B', data[offset:offset+1])[0]
            offset += 1
            self.mfd_panel_index_secondary_player = struct.unpack('<B', data[offset:offset+1])[0]
            offset += 1
            self.suggested_gear = struct.unpack('<b', data[offset:offset+1])[0]
    
    def get_player_telemetry(self) -> CarTelemetryData:
        """Krijg telemetrie van speler"""
        return self.car_telemetry_data[self.header.player_car_index]
    
    def get_car_telemetry(self, car_index: int) -> CarTelemetryData:
        """Krijg telemetrie van specifieke auto"""
        if 0 <= car_index < len(self.car_telemetry_data):
            return self.car_telemetry_data[car_index]
        raise IndexError(f"Car index {car_index} buiten bereik")

@dataclass
class CarStatusData:
    """
    Status data voor 1 auto
    
    Bevat fuel, ERS, DRS, schade, etc.
    """
    traction_control: int
    anti_lock_brakes: int
    fuel_mix: int
    front_brake_bias: int
    pit_limiter_status: int
    fuel_in_tank: float
    fuel_capacity: float
    fuel_remaining_laps: float
    max_rpm: int
    idle_rpm: int
    max_gears: int
    drs_allowed: int
    drs_activation_distance: int
    actual_tyre_compound: int
    visual_tyre_compound: int
    tyres_age_laps: int
    vehicle_fia_flags: int
    engine_power_ice: float
    engine_power_mguk: float
    ers_store_energy: float
    ers_deploy_mode: int
    ers_harvested_this_lap_mguk: float
    ers_harvested_this_lap_mguh: float
    ers_deployed_this_lap: float
    network_paused: int
    
    def get_tyre_compound_name(self) -> str:
        """Krijg band compound naam"""
        try:
            return TyreCompound(self.actual_tyre_compound).name
        except ValueError:
            return f"UNKNOWN_{self.actual_tyre_compound}"

class CarStatusPacket:
    """
    Packet ID: 7 - Car Status
    Frequentie: Rate as specified in menus
    
    Status data voor alle auto's
    """
    
    def __init__(self, header: PacketHeader, data: bytes):
        self.header = header
        self.car_status_data: List[CarStatusData] = []
        
        offset = 29
        
        # Format voor CarStatusData
        fmt = '<BBBBBfffHHBBHBBBBffffBfffB'
        size = struct.calcsize(fmt)
        
        for i in range(MAX_CARS):
            if offset + size <= len(data):
                unpacked = struct.unpack(fmt, data[offset:offset+size])
                self.car_status_data.append(CarStatusData(*unpacked))
                offset += size
    
    def get_player_status(self) -> CarStatusData:
        """Krijg status van speler"""
        return self.car_status_data[self.header.player_car_index]
    
    def get_car_status(self, car_index: int) -> CarStatusData:
        """Krijg status van specifieke auto"""
        if 0 <= car_index < len(self.car_status_data):
            return self.car_status_data[car_index]
        raise IndexError(f"Car index {car_index} buiten bereik")

@dataclass
class CarDamageData:
    """
    Schade data voor 1 auto
    """
    tyres_wear: Tuple[float, float, float, float]  # RL, RR, FL, FR (percentage)
    tyres_damage: Tuple[int, int, int, int]  # percentage
    brakes_damage: Tuple[int, int, int, int]  # percentage
    tyre_blisters: Tuple[int, int, int, int]  # percentage (nieuw in F1 25)
    front_left_wing_damage: int  # percentage
    front_right_wing_damage: int
    rear_wing_damage: int
    floor_damage: int
    diffuser_damage: int
    sidepod_damage: int
    drs_fault: int  # 0 = OK, 1 = fault
    ers_fault: int
    gear_box_damage: int
    engine_damage: int
    engine_mguh_wear: int
    engine_es_wear: int
    engine_ce_wear: int
    engine_ice_wear: int
    engine_mguk_wear: int
    engine_tc_wear: int
    engine_blown: int  # 0 = OK, 1 = fault
    engine_seized: int
    
    def has_damage(self) -> bool:
        """Check of auto schade heeft"""
        return (max(self.tyres_damage) > 0 or
                max(self.brakes_damage) > 0 or
                self.front_left_wing_damage > 0 or
                self.front_right_wing_damage > 0 or
                self.rear_wing_damage > 0 or
                self.floor_damage > 0 or
                self.diffuser_damage > 0 or
                self.sidepod_damage > 0 or
                self.gear_box_damage > 0 or
                self.engine_damage > 0)
    
    def get_total_damage_percentage(self) -> float:
        """Krijg totale schade percentage (gemiddelde)"""
        damages = [
            *self.tyres_damage,
            *self.brakes_damage,
            self.front_left_wing_damage,
            self.front_right_wing_damage,
            self.rear_wing_damage,
            self.floor_damage,
            self.diffuser_damage,
            self.sidepod_damage,
            self.gear_box_damage,
            self.engine_damage
        ]
        return sum(damages) / len(damages)

class CarDamagePacket:
    """
    Packet ID: 10 - Car Damage
    Frequentie: 2 per seconde
    
    Schade status voor alle auto's
    """
    
    def __init__(self, header: PacketHeader, data: bytes):
        self.header = header
        self.car_damage_data: List[CarDamageData] = []
        
        offset = 29
        
        for i in range(MAX_CARS):
            # Tyre wear (4x float)
            tyres_wear = struct.unpack('<ffff', data[offset:offset+16])
            offset += 16
            
            # Damage data (veel uint8 waarden)
            fmt = '<BBBBBBBBBBBBBBBBBBBBBBBBBBBB'
            size = struct.calcsize(fmt)
            damage_data = struct.unpack(fmt, data[offset:offset+size])
            offset += size
            
            # Split damage_data in juiste velden
            damage = CarDamageData(
                tyres_wear,
                damage_data[0:4],    # tyres_damage
                damage_data[4:8],    # brakes_damage
                damage_data[8:12],   # tyre_blisters
                *damage_data[12:]    # rest van damage fields
            )
            self.car_damage_data.append(damage)
    
    def get_player_damage(self) -> CarDamageData:
        """Krijg schade van speler"""
        return self.car_damage_data[self.header.player_car_index]
    
    def get_car_damage(self, car_index: int) -> CarDamageData:
        """Krijg schade van specifieke auto"""
        if 0 <= car_index < len(self.car_damage_data):
            return self.car_damage_data[car_index]
        raise IndexError(f"Car index {car_index} buiten bereik")