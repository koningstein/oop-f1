"""
F1 25 Telemetry System - Lap Data Parser (Packet 2)
(Versie 11: Correcte F1 25 struct size (57 bytes) o.b.v. C++ Spec en error log)
"""
import struct
from dataclasses import dataclass
from .base_parser import BaseParser
from .packet_header import PacketHeader
from typing import List, Optional

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
    (F1 25 structuur, 57 bytes, 1:1 met C++ spec)

    """
    # Het C-struct format (o.b.v. F1 25 Telemetry Output Structures.txt)
    # II (2*4=8)
    # HBHBHBHB ( (2+1)*4 = 12 )
    # fff (3*4=12)
    # BBBBBBBBBBBBBBB (15*1=15)
    # HH (2*2=4)
    # B (1)
    # f (4)
    # B (1)
    # Totaal: 8 + 12 + 12 + 15 + 4 + 1 + 4 + 1 = 57 bytes.
    STRUCT_FORMAT = '<IIHBHBHBHBfffBBBBBBBBBBBBBBBHHBfB'
    PACKET_LEN = struct.calcsize(STRUCT_FORMAT) # = 57 bytes

    last_lap_time_ms: int = 0             # uint32 [cite: 8230]
    current_lap_time_ms: int = 0          # uint32 [cite: 8231]
    sector1_time_ms: int = 0              # uint16 [cite: 8232]
    sector1_time_minutes: int = 0         # uint8 [cite: 8233]
    sector2_time_ms: int = 0              # uint16 [cite: 8234]
    sector2_time_minutes: int = 0         # uint8 [cite: 8235]
    delta_to_car_in_front_ms: int = 0     # uint16 [cite: 8236]
    delta_to_car_in_front_minutes: int = 0 # uint8 [cite: 8237]
    delta_to_race_leader_ms: int = 0      # uint16 [cite: 8238]
    delta_to_race_leader_minutes: int = 0  # uint8 [cite: 8239]
    lap_distance: float = 0.0             # float [cite: 8240]
    total_distance: float = 0.0           # float [cite: 8241]
    safety_car_delta: float = 0.0         # float [cite: 8242]
    car_position: int = 0                 # uint8 [cite: 8243]
    current_lap_num: int = 0              # uint8 [cite: 8244]
    pit_status: int = 0                   # uint8 [cite: 8245]
    num_pit_stops: int = 0                # uint8 [cite: 8246]
    sector: int = 0                       # uint8 [cite: 8247]
    current_lap_invalid: int = 0          # uint8 [cite: 8248]
    penalties: int = 0                    # uint8 [cite: 8249]
    total_warnings: int = 0               # uint8 [cite: 8250]
    corner_cutting_warnings: int = 0      # uint8 [cite: 8251]
    num_unserved_drive_through_pens: int = 0 # uint8 [cite: 8252]
    num_unserved_stop_go_pens: int = 0    # uint8 [cite: 8253]
    grid_position: int = 0                # uint8 [cite: 8254]
    driver_status: int = 0                # uint8 [cite: 8255]
    result_status: int = 0                # uint8 [cite: 8256]
    pit_lane_timer_active: int = 0        # uint8 [cite: 8257]
    pit_lane_time_in_lane_ms: int = 0     # uint16 [cite: 8258]
    pit_stop_timer_ms: int = 0            # uint16 [cite: 8259]
    pit_stop_should_serve_pen: int = 0    # uint8 [cite: 8260]
    speed_trap_fastest_speed: float = 0.0 # float [cite: 8261]
    speed_trap_fastest_lap: int = 0       # uint8 [cite: 8262]

    # Aantal velden: 33

    @staticmethod
    def from_bytes(data: bytes) -> 'LapData':
        """
        Unpackt bytes (57) naar een LapData object.
        """
        if len(data) < LapData.PACKET_LEN:
            # Deze warning verwachten we niet meer, tenzij de data echt korter is
            lap_parser_logger.warning(f"LapData.from_bytes data te kort. Expected {LapData.PACKET_LEN}, got {len(data)}")
            return LapData()

        try:
            # Unpack de 57 bytes in één keer
            unpacked_data = struct.unpack(LapData.STRUCT_FORMAT, data[:LapData.PACKET_LEN])

            # Maak het LapData object aan
            return LapData(*unpacked_data)

        except struct.error as e:
            lap_parser_logger.error(f"LapData unpack failed (Struct-based, 57-byte): {e}. Data len: {len(data)}")
            return LapData()
        except Exception as e:
            lap_parser_logger.error(f"Onverwachte fout in LapData.from_bytes: {e}")
            return LapData()

@dataclass
class LapDataPacket(BaseParser):
    """
    Dataclass voor Packet 2.
    [cite: 8263-8267]
    """
    header: PacketHeader
    lap_data: List[LapData]
    time_trial_pb_car_idx: Optional[int] = None   # [cite: 8266]
    time_trial_rival_car_idx: Optional[int] = None # [cite: 8267]

    def __init__(self, header: PacketHeader, data: bytes):
        self.header = header

        # De totale payload (data) MOET 1256 bytes zijn.
        # 1254 bytes (22 * 57) + 2 bytes (PB/Rival)
        self.lap_data = []
        self.time_trial_pb_car_idx = None
        self.time_trial_rival_car_idx = None

        if not self.validate_payload_size(data):
            return

        self.parse(data)

    def validate_payload_size(self, data: bytes) -> bool:
        """Controleert de payload size (1256 bytes)."""

        # 1256 bytes = (22 * 57 bytes) + 1 byte + 1 byte
        total_expected_payload = (LapData.PACKET_LEN * 22) + 2

        if len(data) != total_expected_payload:
            lap_parser_logger.warning(
                f"LapDataPacket payload size incorrect. Expected {total_expected_payload} (1256), Got {len(data)}"
            )
            return False
        return True

    def parse(self, data: bytes):
        """Parse de volledige 1256-byte payload."""

        # 1. Parse de 22 auto's (1254 bytes)
        for i in range(22):
            start = i * LapData.PACKET_LEN # Stride is nu 57
            end = start + LapData.PACKET_LEN

            # We hoeven end niet te checken, want validate_payload_size()
            # heeft al gegarandeerd dat data lang genoeg is.
            car_data_bytes = data[start:end]
            self.lap_data.append(LapData.from_bytes(car_data_bytes))

        # 2. Parse de laatste 2 bytes
        try:
            pb_rival_offset = LapData.PACKET_LEN * 22 # 1254
            self.time_trial_pb_car_idx = struct.unpack_from('<B', data, pb_rival_offset)[0]
            self.time_trial_rival_car_idx = struct.unpack_from('<B', data, pb_rival_offset + 1)[0]
        except struct.error as e:
            lap_parser_logger.error(f"Fout bij parsen van PB/Rival index: {e}")
        except Exception as e:
            lap_parser_logger.error(f"Onverwachte fout bij PB/Rival parse: {e}")


class LapDataParser:
    """
    Parser voor Lap Data Packet (Packet 2).
    """
    def parse(self, header: PacketHeader, data: bytes) -> LapDataPacket:
        """Parse het pakket en retourneer een LapDataPacket object."""
        return LapDataPacket(header, data)