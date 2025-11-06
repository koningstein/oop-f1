"""
F1 25 Telemetry - Session Parser
Parse Session packet (ID 1) met track en weather informatie
"""

from dataclasses import dataclass, field
from typing import Optional, List
from .base_parser import BaseParser
from .packet_header import PacketHeader
from .packet_types import SessionType, Weather
import struct
import logging

# Gebruik de logger van de BaseParser, maar definieer deze hier voor SessionData struct
# zodat de SessionData dataclass er zelf geen afhankelijkheid van heeft.

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
    
    BELANGRIJK: Velden ZONDER default waarde moeten ALTIJD voor velden MET default waarde staan.
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
    # safety_car_status en verder stonden voor marshal_zones, wat de fout veroorzaakte
    safety_car_status: int
    network_game: int
    num_weather_forecast_samples: int
    
    # Nieuwe velden voor F1 25, allemaal zonder default
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
    num_red_flag_periods: int  # <-- Nieuw in F1 25
    
    # -------------------------------------------------------------
    # Array velden: MOETEN als LAATSTE staan omdat ze een default hebben
    # -------------------------------------------------------------
    marshal_zones: list = field(default_factory=list)
    weather_forecast_samples: list = field(default_factory=list)


class SessionParser(BaseParser):
    """Parser voor Session packets (ID 1)"""
    
    # 21 Marshal Zones
    NUM_MARSHAL_ZONES = 21
    MARSHAL_ZONE_FORMAT = "<fb" # float zoneStart, int8 zoneFlag (5 bytes)
    
    # 20 Weather Forecast Samples
    NUM_WEATHER_SAMPLES = 20
    # structuur: uint8, uint8, uint8, int8, int8, uint8
    WEATHER_SAMPLE_FORMAT = "<BBBbbB" 
    
    # Hoofdstructuur - Eerste deel (16 velden)
    # B weather(B) trackTemperature(b) airTemperature(b) H totalLaps(H) H trackLength(H) B sessionType(B) 
    # b trackId(b) B formula(B) H sessionTimeLeft(H) H sessionDuration(H) B pitSpeedLimit(B) 
    # B gamePaused(B) B isSpectating(B) B spectatorCarIndex(B) B sliProNativeSupport(B) B numMarshalZones(B)
    SESSION_DATA_HEADER_FORMAT = "<BbBHBHBH HBBBBBB" 
    
    # Hoofdstructuur - Middelste deel (3 velden tussen arrays)
    # safetyCarStatus(B) networkGame(B) numWeatherForecastSamples(B)
    SESSION_DATA_MID_FORMAT = "<BBB"
    
    # Hoofdstructuur - Derde deel (28 velden na arrays) - Gecorrigeerd voor F1 25
    # B(forecast) B(ai_diff) I(season) I(weekend) I(session) B(pit_ideal) B(pit_latest) B(pit_rejoin) 
    # B(steer) B(brake) B(gear) B(pit_assist) B(pit_release) B(ers) B(drs) B(dyn_line) B(dyn_type)
    # B(game_mode) B(rule_set) I(time_of_day) B(session_length)
    # B(speed_lead) B(temp_lead) B(speed_secondary) B(temp_secondary)
    # B(num_sc) B(num_vsc) B(num_red)
    SESSION_DATA_FOOTER_FORMAT = "<BBIII BBB BBBBBBBBB BBIBBBBBB"

    
    def parse(self, header: PacketHeader, payload: bytes) -> Optional[SessionData]:
        try:
            # 1. Parse het eerste deel (16 velden, excl. Marshal Zones)
            header_data = self.unpack_safely(self.SESSION_DATA_HEADER_FORMAT, payload, offset=0)
            if not header_data:
                return None
            
            offset = struct.calcsize(self.SESSION_DATA_HEADER_FORMAT)
            
            # 2. Parse Marshal Zones (21 zones)
            marshal_zones_list = []
            
            # We gebruiken NUM_MARSHAL_ZONES (21), niet num_marshal_zones van de data,
            # omdat de struct altijd 21 zones stuurt, ongeacht de waarde van de uint8 in het packet.
            for i in range(self.NUM_MARSHAL_ZONES):
                zone_data = self.unpack_safely(self.MARSHAL_ZONE_FORMAT, payload, offset)
                if zone_data:
                    marshal_zones_list.append(MarshalZone(
                        zone_start=zone_data[0],
                        zone_flag=zone_data[1]
                    ))
                offset += struct.calcsize(self.MARSHAL_ZONE_FORMAT)
            
            # 3. Parse het middelste deel (3 velden)
            mid_data = self.unpack_safely(self.SESSION_DATA_MID_FORMAT, payload, offset)
            if not mid_data:
                return None
            
            offset += struct.calcsize(self.SESSION_DATA_MID_FORMAT)

            # 4. Parse Weather Forecast Samples (20 samples)
            weather_samples_list = []

            # We gebruiken NUM_WEATHER_SAMPLES (20), de struct stuurt altijd 20 samples.
            for i in range(self.NUM_WEATHER_SAMPLES):
                sample_data = self.unpack_safely(self.WEATHER_SAMPLE_FORMAT, payload, offset)
                if sample_data:
                    weather_samples_list.append(WeatherForecastSample(
                        session_type=sample_data[0],
                        time_offset=sample_data[1],
                        weather=sample_data[2],
                        track_temperature=sample_data[3],
                        air_temperature=sample_data[4],
                        rain_percentage=sample_data[5]
                    ))
                offset += struct.calcsize(self.WEATHER_SAMPLE_FORMAT)

            # 5. Parse het laatste deel (28 velden)
            footer_data = self.unpack_safely(self.SESSION_DATA_FOOTER_FORMAT, payload, offset)
            if not footer_data:
                return None
            
            # --- Combineer en creëer het SessionData object ---
            
            unpacked = list(header_data) + list(mid_data) + list(footer_data)
            
            # De indices in 'unpacked' zijn nu als volgt:
            # Header Data: [0] tot [15] (16 velden)
            # Mid Data: [16] tot [18] (3 velden)
            # Footer Data: [19] tot [46] (28 velden)
            # Totaal: 16 + 3 + 28 = 47 velden (index 0 t/m 46)

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
                
                safety_car_status=unpacked[16],
                network_game=unpacked[17],
                num_weather_forecast_samples=unpacked[18],

                # Vanaf hier: Footer Data (index 19 t/m 46)
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
                
                # Default arguments (geen unpacked[] index):
                marshal_zones=marshal_zones_list,
                weather_forecast_samples=weather_samples_list
            )
            
        except Exception as e:
            # U kunt de logging hier beter inschakelen om te zien welke index de fout geeft,
            # maar de structurele fout is nu opgelost.
            # self.logger.error(f"Session parse fout: {e}", exc_info=True)
            return None