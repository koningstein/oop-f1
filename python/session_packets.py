"""
F1 25 Telemetry - Session Packets
Bevat Session en Event packet parsers
"""

import struct
from dataclasses import dataclass
from packet_header import PacketHeader
from packet_types import SessionType, Weather, TrackID, EventCode, MAX_CARS

class SessionPacket:
    """
    Packet ID: 1 - Session Data
    Frequentie: 2x per seconde
    
    Data over de sessie - circuit, tijd over, weer, etc.
    """
    
    def __init__(self, header: PacketHeader, data: bytes):
        self.header = header
        offset = 29
        
        # Parse session data
        self.weather = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        self.track_temperature = struct.unpack('<b', data[offset:offset+1])[0]  # signed
        offset += 1
        self.air_temperature = struct.unpack('<b', data[offset:offset+1])[0]  # signed
        offset += 1
        self.total_laps = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        self.track_length = struct.unpack('<H', data[offset:offset+2])[0]
        offset += 2
        self.session_type = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        self.track_id = struct.unpack('<b', data[offset:offset+1])[0]  # signed
        offset += 1
        self.formula = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        self.session_time_left = struct.unpack('<H', data[offset:offset+2])[0]
        offset += 2
        self.session_duration = struct.unpack('<H', data[offset:offset+2])[0]
        offset += 2
        self.pit_speed_limit = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        self.game_paused = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        self.is_spectating = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        self.spectator_car_index = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        self.sli_pro_native_support = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        self.num_marshal_zones = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        
        # Marshal zones (max 21)
        self.marshal_zones = []
        for i in range(21):
            zone_start = struct.unpack('<f', data[offset:offset+4])[0]
            offset += 4
            zone_flag = struct.unpack('<b', data[offset:offset+1])[0]
            offset += 1
            self.marshal_zones.append({'zone_start': zone_start, 'zone_flag': zone_flag})
        
        # Safety car status
        self.safety_car_status = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        self.network_game = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        
        # Weather forecast (max 56 samples)
        self.num_weather_forecast_samples = struct.unpack('<B', data[offset:offset+1])[0]
        offset += 1
        
        self.weather_forecast_samples = []
        for i in range(56):
            if offset + 8 <= len(data):
                session_type = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                time_offset = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                weather = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                track_temp = struct.unpack('<b', data[offset:offset+1])[0]
                offset += 1
                track_temp_change = struct.unpack('<b', data[offset:offset+1])[0]
                offset += 1
                air_temp = struct.unpack('<b', data[offset:offset+1])[0]
                offset += 1
                air_temp_change = struct.unpack('<b', data[offset:offset+1])[0]
                offset += 1
                rain_percentage = struct.unpack('<B', data[offset:offset+1])[0]
                offset += 1
                
                self.weather_forecast_samples.append({
                    'session_type': session_type,
                    'time_offset': time_offset,
                    'weather': weather,
                    'track_temperature': track_temp,
                    'track_temperature_change': track_temp_change,
                    'air_temperature': air_temp,
                    'air_temperature_change': air_temp_change,
                    'rain_percentage': rain_percentage
                })
    
    def get_weather_name(self) -> str:
        """Krijg leesbare weer naam"""
        try:
            return Weather(self.weather).name
        except ValueError:
            return f"UNKNOWN_{self.weather}"
    
    def get_track_name(self) -> str:
        """Krijg circuit naam"""
        try:
            return TrackID(self.track_id).name
        except ValueError:
            return f"UNKNOWN_{self.track_id}"
    
    def get_session_type_name(self) -> str:
        """Krijg sessie type naam"""
        try:
            return SessionType(self.session_type).name
        except ValueError:
            return f"UNKNOWN_{self.session_type}"
    
    def __str__(self):
        return (f"Session({self.get_session_type_name()} @ {self.get_track_name()}, "
                f"Laps: {self.total_laps}, Weather: {self.get_weather_name()}, "
                f"Time left: {self.session_time_left}s)")

class EventPacket:
    """
    Packet ID: 3 - Event Data
    Frequentie: Bij specifieke events
    
    Diverse opmerkelijke events die gebeuren tijdens sessie
    """
    
    def __init__(self, header: PacketHeader, data: bytes):
        self.header = header
        offset = 29
        
        # Event string code (4 chars)
        self.event_string_code = data[offset:offset+4].decode('utf-8')
        offset += 4
        
        # Event details afhankelijk van type
        self.event_details = None
        
        # Parse event-specifieke data
        if self.event_string_code == EventCode.FASTEST_LAP:
            self.event_details = {
                'vehicle_idx': struct.unpack('<B', data[offset:offset+1])[0],
                'lap_time': struct.unpack('<f', data[offset+1:offset+5])[0]
            }
        
        elif self.event_string_code == EventCode.RETIREMENT:
            self.event_details = {
                'vehicle_idx': struct.unpack('<B', data[offset:offset+1])[0],
                'retirement_reason': struct.unpack('<B', data[offset+1:offset+2])[0]
            }
        
        elif self.event_string_code == EventCode.TEAM_MATE_IN_PITS:
            self.event_details = {
                'vehicle_idx': struct.unpack('<B', data[offset:offset+1])[0]
            }
        
        elif self.event_string_code == EventCode.RACE_WINNER:
            self.event_details = {
                'vehicle_idx': struct.unpack('<B', data[offset:offset+1])[0]
            }
        
        elif self.event_string_code == EventCode.PENALTY_ISSUED:
            self.event_details = {
                'penalty_type': struct.unpack('<B', data[offset:offset+1])[0],
                'infringement_type': struct.unpack('<B', data[offset+1:offset+2])[0],
                'vehicle_idx': struct.unpack('<B', data[offset+2:offset+3])[0],
                'other_vehicle_idx': struct.unpack('<B', data[offset+3:offset+4])[0],
                'time': struct.unpack('<B', data[offset+4:offset+5])[0],
                'lap_num': struct.unpack('<B', data[offset+5:offset+6])[0],
                'places_gained': struct.unpack('<B', data[offset+6:offset+7])[0]
            }
        
        elif self.event_string_code == EventCode.SPEED_TRAP_TRIGGERED:
            self.event_details = {
                'vehicle_idx': struct.unpack('<B', data[offset:offset+1])[0],
                'speed': struct.unpack('<f', data[offset+1:offset+5])[0],
                'is_overall_fastest_in_session': struct.unpack('<B', data[offset+5:offset+6])[0],
                'is_driver_fastest_in_session': struct.unpack('<B', data[offset+6:offset+7])[0],
                'fastest_vehicle_idx_in_session': struct.unpack('<B', data[offset+7:offset+8])[0],
                'fastest_speed_in_session': struct.unpack('<f', data[offset+8:offset+12])[0]
            }
        
        elif self.event_string_code == EventCode.START_LIGHTS:
            self.event_details = {
                'num_lights': struct.unpack('<B', data[offset:offset+1])[0]
            }
        
        elif self.event_string_code == EventCode.FLASHBACK:
            self.event_details = {
                'flashback_frame_identifier': struct.unpack('<I', data[offset:offset+4])[0],
                'flashback_session_time': struct.unpack('<f', data[offset+4:offset+8])[0]
            }
        
        elif self.event_string_code == EventCode.BUTTON_STATUS:
            self.event_details = {
                'button_status': struct.unpack('<I', data[offset:offset+4])[0]
            }
        
        elif self.event_string_code == EventCode.OVERTAKE:
            self.event_details = {
                'overtaking_vehicle_idx': struct.unpack('<B', data[offset:offset+1])[0],
                'being_overtaken_vehicle_idx': struct.unpack('<B', data[offset+1:offset+2])[0]
            }
    
    def __str__(self):
        return f"Event({self.event_string_code}: {self.event_details})"