"""
F1 25 Telemetry - Session History Parser (Packet 11)
(Versie 2: Correcte validatie bit flags)
"""

from dataclasses import dataclass
from typing import Optional, List
from .base_parser import BaseParser
from .packet_header import PacketHeader
import struct # Nodig voor unpack

# Importeer de correcte logger
try:
    from services.logger_services import logger_service
except ImportError:
    import logging
    logger_service = logging.getLogger('HistoryParser')

history_parser_logger = logger_service.get_logger('HistoryParser')


@dataclass
class LapHistoryData:
    """
    Historische lap data met sector validatie.
    Validatie flags:
    0x01 = Lap Valid
    0x02 = Sector 1 Valid
    0x04 = Sector 2 Valid
    0x08 = Sector 3 Valid
    """
    lap_time_ms: int
    sector1_time_ms: int
    sector1_time_minutes: int
    sector2_time_ms: int
    sector2_time_minutes: int
    sector3_time_ms: int
    sector3_time_minutes: int
    lap_valid_bit_flags: int

    # --- GECORRIGEERDE VALIDATIE FUNCTIES ---

    def is_lap_valid(self) -> bool:
        """Check of lap valide is via bit flag 0x01 """
        return bool(self.lap_valid_bit_flags & 0x01)

    def is_sector1_valid(self) -> bool:
        """Check of sector 1 valide is via bit flag 0x02 """
        return bool(self.lap_valid_bit_flags & 0x02)

    def is_sector2_valid(self) -> bool:
        """Check of sector 2 valide is via bit flag 0x04 """
        return bool(self.lap_valid_bit_flags & 0x04)

    def is_sector3_valid(self) -> bool:
        """Check of sector 3 valide is via bit flag 0x08 """
        return bool(self.lap_valid_bit_flags & 0x08)

    # --- EINDE CORRECTIES ---

    def get_sector1_total_ms(self) -> int:
        """Totale sector 1 tijd in ms"""
        return (self.sector1_time_minutes * 60000) + self.sector1_time_ms

    def get_sector2_total_ms(self) -> int:
        """Totale sector 2 tijd in ms"""
        return (self.sector2_time_minutes * 60000) + self.sector2_time_ms

    def get_sector3_total_ms(self) -> int:
        """Totale sector 3 tijd in ms"""
        return (self.sector3_time_minutes * 60000) + self.sector3_time_ms

@dataclass
class TyreStintHistoryData:
    """Tyre stint history"""
    end_lap: int
    tyre_actual_compound: int
    tyre_visual_compound: int

@dataclass
class SessionHistoryData:
    """Complete session history voor één auto"""
    header: PacketHeader
    car_idx: int
    num_laps: int
    num_tyre_stints: int
    best_lap_time_lap_num: int
    best_sector1_lap_num: int
    best_sector2_lap_num: int
    best_sector3_lap_num: int
    lap_history_data: List[LapHistoryData]
    tyre_stints_history_data: List[TyreStintHistoryData]

class SessionHistoryParser(BaseParser):
    """Parser voor Session History packets (ID 11)"""

    # Format voor één LapHistoryData (14 bytes) [cite: 4455-4462]
    LAP_HISTORY_FORMAT = "<IHBHBHBB"
    LAP_HISTORY_SIZE = struct.calcsize(LAP_HISTORY_FORMAT) # 14 bytes

    # Format voor één TyreStintHistoryData (3 bytes) [cite: 4464-4466]
    TYRE_STINT_FORMAT = "<BBB"
    TYRE_STINT_SIZE = struct.calcsize(TYRE_STINT_FORMAT) # 3 bytes

    # Totale grootte [cite: 4467-4475]
    # Header (7) + Laps (100 * 14) + Stints (8 * 3) = 7 + 1400 + 24 = 1431 bytes
    TOTAL_PAYLOAD_SIZE = 1431

    def __init__(self):
        """Initialiseer de logger voor deze parser."""
        self.logger = history_parser_logger

    def parse(self, header: PacketHeader, payload: bytes) -> Optional[SessionHistoryData]:
        """
        Parse session history packet
        """
        # Gebruik de totale payload size voor validatie
        if len(payload) != self.TOTAL_PAYLOAD_SIZE:
             self.logger.warning(
                 f"HistoryParser payload size incorrect. Expected {self.TOTAL_PAYLOAD_SIZE}, Got {len(payload)}"
             )
             return None

        try:
            # Parse header info (7 bytes) [cite: 4468-4474]
            offset = 0
            header_data = struct.unpack_from("<BBBBBBB", payload, offset)
            offset += 7

            car_idx, num_laps, num_tyre_stints, best_lap_time_lap_num, \
            best_sector1_lap_num, best_sector2_lap_num, best_sector3_lap_num = header_data

            # Valideer car index (0-21)
            if not (0 <= car_idx <= 21):
                self.logger.warning(f"Ongeldige car_idx: {car_idx}")
                return None

            # Parse lap history (altijd 100 slots lezen) [cite: 4475]
            lap_history = []
            for lap_num in range(100):
                lap_data = struct.unpack_from(self.LAP_HISTORY_FORMAT, payload, offset)
                offset += self.LAP_HISTORY_SIZE

                # Voeg alleen toe als het binnen de gerapporteerde num_laps valt
                if lap_num < num_laps:
                    lap_history.append(LapHistoryData(*lap_data))

            # Parse tyre stints (altijd 8 slots lezen) [cite: 4475]
            tyre_stints = []
            for stint_num in range(8):
                stint_data = struct.unpack_from(self.TYRE_STINT_FORMAT, payload, offset)
                offset += self.TYRE_STINT_SIZE

                if stint_num < num_tyre_stints:
                    tyre_stints.append(TyreStintHistoryData(*stint_data))

            return SessionHistoryData(
                header=header,
                car_idx=car_idx,
                num_laps=num_laps,
                num_tyre_stints=num_tyre_stints,
                best_lap_time_lap_num=best_lap_time_lap_num,
                best_sector1_lap_num=best_sector1_lap_num,
                best_sector2_lap_num=best_sector2_lap_num,
                best_sector3_lap_num=best_sector3_lap_num,
                lap_history_data=lap_history,
                tyre_stints_history_data=tyre_stints
            )

        except struct.error as e:
            self.logger.error(f"Session history unpack fout: {e}. Offset: {offset}")
            return None
        except Exception as e:
            self.logger.error(f"Onverwachte session history parse fout: {e}")
            return None