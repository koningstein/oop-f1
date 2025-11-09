"""
F1 25 Telemetry System - View voor Scherm 1.3: Toernooi
Toont toernooi standen uit de database. (Niet-live)
"""
import os
from controllers import TelemetryController
from views.components import Header, DataTable


class TournamentView:
    def __init__(self, telemetry_controller: TelemetryController):
        self.controller = telemetry_controller
        self.header = Header()
        self.data_table = DataTable()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def render(self):
        self.clear_screen()
        self.header.render_box_header("TOERNOOI STAND (UIT DATABASE)")

        # Haal de data op (Controller -> Models -> Database)
        standings = self.controller.get_tournament_standings()

        if not standings:
            print("\n  Database is leeg of kon niet worden bereikt.")
            return

        # Haal headers dynamisch op uit de eerste entry
        headers = list(standings[0].keys())
        rows = [list(row.values()) for row in standings]

        self.data_table.render_table(headers, rows)