"""
F1 25 Telemetry - Session Parser
Parse Session packet (ID 1) met track en weather informatie
"""

from dataclasses import dataclass
from typing import Optional
from parsers.base_parser import BaseParser
from parsers.packet_header import PacketHeader
from parsers.packet_types import SessionType, Weather

@dataclass
class MarshalZone:
    """Marshal zone data"""
    zone_start: float
    zone_flag: int

@dataclass
class WeatherForecastSample:
    """Weather forecast sample"""
    session_type: int
    time_offset: int
    weather: int
    track_temperature: int
    air_temperature: int
    rain_percentage: int

@dataclass
class SessionData:
    """
    Parsed session packet data
    """
    header: PacketHeader
    weather: int
    track_temperature: int
    air_temperature: int
    total_laps: int
    track_length: int
    session_type: int
    track_id: int
    formula: int
    session_time_left: int
    session_duration: int
    pit_speed_limit: int
    game_paused: bool
    is_spectating: bool
    spectator_car_index: int
    sli_pro_native_support: bool
    num_marshal_zones: int
    marshal_zones: list
    safety_car_status: int
    network_game: bool
    num_weather_forecast_samples: int
    weather_forecast_samples: list
    forecast_accuracy: int
    ai_difficulty: int
    season_link_identifier: int
    weekend_link_identifier: int
    session_link_identifier: int
    pit_stop_window_ideal_lap: int
    pit_stop_window_latest_lap: int
    pit_stop_rejoin_position: int
    steering_assist: bool
    braking_assist: int
    gearbox_assist: int
    pit_assist: bool
    pit_release_assist: bool
    ers_assist: bool
    drs_assist: bool
    dynamic_racing_line: int
    dynamic_racing_line_type: int
    game_mode: int
    rule_set: int
    time_of_day: int
    session_length: int
    speed_units_lead_player: int
    temperature_units_lead_player: int
    speed_units_secondary_player: int
    temperature_units_secondary_player: int
    num_safety_car_periods: int
    num_virtual_safety_car_periods: int
    num_red_flag_periods: int

class SessionParser(BaseParser):
    """Parser voor Session packets (ID 1)"""
    
    # Format voor session data (zonder marshal zones en weather forecast)
    SESSION_FORMAT = "<BBbBHBbbHHBBBBBBBBBBBIIIBBBBBBBBBBBBBBBBBBBB"
    
    def parse(self, header: PacketHeader, payload: bytes) -> Optional[SessionData]:
        """
        Parse session packet
        
        Args:
            header: Packet header
            payload: Packet payload
            
        Returns:
            SessionData object of None
        """
        if not self.validate_payload_size(payload, 632):
            return None
        
        try:
            # Parse basis session info
            unpacked = self.unpack_safely(self.SESSION_FORMAT, payload, 0)
            if not unpacked:
                return None
            
            offset = 52  # Na basis data
            
            # Parse marshal zones
            num_marshal_zones = unpacked[16]
            marshal_zones = []
            for i in range(21):  # Max 21 zones
                zone_data = self.unpack_safely("<fB", payload, offset)
                if zone_data and i < num_marshal_zones:
                    marshal_zones.append(MarshalZone(
                        zone_start=zone_data[0],
                        zone_flag=zone_data[1]
                    ))
                offset += 5
            
            # Parse weather forecast samples
            offset = 157  # Start van weather forecast
            num_forecast = unpacked[18]
            weather_samples = []
            for i in range(56):  # Max 56 samples
                sample_data = self.unpack_safely("<BBBbbBBBBB", payload, offset)
                if sample_data and i < num_forecast:
                    weather_samples.append(WeatherForecastSample(
                        session_type=sample_data[0],
                        time_offset=sample_data[1],
                        weather=sample_data[2],
                        track_temperature=sample_data[3],
                        air_temperature=sample_data[4],
                        rain_percentage=sample_data[5]
                    ))
                offset += 10
            
            return SessionData(
                header=header,
                weather=unpacked[0],
                track_temperature=unpacked[1],
                air_temperature=unpacked[2],
                total_laps=unpacked[3],
                track_length=unpacked[4],
                session_type=unpacked[5],
                track_id=unpacked[6],
                formula=unpacked[7],
                session_time_left=unpacked[8],
                session_duration=unpacked[9],
                pit_speed_limit=unpacked[10],
                game_paused=bool(unpacked[11]),
                is_spectating=bool(unpacked[12]),
                spectator_car_index=unpacked[13],
                sli_pro_native_support=bool(unpacked[14]),
                num_marshal_zones=unpacked[15],
                marshal_zones=marshal_zones,
                safety_car_status=unpacked[17],
                network_game=bool(unpacked[18]),
                num_weather_forecast_samples=num_forecast,
                weather_forecast_samples=weather_samples,
                forecast_accuracy=unpacked[19],
                ai_difficulty=unpacked[20],
                season_link_identifier=unpacked[21],
                weekend_link_identifier=unpacked[22],
                session_link_identifier=unpacked[23],
                pit_stop_window_ideal_lap=unpacked[24],
                pit_stop_window_latest_lap=unpacked[25],
                pit_stop_rejoin_position=unpacked[26],
                steering_assist=bool(unpacked[27]),
                braking_assist=unpacked[28],
                gearbox_assist=unpacked[29],
                pit_assist=bool(unpacked[30]),
                pit_release_assist=bool(unpacked[31]),
                ers_assist=bool(unpacked[32]),
                drs_assist=bool(unpacked[33]),
                dynamic_racing_line=unpacked[34],
                dynamic_racing_line_type=unpacked[35],
                game_mode=unpacked[36],
                rule_set=unpacked[37],
                time_of_day=unpacked[38],
                session_length=unpacked[39],
                speed_units_lead_player=unpacked[40],
                temperature_units_lead_player=unpacked[41],
                speed_units_secondary_player=unpacked[42],
                temperature_units_secondary_player=unpacked[43],
                num_safety_car_periods=unpacked[44],
                num_virtual_safety_car_periods=unpacked[45],
                num_red_flag_periods=unpacked[46]
            )
            
        except Exception as e:
            self.logger.error(f"Session parse fout: {e}")
            return None