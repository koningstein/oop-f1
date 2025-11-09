"""
F1 25 Telemetry System - Position Parser (Packet 15)
(GECORRIGEERDE VERSIE)
"""
import struct
from dataclasses import dataclass, field
from typing import List

# --- Fout 1: Import fix (relatief) ---
from .packet_header import PacketHeader
# BaseParser is hier niet nodig, de parser-klasse gebruikt 'm niet direct

@dataclass
class LapPositionsData:
    """
    Dataclass voor de positie data.
    Bevat posities van alle 22 autos voor 50 ronden.
    """
    # --- Fout 2: Volgorde fix (geen default eerst) ---
    positions: List[List[int]]

    # Velden met default daarna
    num_laps: int = 0
    lap_start: int = 0

    @staticmethod
    def from_bytes(data: bytes) -> 'LapPositionsData':
        """Unpackt de positie data."""
        num_laps, lap_start = struct.unpack('<BB', data[:2])

        offset = 2
        max_laps = 50 # cs_maxNumLapsInLapPositionsHistoryPacket
        max_cars = 22 # cs_maxNumCarsInUDPData

        try:
            # Lees de volledige 50x22 byte array
            expected_len = max_laps * max_cars
            position_flat_list = struct.unpack('<' + ('B' * expected_len), data[offset:offset + expected_len])
        except struct.error as e:
            # Data is korter dan verwacht (komt voor bij P15)
            # Maak een lege grid
            positions_grid = [[0 for _ in range(max_cars)] for _ in range(max_laps)]
        else:
            # Herstructureer de flat list naar een geneste lijst
            positions_grid = []
            for i in range(max_laps):
                lap_pos = list(position_flat_list[i * max_cars : (i + 1) * max_cars])
                positions_grid.append(lap_pos)

        return LapPositionsData(
            positions=positions_grid, # Eerst
            num_laps=num_laps,        # Daarna
            lap_start=lap_start
        )

@dataclass
class LapPositionsPacket:
    """
    Dataclass voor Packet 15.
    --- Fout 3: Geen overerving van BaseParser ---
    Dit is een pure data container.
    """
    header: PacketHeader
    lap_positions: LapPositionsData
    # Geen __init__ of parse hier, dat doet de Parser klasse

class PositionParser:
    """
    Parser voor Lap Positions Packet (Packet 15).
    Deze klasse implementeert de 'parse'-methode die de DataProcessor verwacht.
    """
    def parse(self, header: PacketHeader, data: bytes) -> LapPositionsPacket:
        """
        Parse het pakket en retourneer een LapPositionsPacket object.
        --- Fout 3: Dit is nu de enige plek die parseert en instantieert ---
        """
        # 1. Parse de payload data naar een LapPositionsData object
        lap_positions_data = LapPositionsData.from_bytes(data)

        # 2. Creëer en retourneer het volledige LapPositionsPacket
        return LapPositionsPacket(
            header=header,
            lap_positions=lap_positions_data
        )