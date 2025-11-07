"""
F1 25 Telemetry System - View voor Scherm 1.5: Live Timing
Toont live ronde- en sectortijden met validatie.
"""
from controllers import TelemetryController

# --- GECORRIGEERDE IMPORT ---
# Importeer de 'LapData' dataclass
try:
    # Aanname: je 'oud2/lap_packets.py' heet nu 'packet_parsers/lap_parser.py'
    from packet_parsers.lap_parser import LapData
except ImportError:
    print("[Waarschuwing] Kon LapData structuur niet importeren. Scherm 1.5 zal falen.")
    class LapData: pass

# Validatie bits (0 = valid, 1 = invalid)
# Deze komen uit de F1 25 spec voor 'm_currentLapInvalid'
LAP_VALID = 0b00000001
SECTOR_1_VALID = 0b00000010
SECTOR_2_VALID = 0b00000100
SECTOR_3_VALID = 0b00001000

class LiveTimingView:
    """
    Rendert de live timing data voor Scherm 1.5.
    """
    
    def __init__(self, telemetry_controller: TelemetryController):
        self.controller = telemetry_controller
        self.VALID_ICON = "✅"
        self.INVALID_ICON = "❌"

    def _format_time_ms(self, time_ms: int) -> str:
        """Helper: Converteer milliseconden naar M:SS.mmm formaat."""
        if time_ms == 0:
            return "-:--.---"
        
        minutes = time_ms // 60000
        seconds = (time_ms % 60000) // 1000
        milliseconds = time_ms % 1000
        return f"{minutes}:{seconds:02d}.{milliseconds:03d}"

    def _get_validation_icon(self, flags: int, bit_flag: int) -> str:
        """
        Helper: Check een specifieke validatie bit flag.
        De F1 25 spec zegt: 0 = valid, 1 = invalid.
        """
        is_invalid = (flags & bit_flag) > 0
        return self.INVALID_ICON if is_invalid else self.VALID_ICON

    def render(self):
        """
        Render de live timing data.
        """
        
        # Haal de data op bij de controller (is thread-safe)
        player_lap_data = self.controller.get_player_lap_data()
        
        if not player_lap_data:
            print("\n  Wachten op F1 25 Lap Data (Packet 2)...")
            print("  Zorg dat je een ronde rijdt in de game.")
            return

        try:
            # --- Attribuutnamen gebaseerd op 'oud2/lap_packets.py' ---
            s1_time = player_lap_data.sector1_time_ms
            s2_time = player_lap_data.sector2_time_ms
            lap_time = player_lap_data.last_lap_time_ms
            flags = player_lap_data.current_lap_invalid
            
        except AttributeError as e:
            print(f"\n  [FOUT] Data structuur (LapData) komt niet overeen: {e}")
            print("  Controleer de attributen in 'lap_parser.py'.")
            return
        except Exception as e:
            print(f"\n  [FOUT] Onverwachte datafout: {e}")
            return
            
        # Bereken cumulatieve tijd
        s1_s2_time = 0
        if s1_time > 0 and s2_time > 0:
            s1_s2_time = s1_time + s2_time

        # Check de bits van 'current_lap_invalid'
        lap_icon = self._get_validation_icon(flags, LAP_VALID)
        s1_icon = self._get_validation_icon(flags, SECTOR_1_VALID)
        s2_icon = self._get_validation_icon(flags, SECTOR_2_VALID)

        # Print de data
        print("  LIVE SECTOR & LAP TIJDEN (Speler)")
        print("  " + "-"*40)
        print(f"  Sector 1:    {self._format_time_ms(s1_time)} {s1_icon}")
        print(f"  Sector 2:    {self._format_time_ms(s2_time)} {s2_icon}")
        print(f"  S1 + S2:     {self._format_time_ms(s1_s2_time)}")
        print("  " + "-"*40)
        print(f"  Laatste Ronde: {self._format_time_ms(lap_time)} {lap_icon}")
        print("  " + "-"*40)