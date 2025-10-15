"""
F1 25 Telemetry - Menu System (menu.py)

BELANGRIJK: 
- Sla dit bestand op als: menu.py
- Zorg dat de screens/ map bestaat met alle screen modules

Bestandsstructuur:
python/
├── menu.py                    ← DIT BESTAND (nieuw)
├── main.py                    ← Blijft bestaan
├── screens/                   ← Screen modules
│   ├── __init__.py
│   ├── screen1.py
│   ├── screen2.py
│   ├── screen3.py
│   ├── screen4.py
│   ├── screen5.py
│   └── screen6.py
├── telemetry_listener.py
└── ... (andere packet bestanden)

Gebruik: python menu.py
"""

import os
import sys
import threading
import time

# Import alle screen modules
from screens import screen1, screen2, screen3, screen4, screen5, screen6


# ==================== GLOBAL LISTENER MANAGEMENT ====================

# Global variabele om de actieve listener bij te houden
_active_listener = None
_listener_lock = threading.Lock()

def get_active_listener():
    """Geef de actieve listener terug"""
    global _active_listener
    return _active_listener

def set_active_listener(listener):
    """Sla de actieve listener op"""
    global _active_listener
    with _listener_lock:
        _active_listener = listener

def stop_active_listener():
    """Stop de actieve listener als die er is"""
    global _active_listener
    
    with _listener_lock:
        if _active_listener is not None:
            try:
                _active_listener.running = False
                if hasattr(_active_listener, 'sock') and _active_listener.sock:
                    _active_listener.sock.close()
            except Exception:
                pass  # Negeer alle errors tijdens cleanup
            finally:
                _active_listener = None

# Maak de functies beschikbaar voor screen modules
screen1.set_active_listener = set_active_listener
screen1.get_active_listener = get_active_listener
screen2.set_active_listener = set_active_listener
screen2.get_active_listener = get_active_listener
screen3.set_active_listener = set_active_listener
screen3.get_active_listener = get_active_listener
screen4.set_active_listener = set_active_listener
screen4.get_active_listener = get_active_listener
screen5.set_active_listener = set_active_listener
screen5.get_active_listener = get_active_listener
screen6.set_active_listener = set_active_listener
screen6.get_active_listener = get_active_listener


# ==================== UTILITY FUNCTIES ====================

def clear_screen():
    """Maak het scherm leeg"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_header(title):
    """Toon een mooie header"""
    print("\n" + "=" * 80)
    print(f"🏎️  F1 25 TELEMETRY - {title.upper()}")
    print("=" * 80)

def pause():
    """Wacht op enter"""
    input("\n📌 Druk op ENTER om terug te gaan naar het menu...")

def run_listener_function(func):
    """
    Wrapper om listener functies te runnen in een thread die je kunt stoppen
    """
    clear_screen()
    print("\n" + "=" * 80)
    print("🎮 Functie actief - Druk op ENTER om te stoppen en terug te gaan")
    print("=" * 80)
    print()
    
    # Stop eventuele oude listener eerst - BELANGRIJK!
    stop_active_listener()
    time.sleep(0.3)  # Geef OS tijd om socket vrij te geven
    
    # Start listener in een aparte thread
    listener_thread = threading.Thread(target=func, daemon=True)
    listener_thread.start()
    
    # Wacht op ENTER in de main thread
    try:
        input()  # Wacht tot gebruiker op ENTER drukt
    except KeyboardInterrupt:
        pass
    
    # Stop de listener netjes
    stop_active_listener()
    time.sleep(0.3)  # Geef OS tijd om socket vrij te geven
    
    print("\n⏹️  Gestopt - Terug naar menu...")
    time.sleep(0.3)


# ==================== SCHERM 1: OVERZICHT / LEADERBOARD / TOERNOOI ====================

def scherm1_submenu():
    """Submenu voor Scherm 1"""
    while True:
        clear_screen()
        show_header("Scherm 1: Overzicht / Leaderboard / Toernooi")
        print("\n1. Toon alle data (volledig scherm)")
        print("2. Practice Mode - Leaderboard rondetijden")
        print("3. Practice Mode - Consistentie analyse")
        print("4. Race Mode - Live klassement")
        print("5. Race Mode - Delta's tussen rijders")
        print("6. Toernooi - Kampioenschapsstand")
        print("7. Toernooi - Race historie")
        print("8. Toernooi - Punten systeem")
        print("9. Position Chart - Positieverloop per ronde")
        print("\n0. Terug naar hoofdmenu")
        print("=" * 80)
        
        choice = input("\n➤ Keuze: ").strip()
        
        if choice == "1":
            run_listener_function(screen1.toon_alle_data)
        elif choice == "2":
            run_listener_function(screen1.practice_leaderboard)
        elif choice == "3":
            run_listener_function(screen1.practice_consistency)
        elif choice == "4":
            run_listener_function(screen1.race_live_klassement)
        elif choice == "5":
            run_listener_function(screen1.race_deltas)
        elif choice == "6":
            screen1.toernooi_stand()
            pause()
        elif choice == "7":
            screen1.toernooi_historie()
            pause()
        elif choice == "8":
            screen1.toernooi_punten()
            pause()
        elif choice == "9":
            screen1.position_chart()
            pause()
        elif choice == "0":
            break
        else:
            print("\n❌ Ongeldige keuze!")
            pause()


# ==================== SCHERM 2: INVOERSCHERM + TOERNOOI BEHEER ====================

def scherm2_submenu():
    """Submenu voor Scherm 2"""
    while True:
        clear_screen()
        show_header("Scherm 2: Invoerscherm + Toernooi Beheer")
        print("\n1. Toon alle data (volledig scherm)")
        print("2. Student registratie - Naam invoeren")
        print("3. Simulator selectie - Auto 1 of Auto 2")
        print("4. Sessie beheer - Start/Stop knoppen")
        print("5. Toernooi setup - Race toevoegen")
        print("6. Toernooi setup - Circuit selectie")
        print("7. Toernooi setup - Deelnemers beheer")
        print("8. Toernooi setup - Punten systeem configuratie")
        print("\n0. Terug naar hoofdmenu")
        print("=" * 80)
        
        choice = input("\n➤ Keuze: ").strip()
        
        if choice == "1":
            run_listener_function(screen2.toon_alle_data)
        elif choice == "2":
            screen2.student_registratie()
        elif choice == "3":
            screen2.simulator_selectie()
        elif choice == "4":
            run_listener_function(screen2.sessie_beheer)
        elif choice == "5":
            screen2.toernooi_race_toevoegen()
        elif choice == "6":
            screen2.toernooi_circuit_selectie()
        elif choice == "7":
            screen2.toernooi_deelnemers()
        elif choice == "8":
            screen2.toernooi_punten_configuratie()
        elif choice == "0":
            break
        else:
            print("\n❌ Ongeldige keuze!")
            pause()


# ==================== SCHERM 3: REALTIME DATA AUTO 1 ====================

def scherm3_submenu():
    """Submenu voor Scherm 3"""
    while True:
        clear_screen()
        show_header("Scherm 3: Realtime Data Auto 1")
        print("\n1. Toon alle data (volledig scherm)")
        print("2. Dashboard - Live telemetrie")
        print("3. Fuel & ERS Management")
        print("4. Damage Monitoring - Visuele schade weergave")
        print("5. Setup Tab - Setup data")
        print("6. Tyre Management - Band sets overzicht")
        print("7. Advanced Telemetry - Wielspecifieke data")
        print("\n0. Terug naar hoofdmenu")
        print("=" * 80)
        
        choice = input("\n➤ Keuze: ").strip()
        
        if choice == "1":
            run_listener_function(screen3.toon_alle_data)
        elif choice == "2":
            run_listener_function(screen3.dashboard_live_telemetrie)
        elif choice == "3":
            run_listener_function(screen3.fuel_ers_management)
        elif choice == "4":
            run_listener_function(screen3.damage_monitoring)
        elif choice == "5":
            run_listener_function(screen3.setup_tab)
        elif choice == "6":
            screen3.tyre_management()
            pause()
        elif choice == "7":
            screen3.advanced_telemetry()
            pause()
        elif choice == "0":
            break
        else:
            print("\n❌ Ongeldige keuze!")
            pause()


# ==================== SCHERM 4: REALTIME DATA AUTO 2 ====================

def scherm4_submenu():
    """Submenu voor Scherm 4"""
    while True:
        clear_screen()
        show_header("Scherm 4: Realtime Data Auto 2")
        print("\n1. Toon alle data (volledig scherm)")
        print("2. Dashboard - Live telemetrie")
        print("3. Fuel & ERS Management")
        print("4. Damage Monitoring - Visuele schade weergave")
        print("5. Setup Tab - Setup data")
        print("6. Tyre Management - Band sets overzicht")
        print("7. Advanced Telemetry - Wielspecifieke data")
        print("8. Vergelijk met Auto 1")
        print("\n0. Terug naar hoofdmenu")
        print("=" * 80)
        
        choice = input("\n➤ Keuze: ").strip()
        
        if choice == "1":
            run_listener_function(screen4.toon_alle_data)
        elif choice == "2":
            run_listener_function(screen4.dashboard_live_telemetrie)
        elif choice == "3":
            run_listener_function(screen4.fuel_ers_management)
        elif choice == "4":
            run_listener_function(screen4.damage_monitoring)
        elif choice == "5":
            run_listener_function(screen4.setup_tab)
        elif choice == "6":
            screen4.tyre_management()
            pause()
        elif choice == "7":
            screen4.advanced_telemetry()
            pause()
        elif choice == "8":
            run_listener_function(screen4.vergelijk_met_auto1)
        elif choice == "0":
            break
        else:
            print("\n❌ Ongeldige keuze!")
            pause()


# ==================== SCHERM 5: RACE STRATEGY & TYRE MANAGEMENT ====================

def scherm5_submenu():
    """Submenu voor Scherm 5"""
    while True:
        clear_screen()
        show_header("Scherm 5: Race Strategy & Tyre Management")
        print("\n1. Toon alle data (volledig scherm)")
        print("2. Lap Time Comparison - Side-by-side vergelijking")
        print("3. Lap Time Comparison - Delta's per sector")
        print("4. Lap Time Comparison - Consistency metrics")
        print("5. Lap Time Comparison - Setup analyse")
        print("6. Tyre Strategy - Band set overview")
        print("7. Tyre Strategy - Current tyre status")
        print("8. Tyre Strategy - Stint comparison")
        print("9. Tyre Strategy - Degradation curves")
        print("10. Position & Strategy - Position battle chart")
        print("11. Position & Strategy - Stint timeline")
        print("12. Position & Strategy - Optimal strategy")
        print("13. Position & Strategy - Fuel vs tyre strategy")
        print("\n0. Terug naar hoofdmenu")
        print("=" * 80)
        
        choice = input("\n➤ Keuze: ").strip()
        
        if choice == "1":
            run_listener_function(screen5.toon_alle_data)
        elif choice == "2":
            run_listener_function(screen5.lap_time_comparison)
        elif choice == "3":
            run_listener_function(screen5.lap_time_deltas)
        elif choice == "4":
            run_listener_function(screen5.consistency_metrics)
        elif choice == "5":
            screen5.setup_analyse()
            pause()
        elif choice == "6":
            screen5.tyre_set_overview()
            pause()
        elif choice == "7":
            run_listener_function(screen5.tyre_status)
        elif choice == "8":
            screen5.stint_comparison()
            pause()
        elif choice == "9":
            screen5.degradation_curves()
            pause()
        elif choice == "10":
            screen5.position_battle_chart()
            pause()
        elif choice == "11":
            screen5.stint_timeline()
            pause()
        elif choice == "12":
            screen5.optimal_strategy()
            pause()
        elif choice == "13":
            screen5.fuel_vs_tyre_strategy()
            pause()
        elif choice == "0":
            break
        else:
            print("\n❌ Ongeldige keuze!")
            pause()


# ==================== SCHERM 6: LIVE TRACK MAP + TELEMETRIE VERGELIJKING ====================

def scherm6_submenu():
    """Submenu voor Scherm 6"""
    while True:
        clear_screen()
        show_header("Scherm 6: Live Track Map + Telemetrie Vergelijking")
        print("\n1. Toon alle data (volledig scherm)")
        print("2. Circuit Layout - 2D track map")
        print("3. Live Telemetrie Overlay - Throttle/brake")
        print("4. Live Telemetrie Overlay - Speed comparison")
        print("5. Live Telemetrie Overlay - Steering input")
        print("6. Live Telemetrie Overlay - Gear indicator")
        print("7. Corner Analysis - Bocht aanpak visualisatie")
        print("8. Corner-by-corner vergelijking")
        print("9. Slip Analysis - Slip angles & grip levels")
        print("\n0. Terug naar hoofdmenu")
        print("=" * 80)
        
        choice = input("\n➤ Keuze: ").strip()
        
        if choice == "1":
            run_listener_function(screen6.toon_alle_data)
        elif choice == "2":
            run_listener_function(screen6.circuit_layout)
        elif choice == "3":
            run_listener_function(screen6.throttle_brake_overlay)
        elif choice == "4":
            run_listener_function(screen6.speed_comparison)
        elif choice == "5":
            run_listener_function(screen6.steering_input)
        elif choice == "6":
            run_listener_function(screen6.gear_indicator)
        elif choice == "7":
            screen6.corner_analysis()
            pause()
        elif choice == "8":
            screen6.corner_by_corner()
            pause()
        elif choice == "9":
            screen6.slip_analysis()
            pause()
        elif choice == "0":
            break
        else:
            print("\n❌ Ongeldige keuze!")
            pause()


# ==================== HOOFDMENU ====================

def hoofdmenu():
    """Hoofdmenu voor scherm selectie"""
    while True:
        clear_screen()
        show_header("Hoofdmenu")
        print("\nSelecteer een scherm om te testen:\n")
        print("  1. Scherm 1: Overzicht / Leaderboard / Toernooi")
        print("  2. Scherm 2: Invoerscherm + Toernooi Beheer")
        print("  3. Scherm 3: Realtime Data Auto 1")
        print("  4. Scherm 4: Realtime Data Auto 2")
        print("  5. Scherm 5: Race Strategy & Tyre Management")
        print("  6. Scherm 6: Live Track Map + Telemetrie Vergelijking")
        print("\n  0. Afsluiten")
        print("=" * 80)
        
        choice = input("\n➤ Keuze: ").strip()
        
        if choice == "1":
            scherm1_submenu()
        elif choice == "2":
            scherm2_submenu()
        elif choice == "3":
            scherm3_submenu()
        elif choice == "4":
            scherm4_submenu()
        elif choice == "5":
            scherm5_submenu()
        elif choice == "6":
            scherm6_submenu()
        elif choice == "0":
            clear_screen()
            print("\n" + "=" * 80)
            print("👋 Tot ziens!")
            print("=" * 80 + "\n")
            sys.exit(0)
        else:
            print("\n❌ Ongeldige keuze!")
            pause()


# ==================== START PROGRAMMA ====================

if __name__ == "__main__":
    print("\n⚠️  BELANGRIJK:")
    print("   1. Start F1 25")
    print("   2. Ga naar Instellingen > UDP Telemetry Settings")
    print("   3. Zet 'UDP Telemetry' op 'Enabled'")
    print("   4. IP: 127.0.0.1, Port: 20777")
    print("   5. Format: 2025")
    print()
    input("Druk op ENTER om door te gaan...")
    
    try:
        hoofdmenu()
    except KeyboardInterrupt:
        clear_screen()
        print("\n" + "=" * 80)
        print("👋 Programma gestopt door gebruiker")
        print("=" * 80 + "\n")
        sys.exit(0)