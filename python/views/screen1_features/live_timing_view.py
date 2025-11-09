"""
F1 25 Telemetry System - View voor Scherm 1.5: Live Timing
(Versie 4: GECORRIGEERDE import)
"""
import os
from controllers import TelemetryController
from services import logger_service

# --- CORRECTIE HIER ---
from utils.time_formatter import ms_to_time_string # Gebruik de juiste naam
# --- EINDE CORRECTIE ---

try:
    from packet_parsers.lap_parser import LapData
except ImportError:
    print("[Waarschuwing] Kon LapData structuur niet importeren. Scherm 1.5 zal falen.")
    class LapData: pass

# Validatie bits
LAP_VALID = 0b00000001
SECTOR_1_VALID = 0b00000010
SECTOR_2_VALID = 0b00000100

class LiveTimingView:
    def __init__(self, telemetry_controller: TelemetryController):
        self.controller = telemetry_controller
        self.logger = logger_service.get_logger('LiveTimingView')
        self.VALID_ICON = "✅"
        self.INVALID_ICON = "❌"

    def _get_validation_icon(self, flags: int, bit_flag: int) -> str:
        is_invalid = (flags & bit_flag) > 0
        return self.INVALID_ICON if is_invalid else self.VALID_ICON

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def render(self):
        self.clear_screen()
        player_lap_data = self.controller.get_player_lap_data()

        if not player_lap_data or player_lap_data.last_lap_time_ms == 0:
            print("\n  Wachten op F1 25 Lap Data (Packet 2)...")
            return

        try:
            s1_time = player_lap_data.sector1_time_ms
            s2_time = player_lap_data.sector2_time_ms
            lap_time = player_lap_data.last_lap_time_ms
            current_time = player_lap_data.current_lap_time_ms
            flags = player_lap_data.current_lap_invalid

        except AttributeError as e:
            self.logger.error(f"Data structuur (LapData) komt niet overeen: {e}")
            print(f"\n  [FOUT] Data structuur (LapData) komt niet overeen: {e}")
            return

        s1_s2_time = 0
        if s1_time > 0 and s2_time > 0:
            s1_s2_time = s1_time + s2_time

        lap_icon = self._get_validation_icon(flags, LAP_VALID)
        s1_icon = self._get_validation_icon(flags, SECTOR_1_VALID)
        s2_icon = self._get_validation_icon(flags, SECTOR_2_VALID)

        print("  LIVE SECTOR & LAP TIJDEN (Speler)")
        print("  " + "-"*40)
        # --- CORRECTIE HIER ---
        print(f"  HUIDIGE RONDE: {ms_to_time_string(current_time)}")
        print("  " + "-"*40)
        print(f"  Sector 1:    {ms_to_time_string(s1_time)} {s1_icon}")
        print(f"  Sector 2:    {ms_to_time_string(s2_time)} {s2_icon}")
        print(f"  S1 + S2:     {ms_to_time_string(s1_s2_time)}")
        print("  " + "-"*40)
        print(f"  Laatste Ronde: {ms_to_time_string(lap_time)} {lap_icon}")
        # --- EINDE CORRECTIE ---
        print("  " + "-"*40)