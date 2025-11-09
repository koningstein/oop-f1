"""
F1 25 Telemetry System - View voor Scherm 1.1: Practice Mode
(Versie 2: GECORRIGEERDE import)
"""
import os
from controllers import TelemetryController
from views.components import Header, DataTable

# --- CORRECTIE HIER ---
from utils.time_formatter import ms_to_time_string
# --- EINDE CORRECTIE ---

class PracticeView:
    def __init__(self, telemetry_controller: TelemetryController):
        self.controller = telemetry_controller
        self.header = Header()
        self.data_table = DataTable()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def render(self):
        self.clear_screen()
        self.header.render_box_header("PRACTICE MODE - BEST LAP LEADERBOARD")

        timing_data = self.controller.get_combined_timing_data()

        if not timing_data:
            print("\n  Wachten op data (Packet 2 & 4)...")
            return

        sorted_data = sorted(
            [d for d in timing_data if d['best_lap_time_ms'] > 0],
            key=lambda x: x['best_lap_time_ms']
        )

        headers = ["Pos", "Driver", "Best Lap"]
        rows = []

        for idx, data in enumerate(sorted_data):
            pos = f"{idx + 1}."
            name = data['name']
            # --- CORRECTIE HIER ---
            best_lap = ms_to_time_string(data['best_lap_time_ms'])
            # --- EINDE CORRECTIE ---
            rows.append([pos, name, best_lap])

        if not rows:
            print("\n  Nog geen beste rondetijden gezet in deze sessie...")
        else:
            self.data_table.render_table(headers, rows)