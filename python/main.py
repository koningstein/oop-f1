"""
F1 25 Telemetry - Main Example
Voorbeelden van hoe je de telemetry listener gebruikt
"""

from telemetry_listener import F1TelemetryListener, create_simple_listener
from packet_types import PacketID

# Import packet types die we willen gebruiken
from motion_packets import MotionPacket, MotionExPacket
from session_packets import SessionPacket, EventPacket
from lap_packets import LapDataPacket, LapPositionsPacket
from car_packets import CarTelemetryPacket, CarStatusPacket, CarDamagePacket
from participants_packets import ParticipantsPacket, LobbyInfoPacket
from other_packets import FinalClassificationPacket


# ===== VOORBEELD 1: BASIS TELEMETRIE =====
def example_basic_telemetry():
    """
    Simpel voorbeeld: Toon snelheid, versnelling, RPM
    """
    print("\n📋 VOORBEELD 1: Basis Telemetrie")
    print("=" * 60)
    
    def handle_telemetry(packet: CarTelemetryPacket):
        player = packet.get_player_telemetry()
        
        # Print telemetrie op 1 regel (overschrijft vorige regel)
        print(f"\r🏎️  Speed: {player.speed:3d} km/h | "
              f"Gear: {player.gear:2d} | "
              f"RPM: {player.engine_rpm:5d} | "
              f"Throttle: {player.throttle:5.1%} | "
              f"Brake: {player.brake:5.1%}", end='', flush=True)
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.CAR_TELEMETRY, handle_telemetry)
    listener.start()


# ===== VOORBEELD 2: SESSIE INFORMATIE =====
def example_session_info():
    """
    Toon sessie informatie en lap data
    """
    print("\n📋 VOORBEELD 2: Sessie Informatie")
    print("=" * 60)
    
    def handle_session(packet: SessionPacket):
        print(f"\n📍 Sessie: {packet.get_session_type_name()}")
        print(f"   Circuit: {packet.get_track_name()}")
        print(f"   Weer: {packet.get_weather_name()}")
        print(f"   Track temp: {packet.track_temperature}°C")
        print(f"   Air temp: {packet.air_temperature}°C")
        print(f"   Totaal rondes: {packet.total_laps}")
        print(f"   Tijd over: {packet.session_time_left}s")
    
    def handle_lap_data(packet: LapDataPacket):
        player = packet.get_player_lap_data()
        
        print(f"\r🏁 Lap {player.current_lap_num} | "
              f"Position: P{player.car_position} | "
              f"Time: {player.get_current_lap_time_str()} | "
              f"Last: {player.get_last_lap_time_str()}", end='', flush=True)
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.SESSION, handle_session)
    listener.register_handler(PacketID.LAP_DATA, handle_lap_data)
    listener.start()


# ===== VOORBEELD 3: EVENTS TRACKER =====
def example_events():
    """
    Track belangrijke race events
    """
    print("\n📋 VOORBEELD 3: Event Tracker")
    print("=" * 60)
    
    # Bewaar participant namen
    participant_names = {}
    
    def handle_participants(packet: ParticipantsPacket):
        nonlocal participant_names
        print(f"\n👥 Sessie gestart met {packet.num_active_cars} auto's:")
        for i in range(packet.num_active_cars):
            participant = packet.participants[i]
            participant_names[i] = participant.name
            status = "🤖 AI" if participant.ai_controlled else "👤 Human"
            print(f"   {i+1:2d}. {status} #{participant.race_number:2d} {participant.name:20s} ({participant.get_team_name()})")
    
    def handle_event(packet: EventPacket):
        event_code = packet.event_string_code
        
        if event_code == "FTLP":  # Fastest Lap
            idx = packet.event_details['vehicle_idx']
            name = participant_names.get(idx, f"Car {idx}")
            time = packet.event_details['lap_time']
            print(f"\n⚡ FASTEST LAP: {name} - {time:.3f}s")
        
        elif event_code == "RTMT":  # Retirement
            idx = packet.event_details['vehicle_idx']
            name = participant_names.get(idx, f"Car {idx}")
            print(f"\n❌ RETIREMENT: {name}")
        
        elif event_code == "PENA":  # Penalty
            idx = packet.event_details['vehicle_idx']
            name = participant_names.get(idx, f"Car {idx}")
            penalty_time = packet.event_details['time']
            print(f"\n⚠️  PENALTY: {name} - {penalty_time}s")
        
        elif event_code == "RCWN":  # Race Winner
            idx = packet.event_details['vehicle_idx']
            name = participant_names.get(idx, f"Car {idx}")
            print(f"\n🏆 RACE WINNER: {name}")
        
        elif event_code == "DRSE":  # DRS Enabled
            print(f"\n💨 DRS ENABLED")
        
        elif event_code == "DRSD":  # DRS Disabled
            print(f"\n🚫 DRS DISABLED")
        
        elif event_code == "CHQF":  # Chequered Flag
            print(f"\n🏁 CHEQUERED FLAG")
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.PARTICIPANTS, handle_participants)
    listener.register_handler(PacketID.EVENT, handle_event)
    listener.start()


# ===== VOORBEELD 4: SCHADE MONITOR =====
def example_damage_monitor():
    """
    Monitor schade aan je auto
    """
    print("\n📋 VOORBEELD 4: Schade Monitor")
    print("=" * 60)
    
    def handle_damage(packet: CarDamagePacket):
        damage = packet.get_player_damage()
        
        if damage.has_damage():
            print(f"\n⚠️  SCHADE GEDETECTEERD!")
            print(f"   Totaal: {damage.get_total_damage_percentage():.1f}%")
            
            # Toon significante schade (>5%)
            if max(damage.tyres_damage) > 5:
                print(f"   Banden: RL:{damage.tyres_damage[0]}% RR:{damage.tyres_damage[1]}% "
                      f"FL:{damage.tyres_damage[2]}% FR:{damage.tyres_damage[3]}%")
            
            if damage.front_left_wing_damage > 5:
                print(f"   Front Left Wing: {damage.front_left_wing_damage}%")
            if damage.front_right_wing_damage > 5:
                print(f"   Front Right Wing: {damage.front_right_wing_damage}%")
            if damage.rear_wing_damage > 5:
                print(f"   Rear Wing: {damage.rear_wing_damage}%")
            if damage.floor_damage > 5:
                print(f"   Floor: {damage.floor_damage}%")
            if damage.engine_damage > 5:
                print(f"   Engine: {damage.engine_damage}%")
            
            if damage.drs_fault:
                print(f"   ❌ DRS FAULT!")
            if damage.ers_fault:
                print(f"   ❌ ERS FAULT!")
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.CAR_DAMAGE, handle_damage)
    listener.start()


# ===== VOORBEELD 5: UITGEBREIDE DASHBOARD =====
def example_full_dashboard():
    """
    Uitgebreid dashboard met meerdere data types
    """
    print("\n📋 VOORBEELD 5: Volledig Dashboard")
    print("=" * 60)
    
    # State
    current_session = ""
    current_track = ""
    
    def handle_session(packet: SessionPacket):
        nonlocal current_session, current_track
        current_session = packet.get_session_type_name()
        current_track = packet.get_track_name()
    
    def handle_telemetry(packet: CarTelemetryPacket):
        player = packet.get_player_telemetry()
        
        # Band temperaturen (gemiddeld)
        avg_tyre_temp = sum(player.tyres_surface_temperature) / 4
        
        print(f"\r🏎️  {player.speed:3d} km/h | "
              f"G{player.gear} | "
              f"{player.engine_rpm:5d} RPM | "
              f"🌡️ {avg_tyre_temp:.0f}°C | "
              f"⛽ Throttle {player.throttle:4.0%} | "
              f"🔴 Brake {player.brake:4.0%}", end='', flush=True)
    
    def handle_lap_data(packet: LapDataPacket):
        player = packet.get_player_lap_data()
        
        if player.current_lap_num > 0:
            print(f"\n📍 {current_session} @ {current_track}")
            print(f"   Lap {player.current_lap_num} | P{player.car_position} | "
                  f"Current: {player.get_current_lap_time_str()} | "
                  f"Last: {player.get_last_lap_time_str()}")
    
    def handle_status(packet: CarStatusPacket):
        status = packet.get_player_status()
        
        # Print status info af en toe (niet elke frame)
        if packet.header.frame_identifier % 60 == 0:  # Elke 60 frames
            print(f"\n⚙️  Status:")
            print(f"   Fuel: {status.fuel_in_tank:.1f}L ({status.fuel_remaining_laps:.1f} laps)")
            print(f"   ERS: {status.ers_store_energy:.1f}J")
            print(f"   DRS: {'✓ Beschikbaar' if status.drs_allowed else '✗ Niet beschikbaar'}")
            print(f"   Banden: {status.get_tyre_compound_name()} ({status.tyres_age_laps} laps)")
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.SESSION, handle_session)
    listener.register_handler(PacketID.CAR_TELEMETRY, handle_telemetry)
    listener.register_handler(PacketID.LAP_DATA, handle_lap_data)
    listener.register_handler(PacketID.CAR_STATUS, handle_status)
    listener.start()


# ===== VOORBEELD 6: DATA LOGGER =====
def example_data_logger():
    """
    Log alle data naar bestanden (voor latere analyse)
    """
    print("\n📋 VOORBEELD 6: Data Logger")
    print("=" * 60)
    
    import json
    from datetime import datetime
    
    # Maak log bestanden
    session_start = datetime.now().strftime("%Y%m%d_%H%M%S")
    telemetry_log = open(f"telemetry_{session_start}.jsonl", "w")
    lap_log = open(f"laps_{session_start}.jsonl", "w")
    
    def handle_telemetry(packet: CarTelemetryPacket):
        player = packet.get_player_telemetry()
        
        data = {
            'timestamp': packet.header.session_time,
            'frame': packet.header.frame_identifier,
            'speed': player.speed,
            'gear': player.gear,
            'rpm': player.engine_rpm,
            'throttle': player.throttle,
            'brake': player.brake,
            'steer': player.steer,
            'drs': player.drs,
        }
        
        telemetry_log.write(json.dumps(data) + "\n")
        telemetry_log.flush()
        
        # Print progress
        if packet.header.frame_identifier % 60 == 0:
            print(f"\r📝 Logging... Frame {packet.header.frame_identifier}", end='', flush=True)
    
    def handle_lap_data(packet: LapDataPacket):
        player = packet.get_player_lap_data()
        
        if player.last_lap_time_ms > 0:
            data = {
                'lap': player.current_lap_num - 1,
                'time_ms': player.last_lap_time_ms,
                'time_str': player.get_last_lap_time_str(),
                'position': player.car_position,
                'valid': not player.current_lap_invalid,
            }
            
            lap_log.write(json.dumps(data) + "\n")
            lap_log.flush()
            
            print(f"\n✓ Lap {data['lap']}: {data['time_str']} (P{data['position']})")
    
    try:
        listener = F1TelemetryListener()
        listener.register_handler(PacketID.CAR_TELEMETRY, handle_telemetry)
        listener.register_handler(PacketID.LAP_DATA, handle_lap_data)
        listener.start()
    finally:
        telemetry_log.close()
        lap_log.close()
        print(f"\n✓ Logs opgeslagen!")


# ===== VOORBEELD 7: MULTIPLAYER LEADERBOARD =====
def example_multiplayer_leaderboard():
    """
    Toon real-time leaderboard in multiplayer
    """
    print("\n📋 VOORBEELD 7: Multiplayer Leaderboard")
    print("=" * 60)
    
    participant_names = {}
    
    def handle_participants(packet: ParticipantsPacket):
        nonlocal participant_names
        for i in range(packet.num_active_cars):
            participant_names[i] = packet.participants[i].name
    
    def handle_lap_data(packet: LapDataPacket):
        # Print leaderboard elke 2 seconden (120 frames @ 60fps)
        if packet.header.frame_identifier % 120 != 0:
            return
        
        leaderboard = packet.get_leaderboard()
        
        print("\n" + "=" * 60)
        print("🏆 LEADERBOARD")
        print("=" * 60)
        print(f"{'Pos':<4} {'Driver':<20} {'Lap':<4} {'Last Lap':<12} {'Gap':<10}")
        print("-" * 60)
        
        leader_time = None
        for car_idx, lap_data in leaderboard[:10]:  # Top 10
            name = participant_names.get(car_idx, f"Car {car_idx}")
            position = lap_data.car_position
            lap_num = lap_data.current_lap_num
            last_lap = lap_data.get_last_lap_time_str()
            
            # Bereken gap naar leider
            if leader_time is None:
                leader_time = lap_data.total_distance
                gap = "Leader"
            else:
                gap_distance = leader_time - lap_data.total_distance
                if gap_distance > 0:
                    gap = f"+{gap_distance:.1f}m"
                else:
                    gap = "-"
            
            print(f"{position:<4} {name:<20} {lap_num:<4} {last_lap:<12} {gap:<10}")
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.PARTICIPANTS, handle_participants)
    listener.register_handler(PacketID.LAP_DATA, handle_lap_data)
    listener.start()


# ===== VOORBEELD 8: RONDETIJDEN MET SECTORTIJDEN =====
def example_lap_times():
    """
    Toon rondetijden met sectortijden per ronde
    """
    print("\n📋 VOORBEELD 8: Rondetijden met Sectortijden")
    print("=" * 70)
    
    driver_names = {}
    last_lap_printed = {}
    
    def handle_participants(packet: ParticipantsPacket):
        nonlocal driver_names
        for i in range(packet.num_active_cars):
            if i < len(packet.participants):
                driver_names[i] = packet.participants[i].name
    
    def format_sector_time(ms_part: int, min_part: int) -> str:
        """Converteer sector tijd naar leesbaar formaat"""
        if ms_part == 0 and min_part == 0:
            return "--:--.---"
        
        total_seconds = (min_part * 60) + (ms_part / 1000.0)
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        
        if minutes > 0:
            return f"{minutes}:{seconds:06.3f}"
        else:
            return f"{seconds:.3f}s"
    
    def handle_lap_data(packet: LapDataPacket):
        nonlocal last_lap_printed
        player_idx = packet.header.player_car_index
        player_data = packet.get_player_lap_data()
        
        # Toon huidige status
        print(f"\r🏎️  Lap {player_data.current_lap_num} | "
              f"Sector {player_data.sector} | "
              f"Current: {player_data.get_current_lap_time_str()} | "
              f"Position: P{player_data.car_position}", 
              end='', flush=True)
        
        # Als er een nieuwe rondetijd is
        if player_data.last_lap_time_ms > 0:
            # Voorkom dubbele output
            lap_key = (player_idx, player_data.current_lap_num, player_data.last_lap_time_ms)
            if lap_key in last_lap_printed:
                return
            last_lap_printed[lap_key] = True
            
            driver_name = driver_names.get(player_idx, "You")
            valid = "✓ GELDIG" if not player_data.current_lap_invalid else "✗ ONGELDIG"
            
            # Format sectortijden
            sector1 = format_sector_time(player_data.sector1_time_ms, player_data.sector1_time_minutes)
            sector2 = format_sector_time(player_data.sector2_time_ms, player_data.sector2_time_minutes)
            
            # Bereken sector 3
            if player_data.sector1_time_ms > 0 and player_data.sector2_time_ms > 0:
                total_ms = player_data.last_lap_time_ms
                s1_total = (player_data.sector1_time_minutes * 60000) + player_data.sector1_time_ms
                s2_total = (player_data.sector2_time_minutes * 60000) + player_data.sector2_time_ms
                s3_ms = total_ms - s1_total - s2_total
                
                if s3_ms > 0:
                    s3_seconds = s3_ms / 1000.0
                    sector3 = f"{s3_seconds:.3f}s"
                else:
                    sector3 = "--:--.---"
            else:
                sector3 = "--:--.---"
            
            # Print mooie output
            print(f"\n\n{'='*70}")
            print(f"🏁 RONDE {player_data.current_lap_num - 1} VOLTOOID!")
            print(f"{'='*70}")
            print(f"  Driver:     {driver_name}")
            print(f"  Positie:    P{player_data.car_position}")
            print(f"  Status:     {valid}")
            print(f"{'-'*70}")
            print(f"  📊 SECTORTIJDEN:")
            print(f"     Sector 1:  {sector1}")
            print(f"     Sector 2:  {sector2}")
            print(f"     Sector 3:  {sector3}")
            print(f"{'-'*70}")
            print(f"  ⏱️  RONDETIJD: {player_data.get_last_lap_time_str()}")
            print(f"{'='*70}\n")
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.PARTICIPANTS, handle_participants)
    listener.register_handler(PacketID.LAP_DATA, handle_lap_data)
    listener.start()


# ===== HOOFD MENU =====
def main():
    """
    Hoofd menu om een voorbeeld te kiezen
    """
    print("\n" + "=" * 60)
    print("🏎️  F1 25 TELEMETRY - VOORBEELDEN")
    print("=" * 60)
    print("\nKies een voorbeeld:")
    print("  1. Basis Telemetrie (snelheid, RPM, versnelling)")
    print("  2. Sessie Informatie (circuit, weer, rondetijden)")
    print("  3. Event Tracker (fastest lap, penalties, race winner)")
    print("  4. Schade Monitor")
    print("  5. Volledig Dashboard")
    print("  6. Data Logger (opslaan naar bestanden)")
    print("  7. Multiplayer Leaderboard")
    print("  8. Rondetijden met Sectortijden")
    print("\n  0. Afsluiten")
    print("=" * 60)
    
    try:
        choice = input("\nKeuze (0-8): ").strip()
        
        if choice == "1":
            example_basic_telemetry()
        elif choice == "2":
            example_session_info()
        elif choice == "3":
            example_events()
        elif choice == "4":
            example_damage_monitor()
        elif choice == "5":
            example_full_dashboard()
        elif choice == "6":
            example_data_logger()
        elif choice == "7":
            example_multiplayer_leaderboard()
        elif choice == "8":
            example_lap_times()
        elif choice == "0":
            print("\n👋 Tot ziens!")
        else:
            print("\n❌ Ongeldige keuze!")
            main()
    
    except KeyboardInterrupt:
        print("\n\n👋 Tot ziens!")


if __name__ == "__main__":
    print("\n⚠️  BELANGRIJK:")
    print("   1. Start F1 25")
    print("   2. Ga naar Instellingen > UDP Telemetry Settings")
    print("   3. Zet 'UDP Telemetry' op 'Enabled'")
    print("   4. IP: 127.0.0.1, Port: 20777")
    print("   5. Format: 2025")
    print()
    
    main()