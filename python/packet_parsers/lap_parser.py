"""
F1 25 Telemetry System - Lap Data Parser (Packet 2)
(Versie 8: Fout 'bad char' OPGELOST. Geen ** meer.)
"""
import struct
from dataclasses import dataclass
from .base_parser import BaseParser
from .packet_header import PacketHeader
from typing import List

# Importeer de correcte logger
try:
    from services.logger_services import logger_service
except ImportError:
    import logging
    logger_service = logging.getLogger('LapParser')

lap_parser_logger = logger_service.get_logger('LapParser')


@dataclass
class LapData:
    """
    Dataclass for the lap data of one car.
    (Volledige F1 25 structuur, 61 bytes, 1:1 met spec)
    """
    last_lap_time_ms: int = 0             # uint32 (4)
    current_lap_time_ms: int = 0          # uint32 (4)
    sector1_time_ms: int = 0              # uint16 (2)
    sector1_time_minutes: int = 0         # uint16 (2)
    sector2_time_ms: int = 0              # uint16 (2)
    sector2_time_minutes: int = 0         # uint16 (2)
    delta_to_car_in_front_ms: int = 0     # uint16 (2)
    delta_to_car_in_front_minutes: int = 0 # uint16 (2)
    delta_to_race_leader_ms: int = 0      # uint16 (2)
    delta_to_race_leader_minutes: int = 0  # uint16 (2)
    lap_distance: float = 0.0             # float (4)
    total_distance: float = 0.0           # float (4)
    safety_car_delta: float = 0.0         # float (4)
    car_position: int = 0                 # uint8 (1)
    current_lap_num: int = 0              # uint8 (1)
    pit_status: int = 0                   # uint8 (1)
    num_pit_stops: int = 0                # uint8 (1)
    sector: int = 0                       # uint8 (1)
    current_lap_invalid: int = 0          # uint8 (1)
    penalties: int = 0                    # uint8 (1)
    total_warnings: int = 0               # uint8 (1)
    corner_cutting_warnings: int = 0      # uint8 (1)
    num_unserved_drive_through_pens: int = 0 # uint8 (1)
    num_unserved_stop_go_pens: int = 0    # uint8 (1)
    grid_position: int = 0                # uint8 (1)
    driver_status: int = 0                # uint8 (1)
    result_status: int = 0                # uint8 (1)
    pit_lane_timer_active: int = 0        # uint8 (1)
    pit_lane_time_in_lane_ms: int = 0     # uint16 (2)
    pit_stop_timer_ms: int = 0            # uint16 (2)
    pit_stop_should_serve_pen: int = 0    # uint8 (1)
    speed_trap_fastest_speed: float = 0.0 # float (4)
    speed_trap_fastest_lap: int = 0       # uint8 (1)

    # --- HET DEFINITIEVE GECORRIGEERDE PACKET FORMAT (61 bytes) ---
    # Gecorrigeerd van de 'bad char' fout
    PACKET_FORMAT = "<IIHHHHHHHHfffBBBBBBBBBBBBBBBHHBfB"
    # --- EINDE CORRECTIE ---

    PACKET_LEN = 88 # De *totale* struct grootte per auto is 88 bytes
    KNOWN_FIELDS_LEN = 61 # De *data* die we lezen is 61 bytes

    @staticmethod
    def from_bytes(data: bytes) -> 'LapData':
        """Unpackt bytes naar een LapData object."""
        try:
            if len(data) < LapData.PACKET_LEN:
                raise struct.error(f"Data te kort. Expected {LapData.PACKET_LEN}, got {len(data)}")

            # We pakken alleen de 61 bytes uit die we kennen
            unpacked = struct.unpack(LapData.PACKET_FORMAT, data[:LapData.KNOWN_FIELDS_LEN])

            return LapData(*unpacked)

        except struct.error as e:
            lap_parser_logger.error(f"LapData unpack failed: {e}. Format: {LapData.PACKET_FORMAT}, Expected len: {LapData.KNOWN_FIELDS_LEN}, Got data len: {len(data)}")
            return LapData() # Return een leeg object bij fout

@dataclass
class LapDataPacket(BaseParser):
    """
    Dataclass voor Packet 2.
    """
    header: PacketHeader
    lap_data: List[LapData]

    def __init__(self, header: PacketHeader, data: bytes):
        self.header = header
        self.lap_data = self.parse(data)

    def parse(self, data: bytes) -> List[LapData]:
        """Parse de volledige payload voor 22 auto's."""
        all_lap_data = []
        for i in range(22):
            start = i * LapData.PACKET_LEN
            end = start + LapData.PACKET_LEN
            if end > len(data):
                lap_parser_logger.warning(f"Data te kort voor auto {i+1} in LapDataPacket.")
                break
            all_lap_data.append(LapData.from_bytes(data[start:end]))
        return all_lap_data

class LapDataParser:
    """
    Parser voor Lap Data Packet (Packet 2).
    """
    def parse(self, header: PacketHeader, data: bytes) -> LapDataPacket:
        """Parse het pakket en retourneer een LapDataPacket object."""
        return LapDataPacket(header, data)