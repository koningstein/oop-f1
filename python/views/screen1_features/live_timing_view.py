"""
F1 25 Telemetry System - View voor Scherm 1.5: Live Timing
(Versie 8: Correcte lapnummer weergave)
"""
import os
from controllers import TelemetryController
from utils.time_formatter import ms_to_time_string
from services import logger_service
from views.components import DataTable

try:
    from packet_parsers.lap_parser import LapData
except ImportError:
    print("[Waarschuwing] Kon LapData structuur niet importeren. Scherm 1.5 zal falen.")
    class LapData: pass

LAP_VALID = 0b00000001
SECTOR_1_VALID = 0b00000010
SECTOR_2_VALID = 0b00000100

class LiveTimingView:
    def __init__(self, telemetry_controller: TelemetryController):
        self.controller = telemetry_controller
        self.logger = logger_service.get_logger('LiveTimingView')
        self.data_table = DataTable()
        self.VALID_ICON = "✅"
        self.INVALID_ICON = "❌"

    def _get_validation_icon(self, flags: int, bit_flag: int) -> str:
        is_invalid = (flags & bit_flag) > 0
        return self.INVALID_ICON if is_invalid else self.VALID_ICON

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def render(self):
        self.clear_screen()

        # --- Deel 1: Toon de LIVE Huidige Ronde Tijd ---
        live_data = self.controller.get_player_lap_data()
        current_time_str = "00:00.000"
        if live_data:
            current_time_str = ms_to_time_string(live_data.current_lap_time_ms)

        print("  LIVE SECTOR & LAP TIJDEN (Speler)")
        print("  " + "-"*40)
        print(f"  HUIDIGE RONDE: {current_time_str}")
        print("  " + "-"*40)

        # --- Deel 2: Haal de VOLTOOIDE RONDE HISTORIE op ---
        completed_laps = self.controller.get_completed_laps()

        if not completed_laps:
            print("\n  Wachten op voltooide ronden...")
            print("  Data verschijnt hier zodra je de eerste ronde hebt voltooid.")
            return

        # --- Deel 3: Bouw en render de historie tabel ---
        headers = ["Ronde", "Sector 1", "Sector 2", "Sector 3", "S1 + S2", "Totaal", "Valid"]
        rows = []

        for lap_data in completed_laps:
            # --- GECORRIGEERDE LOGICA ---
            # De data die we opslaan is de *voltooide* ronde.
            # lap_data.current_lap_num is dus het correcte, voltooide rondenummer.
            lap_num = lap_data.current_lap_num
            # --- EINDE CORRECTIE ---

            s1_ms = lap_data.sector1_time_ms
            s2_ms = lap_data.sector2_time_ms
            total_ms = lap_data.last_lap_time_ms

            # Bereken S3
            s3_ms = 0
            if total_ms > 0 and s1_ms > 0 and s2_ms > 0:
                s3_ms = total_ms - s1_ms - s2_ms

            # Bereken Cumulatief
            s1_s2_ms = 0
            if s1_ms > 0 and s2_ms > 0:
                s1_s2_ms = s1_ms + s2_ms

            flags = lap_data.current_lap_invalid
            is_lap_valid = self._get_validation_icon(flags, LAP_VALID)

            row = [
                f"{lap_num}",
                f"{ms_to_time_string(s1_ms)} {self._get_validation_icon(flags, SECTOR_1_VALID)}",
                f"{ms_to_time_string(s2_ms)} {self._get_validation_icon(flags, SECTOR_2_VALID)}",
                f"{ms_to_time_string(s3_ms)}",
                f"{ms_to_time_string(s1_s2_ms)}",
                f"{ms_to_time_string(total_ms)}",
                f"{is_lap_valid}"
            ]
            rows.append(row)

        print("\n  RONDETIJD HISTORIE:")
        self.data_table.render_table(headers, rows)