"""
F1 25 Telemetry - Session Parser
Parse Session packet (ID 1) met track en weather informatie
(Versie 8: Correcte struct format string syntax)
"""

from dataclasses import dataclass, field
from typing import Optional, List
from .base_parser import BaseParser
from .packet_header import PacketHeader
from .packet_types import SessionType, Weather
import struct
import logging


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
    Parsed session packet data (F1 25 Volledige Specificatie)
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
    safety_car_status: int
    network_game: int
    num_weather_forecast_samples: int
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
    equal_car_performance: int
    recovery_mode: int
    flashback_limit: int
    surface_type: int
    low_fuel_mode: int
    race_starts: int
    tyre_temperature: int
    pit_lane_tyre_sim: int
    car_damage: int
    car_damage_rate: int
    collisions: int
    collisions_off_for_first_lap_only: int
    mp_unsafe_pit_release: int
    mp_off_for_griefing: int
    corner_cutting_stringency: int
    parc_ferme_rules: int
    pit_stop_experience: int
    safety_car: int
    safety_car_experience: int
    formation_lap: int
    formation_lap_experience: int
    red_flags: int
    affects_licence_level_solo: int
    affects_licence_level_mp: int
    num_sessions_in_weekend: int
    sector2_lap_distance_start: float
    sector3_lap_distance_start: float

    marshal_zones: list = field(default_factory=list)
    weather_forecast_samples: list = field(default_factory=list)
    weekend_structure: list = field(default_factory=list)


class SessionParser(BaseParser):
    """Parser voor Session packets (ID 1)"""

    def __init__(self):
        """Initialiseer de parser en roep de base class init aan."""
        super().__init__()

    # 21 Marshal Zones
    NUM_MARSHAL_ZONES = 21
    MARSHAL_ZONE_FORMAT = "<fb"  # 5 bytes

    # 64 Weather Forecast Samples
    NUM_WEATHER_SAMPLES = 64
    WEATHER_SAMPLE_FORMAT = "<BBBbbB"  # 6 bytes

    # 12 Weekend Structure Samples
    NUM_WEEKEND_SESSIONS = 12
    WEEKEND_STRUCTURE_FORMAT = "<B"  # 1 byte

    # --- DEFINITIEVE GECORRIGEERDE STRUCT FORMATS ---

    # Deel 1 (16 velden)
    SESSION_DATA_HEADER_FORMAT = "<BbbBHBbBHHBBBBBB"  # 19 bytes

    # Deel 2 (3 velden)
    SESSION_DATA_MID_FORMAT = "<BBB"  # 3 bytes

    # Deel 3 (55 velden) - F1 25 Spec
    # Gecorrigeerd naar EEN enkele string
    SESSION_DATA_FOOTER_FORMAT = (
        "<BBIII"  # 5
        "BBB"  # 3
        "BBBBBBBBB"  # 9
        "B"  # game_mode
        "B"  # rule_set
        "I"  # time_of_day
        "B"  # session_length
        "BBBB"  # 4 units
        "BBB"  # 3 SC periods
        "BBBBBB"  # 6 (equal_car ... race_starts)
        "BBBBBB"  # 6 (tyre_temp ... collisions_off)
        "BBBBBB"  # 6 (mp_unsafe ... safety_car)
        "BBBBBB"  # 6 (safety_car_exp ... licence_solo)
        "B"  # licence_mp
        "B"  # num_sessions
        "ff"  # 2 sector distances
    )  # Totaal 55 velden / 71 bytes

    # --- EINDE FIX ---

    def parse(self, header: PacketHeader, payload: bytes) -> Optional[SessionData]:
        try:
            # 1. Parse het eerste deel (16 velden)
            header_data = self.unpack_safely(self.SESSION_DATA_HEADER_FORMAT, payload, offset=0)
            if not header_data:
                self.logger.error("SessionParser: Kon HEADER_FORMAT niet uitpakken.")
                return None
            offset = struct.calcsize(self.SESSION_DATA_HEADER_FORMAT)  # 19 bytes

            # 2. Parse Marshal Zones (21 zones * 5 bytes)
            marshal_zones_list = []
            for i in range(self.NUM_MARSHAL_ZONES):
                zone_data = self.unpack_safely(self.MARSHAL_ZONE_FORMAT, payload, offset)
                if zone_data:
                    marshal_zones_list.append(MarshalZone(zone_start=zone_data[0], zone_flag=zone_data[1]))
                offset += struct.calcsize(self.MARSHAL_ZONE_FORMAT)  # 105 bytes. Offset = 124

            # 3. Parse het middelste deel (3 velden)
            mid_data = self.unpack_safely(self.SESSION_DATA_MID_FORMAT, payload, offset)
            if not mid_data:
                self.logger.error("SessionParser: Kon MID_FORMAT niet uitpakken.")
                return None
            offset += struct.calcsize(self.SESSION_DATA_MID_FORMAT)  # 3 bytes. Offset = 127

            # 4. Parse Weather Forecast Samples (64 samples * 6 bytes)
            weather_samples_list = []
            for i in range(self.NUM_WEATHER_SAMPLES):
                sample_data = self.unpack_safely(self.WEATHER_SAMPLE_FORMAT, payload, offset)
                if sample_data:
                    weather_samples_list.append(WeatherForecastSample(
                        session_type=sample_data[0], time_offset=sample_data[1],
                        weather=sample_data[2], track_temperature=sample_data[3],
                        air_temperature=sample_data[4], rain_percentage=sample_data[5]
                    ))
                offset += struct.calcsize(self.WEATHER_SAMPLE_FORMAT)  # 384 bytes. Offset = 511

            # 5. Parse het *volledige* laatste deel (55 velden)
            footer_data = self.unpack_safely(self.SESSION_DATA_FOOTER_FORMAT, payload, offset)
            if not footer_data:
                self.logger.error(f"SessionParser: Kon FOOTER_FORMAT niet uitpakken. Offset was {offset}")
                return None
            offset += struct.calcsize(self.SESSION_DATA_FOOTER_FORMAT)  # 71 bytes. Offset = 582

            # 6. Parse Weekend Structure (12 samples * 1 byte)
            weekend_structure_list = []
            for i in range(self.NUM_WEEKEND_SESSIONS):
                # We moeten endianness toevoegen aan de format string
                weekend_data = self.unpack_safely(self.WEEKEND_STRUCTURE_FORMAT, payload, offset)
                if weekend_data:
                    weekend_structure_list.append(weekend_data[0])
                offset += struct.calcsize(self.WEEKEND_STRUCTURE_FORMAT)  # 12 bytes. Offset = 594

            # --- Combineer en creëer het SessionData object ---

            # Totaal: 16 (header) + 3 (mid) + 55 (footer) = 74 velden
            unpacked = list(header_data) + list(mid_data) + list(footer_data)

            return SessionData(
                header=header,
                # Header data (16 velden, index 0-15)
                weather=unpacked[0], track_temperature=unpacked[1], air_temperature=unpacked[2],
                total_laps=unpacked[3], track_length=unpacked[4], session_type=unpacked[5],
                track_id=unpacked[6], formula=unpacked[7], session_time_left=unpacked[8],
                session_duration=unpacked[9], pit_speed_limit=unpacked[10], game_paused=bool(unpacked[11]),
                is_spectating=bool(unpacked[12]), spectator_car_index=unpacked[13],
                sli_pro_native_support=bool(unpacked[14]), num_marshal_zones=unpacked[15],

                # Mid data (3 velden, index 16-18)
                safety_car_status=unpacked[16], network_game=unpacked[17], num_weather_forecast_samples=unpacked[18],

                # Footer data (55 velden, index 19-73)
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
                num_red_flag_periods=unpacked[46],
                equal_car_performance=unpacked[47],
                recovery_mode=unpacked[48],
                flashback_limit=unpacked[49],
                surface_type=unpacked[50],
                low_fuel_mode=unpacked[51],
                race_starts=unpacked[52],
                tyre_temperature=unpacked[53],
                pit_lane_tyre_sim=unpacked[54],
                car_damage=unpacked[55],
                car_damage_rate=unpacked[56],
                collisions=unpacked[57],
                collisions_off_for_first_lap_only=unpacked[58],
                mp_unsafe_pit_release=unpacked[59],
                mp_off_for_griefing=unpacked[60],
                corner_cutting_stringency=unpacked[61],
                parc_ferme_rules=unpacked[62],
                pit_stop_experience=unpacked[63],
                safety_car=unpacked[64],
                safety_car_experience=unpacked[65],
                formation_lap=unpacked[66],
                formation_lap_experience=unpacked[67],
                red_flags=unpacked[68],
                affects_licence_level_solo=unpacked[69],
                affects_licence_level_mp=unpacked[70],
                num_sessions_in_weekend=unpacked[71],
                sector2_lap_distance_start=unpacked[72],
                sector3_lap_distance_start=unpacked[73],

                # Arrays
                marshal_zones=marshal_zones_list,
                weather_forecast_samples=weather_samples_list,
                weekend_structure=weekend_structure_list
            )

        except IndexError as e:
            self.logger.error(f"Session parse fout (IndexError): {e}. Waarschijnlijk een struct mismatch.",
                              exc_info=True)
            return None
        except Exception as e:
            self.logger.error(f"Onverwachte session parse fout: {e}", exc_info=True)
            return None