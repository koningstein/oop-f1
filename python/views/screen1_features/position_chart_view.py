"""
F1 25 Telemetry System - View voor Scherm 1.4: Position Chart
Toont ASCII lap chart uit Packet 15. (Niet-live)
"""
import os
from controllers import TelemetryController
from views.components import Header


class PositionChartView:
    def __init__(self, telemetry_controller: TelemetryController):
        self.controller = telemetry_controller
        self.header = Header()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def render(self):
        self.clear_screen()
        self.header.render_box_header("POSITION CHART (PER RONDE)")

        # Haal P15 data en P4 namen op
        position_data, participant_names = self.controller.get_position_chart_data()

        if not position_data or not participant_names:
            print("\n  Wachten op data (Packet 4 & 15)...")
            print("  Dit pakket wordt vaak pas na de race of sessie gestuurd.")
            return

        num_laps_to_show = position_data.num_laps
        if num_laps_to_show == 0:
            print("\n  Nog geen rondes voltooid.")
            return

        # Maak de header (Ronde 1, Ronde 2, ...)
        header = "Driver".ljust(5) + " | "
        for i in range(num_laps_to_show):
            header += f"R{i + 1}".ljust(3) + " | "
        print(header)
        print("-" * len(header))

        # Print de data per auto
        # We tonen alleen autos die een naam hebben
        for i in range(len(participant_names)):
            name_short = participant_names[i][:3].upper()
            line = name_short.ljust(5) + " | "
            for lap in range(num_laps_to_show):
                # De positie (1-based)
                pos = position_data.positions[lap][i]
                if pos == 0:
                    line += " - ".ljust(3) + " | "
                else:
                    line += f"P{pos}".ljust(3) + " | "
            print(line)