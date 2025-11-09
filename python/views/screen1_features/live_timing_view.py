"""
F1 25 Telemetry System - View voor Scherm 1.5: Live Timing
(Versie 9: Correcte validatie o.b.v. Packet 11 en Live S1/S2)
"""
import os
from controllers import TelemetryController
from utils.time_formatter import ms_to_time_string
from services import logger_service
from views.components import DataTable

# --- Importeer de DATATYPES van de PARSERS ---
try:
    # Voor Live Data (Packet 2)
    from packet_parsers.lap_parser import LapData
except ImportError:
    print("[Waarschuwing] Kon LapData (Packet 2) structuur niet importeren.")
    class LapData: pass

try:
    # Voor Historie Data (Packet 11) - CRUCIAAL VOOR VALIDATIE
    from packet_parsers.history_parser import SessionHistoryData, LapHistoryData
except ImportError:
    print("[Waarschuwing] Kon SessionHistoryData (Packet 11) structuur niet importeren.")
    class SessionHistoryData: pass
    class LapHistoryData: pass


# --- Validatie bits voor Packet 2 (Live Data) ---
# (Deze worden gebruikt voor de 'HUIDIGE RONDE' sectie)
LAP_VALID_P2 = 0b00000001
SECTOR_1_VALID_P2 = 0b00000010
SECTOR_2_VALID_P2 = 0b00000100
SECTOR_3_VALID_P2 = 0b00001000 # Aanname dat S3 ook in Packet 2 vlag zit

class LiveTimingView:
    def __init__(self, telemetry_controller: TelemetryController):
        self.controller = telemetry_controller
        self.logger = logger_service.get_logger('LiveTimingView')
        self.data_table = DataTable()
        self.VALID_ICON = "✅"
        self.INVALID_ICON = "❌"

    def _get_validation_icon(self, flags: int, bit_flag: int) -> str:
        """Helper: 0 = valid, 1 = invalid."""
        is_invalid = (flags & bit_flag) > 0
        return self.INVALID_ICON if is_invalid else self.VALID_ICON

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def _render_live_data(self):
        """Rendert het bovenste blok met live data van Packet 2."""
        live_data = self.controller.get_player_lap_data()

        current_time_str = "00:00.000"
        s1_str = "-:--.---"
        s2_str = "-:--.---"

        if live_data:
            flags = live_data.current_lap_invalid
            current_time_str = ms_to_time_string(live_data.current_lap_time_ms)

            # Toon S1 tijd zodra deze binnenkomt
            if live_data.sector1_time_ms > 0:
                s1_icon = self._get_validation_icon(flags, SECTOR_1_VALID_P2)
                s1_str = f"{ms_to_time_string(live_data.sector1_time_ms)} {s1_icon}"

            # Toon S2 tijd zodra deze binnenkomt
            if live_data.sector2_time_ms > 0:
                s2_icon = self._get_validation_icon(flags, SECTOR_2_VALID_P2)
                s2_str = f"{ms_to_time_string(live_data.sector2_time_ms)} {s2_icon}"

        print("  LIVE SECTOR & LAP TIJDEN (Speler - Packet 2)")
        print("  " + "-"*50)
        print(f"  HUIDIGE RONDE: {current_time_str}")
        print(f"  Sector 1:      {s1_str}")
        print(f"  Sector 2:      {s2_str}")
        print("  " + "-"*50)

    def _render_history_table(self):
        """Rendert de historie-tabel o.b.v. Packet 11 (Session History)."""

        # We gebruiken Packet 11 data voor de historisch correcte validatie
        history_data = self.controller.get_player_lap_history()

        if not history_data or not history_data.lap_history_data:
            print("\n  Wachten op voltooide ronden (Packet 11)...")
            return

        headers = ["Ronde", "Sector 1", "Sector 2", "Sector 3", "S1 + S2", "Totaal", "Lap Valid"]
        rows = []

        # We moeten de rondes zelf tellen, startend vanaf 1
        for i, lap in enumerate(history_data.lap_history_data):
            lap_num = i + 1

            # Gebruik de methods uit de (gecorrigeerde) history_parser
            s1_ms = lap.get_sector1_total_ms()
            s2_ms = lap.get_sector2_total_ms()
            s3_ms = lap.get_sector3_total_ms()
            total_ms = lap.lap_time_ms

            s1_s2_ms = 0
            if s1_ms > 0 and s2_ms > 0:
                s1_s2_ms = s1_ms + s2_ms

            # --- DIT IS DE GECORRIGEERDE VALIDATIE (O.B.V. PACKET 11) ---
            s1_icon = self.VALID_ICON if lap.is_sector1_valid() else self.INVALID_ICON
            s2_icon = self.VALID_ICON if lap.is_sector2_valid() else self.INVALID_ICON
            s3_icon = self.VALID_ICON if lap.is_sector3_valid() else self.INVALID_ICON
            lap_icon = self.VALID_ICON if lap.is_lap_valid() else self.INVALID_ICON
            # --- EINDE CORRECTIE ---

            row = [
                f"{lap_num}",
                f"{ms_to_time_string(s1_ms)} {s1_icon}",
                f"{ms_to_time_string(s2_ms)} {s2_icon}",
                f"{ms_to_time_string(s3_ms)} {s3_icon}", # S3 validatie toegevoegd
                f"{ms_to_time_string(s1_s2_ms)}",
                f"{ms_to_time_string(total_ms)}",
                f"{lap_icon}"
            ]
            rows.append(row)

        print("\n  RONDETIJD HISTORIE (Packet 11 - Validatie Bron)")
        self.data_table.render_table(headers, rows)

    def render(self):
        self.clear_screen()

        # Render de twee delen
        self._render_live_data()
        self._render_history_table()