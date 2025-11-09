"""
F1 25 Telemetry System - View voor Scherm 1.2: Race Mode
(Versie 2: GECORRIGEERDE import)
"""
import os
from controllers import TelemetryController
from views.components import Header, DataTable

# --- CORRECTIE HIER ---
from utils.time_formatter import ms_to_time_string
# --- EINDE CORRECTIE ---

class RaceView:
    def __init__(self, telemetry_controller: TelemetryController):
        self.controller = telemetry_controller
        self.header = Header()
        self.data_table = DataTable()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def render(self):
        self.clear_screen()
        self.header.render_box_header("RACE MODE - LIVE KLASSEMENT")

        timing_data = self.controller.get_combined_timing_data()

        if not timing_data:
            print("\n  Wachten op data (Packet 2 & 4)...")
            return

        headers = ["Pos", "Driver", "Last Lap", "Current Lap"]
        rows = []

        for data in timing_data:
            pos = f"P{data['position']}"
            name = data['name']
            # --- CORRECTIE HIER ---
            last_lap = ms_to_time_string(data['last_lap_time_ms'])
            current_lap = ms_to_time_string(data['current_lap_time_ms'])
            # --- EINDE CORRECTIE ---
            rows.append([pos, name, last_lap, current_lap])

        self.data_table.render_table(headers, rows)