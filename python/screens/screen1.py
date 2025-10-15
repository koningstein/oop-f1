"""
Screen 1: Overview / Leaderboard / Tournament
All functions for leaderboards, lap times, tournaments and position charts

Packets used:
- Packet 2: Lap Data (lap times, sector times, positions)
- Packet 4: Participants (driver names, teams)
- Packet 11: Session History (lap history, consistency)
- Packet 1: Session (session type, track)
- Packet 3: Event (fastest lap, race winner)
- Packet 8: Final Classification (final results, points)
- Packet 15: Lap Positions (position progression per lap)
"""

from telemetry_listener import F1TelemetryListener
from packet_types import PacketID
from lap_packets import LapDataPacket, LapPositionsPacket
from participants_packets import ParticipantsPacket
from session_packets import SessionPacket, EventPacket
from other_packets import FinalClassificationPacket, SessionHistoryPacket

# Global variabele om de actieve listener bij te houden
active_listener = None

def get_active_listener():
    """Geef de actieve listener terug"""
    global active_listener
    return active_listener

def set_active_listener(listener):
    """Sla de actieve listener op"""
    global active_listener
    active_listener = listener


# ==================== HELPER FUNCTIES ====================

def format_time(ms: int) -> str:
    """Format tijd in ms naar mm:ss.SSS"""
    if ms == 0:
        return "--:--.---"
    
    total_seconds = ms / 1000.0
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60
    
    if minutes > 0:
        return f"{minutes}:{seconds:06.3f}"
    else:
        return f"{seconds:.3f}"

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


# ==================== HOOFDFUNCTIES ====================

def toon_alle_data():
    """
    Toon alle data: Volledig leaderboard met rondetijden en sectortijden
    Combineert: leaderboard + lap times + events
    """
    print("\n📊 SCHERM 1 - VOLLEDIG OVERZICHT")
    print("=" * 80)
    print("Druk op ENTER om te stoppen\n")
    
    # State
    driver_names = {}
    lap_times = {}  # {car_idx: {lap_num: time}}
    positions = {}  # {car_idx: position}
    last_lap_printed = {}
    
    def handle_participants(packet: ParticipantsPacket):
        nonlocal driver_names
        print("\n👥 DEELNEMERS:")
        for i in range(packet.num_active_cars):
            if i < len(packet.participants):
                participant = packet.participants[i]
                driver_names[i] = participant.name
                status = "👤" if not participant.ai_controlled else "🤖"
                print(f"   {status} #{participant.race_number:2d} {participant.name:20s}")
        print()
    
    def handle_session(packet: SessionPacket):
        print(f"\n📍 SESSIE INFO:")
        print(f"   Type:     {packet.get_session_type_name()}")
        print(f"   Circuit:  {packet.get_track_name()}")
        print(f"   Rondes:   {packet.total_laps}")
        print(f"   Weer:     {packet.get_weather_name()}")
        print()
    
    def handle_lap_data(packet: LapDataPacket):
        nonlocal lap_times, positions, last_lap_printed
        
        # Update posities en tijden
        for i in range(packet.header.player_car_index + 1):  # Minimaal tot player
            if i < len(packet.lap_data):
                lap_data = packet.lap_data[i]
                positions[i] = lap_data.car_position
                
                # Check nieuwe rondetijd
                if lap_data.last_lap_time_ms > 0:
                    lap_key = (i, lap_data.current_lap_num, lap_data.last_lap_time_ms)
                    if lap_key not in last_lap_printed:
                        last_lap_printed[lap_key] = True
                        
                        driver_name = driver_names.get(i, f"Car {i}")
                        lap_time_str = format_time(lap_data.last_lap_time_ms)
                        valid = "✓" if not lap_data.current_lap_invalid else "✗"
                        
                        # Sectortijden
                        s1 = format_sector_time(lap_data.sector1_time_ms, lap_data.sector1_time_minutes)
                        s2 = format_sector_time(lap_data.sector2_time_ms, lap_data.sector2_time_minutes)
                        
                        print(f"🏁 Lap {lap_data.current_lap_num - 1:2d} | "
                              f"P{lap_data.car_position} {driver_name:15s} | "
                              f"{lap_time_str} {valid} | "
                              f"S1:{s1} S2:{s2}")
        
        # Toon live leaderboard (top 5)
        player_data = packet.get_player_lap_data()
        print(f"\r🏎️  Lap {player_data.current_lap_num} | "
              f"P{player_data.car_position} | "
              f"Time: {player_data.get_current_lap_time_str()}", end='', flush=True)
    
    def handle_event(packet: EventPacket):
        event_code = packet.event_string_code
        
        if event_code == "FTLP":  # Fastest Lap
            idx = packet.event_details['vehicle_idx']
            name = driver_names.get(idx, f"Car {idx}")
            time = packet.event_details['lap_time']
            print(f"\n\n⚡ FASTEST LAP: {name} - {time:.3f}s\n")
        
        elif event_code == "RCWN":  # Race Winner
            idx = packet.event_details['vehicle_idx']
            name = driver_names.get(idx, f"Car {idx}")
            print(f"\n\n🏆 RACE WINNER: {name}\n")
    
    # Start listener
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.PARTICIPANTS, handle_participants)
    listener.register_handler(PacketID.SESSION, handle_session)
    listener.register_handler(PacketID.LAP_DATA, handle_lap_data)
    listener.register_handler(PacketID.EVENT, handle_event)
    
    set_active_listener(listener)
    
    try:
        listener.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if "10048" not in str(e):
            print(f"\n❌ Fout: {e}")


def practice_leaderboard():
    """
    Practice Mode: Leaderboard met rondetijden
    Toont alle rondetijden gesorteerd op snelheid
    """
    print("\n🏁 PRACTICE MODE - LEADERBOARD")
    print("=" * 80)
    print("Druk op ENTER om te stoppen\n")
    
    driver_names = {}
    best_laps = {}  # {car_idx: best_lap_time_ms}
    
    def handle_participants(packet: ParticipantsPacket):
        nonlocal driver_names
        for i in range(packet.num_active_cars):
            if i < len(packet.participants):
                driver_names[i] = packet.participants[i].name
    
    def handle_lap_data(packet: LapDataPacket):
        nonlocal best_laps
        
        # Update best laps
        for i in range(len(packet.lap_data)):
            lap_data = packet.lap_data[i]
            if lap_data.last_lap_time_ms > 0 and not lap_data.current_lap_invalid:
                if i not in best_laps or lap_data.last_lap_time_ms < best_laps[i]:
                    best_laps[i] = lap_data.last_lap_time_ms
        
        # Print leaderboard (elke 60 frames = ~1 sec)
        if packet.header.frame_identifier % 60 == 0 and best_laps:
            print("\n" + "=" * 80)
            print("🏆 LEADERBOARD - BESTE RONDETIJDEN")
            print("=" * 80)
            
            # Sorteer op tijd
            sorted_laps = sorted(best_laps.items(), key=lambda x: x[1])
            
            for pos, (car_idx, lap_time) in enumerate(sorted_laps[:10], 1):  # Top 10
                driver_name = driver_names.get(car_idx, f"Car {car_idx}")
                lap_time_str = format_time(lap_time)
                
                # Gap to leader
                gap = ""
                if pos > 1:
                    gap_ms = lap_time - sorted_laps[0][1]
                    gap = f"+{gap_ms/1000:.3f}s"
                
                print(f"  {pos:2d}. {driver_name:20s}  {lap_time_str:>10s}  {gap}")
            
            print("=" * 80)
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.PARTICIPANTS, handle_participants)
    listener.register_handler(PacketID.LAP_DATA, handle_lap_data)
    
    set_active_listener(listener)
    
    try:
        listener.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if "10048" not in str(e):
            print(f"\n❌ Fout: {e}")


def practice_consistency():
    """
    Practice Mode: Consistentie analyse
    Berekent standaarddeviatie van rondetijden per rijder
    """
    print("\n📈 PRACTICE MODE - CONSISTENTIE ANALYSE")
    print("=" * 80)
    print("Druk op ENTER om te stoppen\n")
    
    import statistics
    
    driver_names = {}
    all_laps = {}  # {car_idx: [lap_times]}
    
    def handle_participants(packet: ParticipantsPacket):
        nonlocal driver_names
        for i in range(packet.num_active_cars):
            if i < len(packet.participants):
                driver_names[i] = packet.participants[i].name
                all_laps[i] = []
    
    def handle_lap_data(packet: LapDataPacket):
        nonlocal all_laps
        
        # Verzamel rondetijden
        for i in range(len(packet.lap_data)):
            lap_data = packet.lap_data[i]
            if lap_data.last_lap_time_ms > 0 and not lap_data.current_lap_invalid:
                if i in all_laps and lap_data.last_lap_time_ms not in all_laps[i]:
                    all_laps[i].append(lap_data.last_lap_time_ms)
        
        # Print consistentie analyse (elke 120 frames = ~2 sec)
        if packet.header.frame_identifier % 120 == 0:
            consistency_data = []
            
            for car_idx, laps in all_laps.items():
                if len(laps) >= 3:  # Minimaal 3 rondes voor statistiek
                    avg_time = statistics.mean(laps)
                    std_dev = statistics.stdev(laps)
                    best_time = min(laps)
                    
                    consistency_data.append({
                        'car_idx': car_idx,
                        'avg': avg_time,
                        'std_dev': std_dev,
                        'best': best_time,
                        'laps': len(laps)
                    })
            
            if consistency_data:
                # Sorteer op standaarddeviatie (laagste = meest consistent)
                consistency_data.sort(key=lambda x: x['std_dev'])
                
                print("\n" + "=" * 90)
                print("📊 CONSISTENTIE ANALYSE (lagere std dev = consistenter)")
                print("=" * 90)
                print(f"{'Pos':<4} {'Driver':<20} {'Laps':<6} {'Best':<12} {'Avg':<12} {'Std Dev':<10}")
                print("-" * 90)
                
                for pos, data in enumerate(consistency_data[:10], 1):
                    driver_name = driver_names.get(data['car_idx'], f"Car {data['car_idx']}")
                    best_str = format_time(data['best'])
                    avg_str = format_time(int(data['avg']))
                    std_dev_str = f"{data['std_dev']/1000:.3f}s"
                    
                    print(f"{pos:<4} {driver_name:<20} {data['laps']:<6} "
                          f"{best_str:<12} {avg_str:<12} {std_dev_str:<10}")
                
                print("=" * 90)
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.PARTICIPANTS, handle_participants)
    listener.register_handler(PacketID.LAP_DATA, handle_lap_data)
    
    set_active_listener(listener)
    
    try:
        listener.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if "10048" not in str(e):
            print(f"\n❌ Fout: {e}")


def race_live_klassement():
    """
    Race Mode: Live klassement met posities en gaps
    """
    print("\n🏆 RACE MODE - LIVE KLASSEMENT")
    print("=" * 80)
    print("Druk op ENTER om te stoppen\n")
    
    driver_names = {}
    
    def handle_participants(packet: ParticipantsPacket):
        nonlocal driver_names
        for i in range(packet.num_active_cars):
            if i < len(packet.participants):
                driver_names[i] = packet.participants[i].name
    
    def handle_lap_data(packet: LapDataPacket):
        # Sorteer rijders op positie
        sorted_drivers = sorted(
            enumerate(packet.lap_data),
            key=lambda x: x[1].car_position if x[1].car_position < 255 else 999
        )
        
        # Print klassement (elke 30 frames)
        if packet.header.frame_identifier % 30 == 0:
            print("\n" + "=" * 80)
            print(f"🏁 LIVE KLASSEMENT - Lap {packet.get_player_lap_data().current_lap_num}")
            print("=" * 80)
            print(f"{'Pos':<4} {'Driver':<20} {'Lap':<5} {'Gap':<12} {'Last Lap':<12}")
            print("-" * 80)
            
            leader_time = None
            for car_idx, lap_data in sorted_drivers[:22]:  # Max 22 cars
                if lap_data.car_position == 255:  # Ongeldige positie
                    continue
                
                driver_name = driver_names.get(car_idx, f"Car {car_idx}")
                lap_num = lap_data.current_lap_num
                last_lap = format_time(lap_data.last_lap_time_ms)
                
                # Bereken gap
                if lap_data.car_position == 1:
                    gap = "Leader"
                    leader_time = lap_data.total_distance
                else:
                    # Gap in tijd (via delta to leader)
                    gap_ms = (lap_data.delta_to_race_leader_minutes * 60000) + lap_data.delta_to_race_leader_ms
                    gap = f"+{gap_ms/1000:.3f}s"
                
                print(f"{lap_data.car_position:<4} {driver_name:<20} {lap_num:<5} {gap:<12} {last_lap:<12}")
            
            print("=" * 80)
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.PARTICIPANTS, handle_participants)
    listener.register_handler(PacketID.LAP_DATA, handle_lap_data)
    
    set_active_listener(listener)
    
    try:
        listener.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if "10048" not in str(e):
            print(f"\n❌ Fout: {e}")


# ==================== PLACEHOLDER FUNCTIES ====================

def race_deltas():
    """Race Mode: Delta's tussen rijders"""
    print("\n⏱️  LIVE RONDETIJDEN MET SECTORTIJDEN")
    print("=" * 70)
    print("Druk op ENTER om te stoppen\n")
    
    driver_names = {}
    last_lap_printed = {}
    
    # Track sector data per car per lap
    sector_data = {}  # {(car_idx, lap_num): {'s1': ms, 's2': ms, 's1_printed': bool, 's2_printed': bool}}
    
    def handle_participants(packet: ParticipantsPacket):
        nonlocal driver_names
        for i in range(packet.num_active_cars):
            if i < len(packet.participants):
                driver_names[i] = packet.participants[i].name
    
    def handle_lap_data(packet: LapDataPacket):
        nonlocal last_lap_printed, sector_data
        player_idx = packet.header.player_car_index
        player_data = packet.get_player_lap_data()
        
        lap_num = player_data.current_lap_num
        sector_key = (player_idx, lap_num)
        
        # Initialiseer sector data voor deze lap als die nog niet bestaat
        if sector_key not in sector_data:
            sector_data[sector_key] = {
                's1': 0,
                's2': 0,
                's1_printed': False,
                's2_printed': False
            }
        
        # Check of sector 1 nieuw is en nog niet geprint
        current_s1_time = player_data.sector1_time_ms
        if current_s1_time > 0 and not sector_data[sector_key]['s1_printed']:
            sector_data[sector_key]['s1'] = current_s1_time
            sector_data[sector_key]['s1_printed'] = True
            
            sector_time = format_sector_time(player_data.sector1_time_ms, player_data.sector1_time_minutes)
            driver_name = driver_names.get(player_idx, f"Car {player_idx}")
            
            print(f"\n⏱️  {driver_name} - SECTOR 1: {sector_time}")
        
        # Check of sector 2 nieuw is en nog niet geprint
        current_s2_time = player_data.sector2_time_ms
        if current_s2_time > 0 and not sector_data[sector_key]['s2_printed']:
            sector_data[sector_key]['s2'] = current_s2_time
            sector_data[sector_key]['s2_printed'] = True
            
            sector_time = format_sector_time(player_data.sector2_time_ms, player_data.sector2_time_minutes)
            driver_name = driver_names.get(player_idx, f"Car {player_idx}")
            
            print(f"\n⏱️  {driver_name} - SECTOR 2: {sector_time}")
        
        # Sector is 0-indexed: 0=sector1, 1=sector2, 2=sector3
        current_sector_display = player_data.sector + 1
        
        # Toon huidige status - gebruik \n voor nieuwe regel ipv \r
        if packet.header.frame_identifier % 10 == 0:  # Update elke 10 frames
            print(f"🏎️  Lap {player_data.current_lap_num} | "
                  f"Sector {current_sector_display} | "
                  f"P{player_data.car_position} | "
                  f"Time: {player_data.get_current_lap_time_str()}", end='\r', flush=True)
        
        # Als ronde voltooid
        if player_data.last_lap_time_ms > 0:
            lap_key = (player_idx, player_data.current_lap_num, player_data.last_lap_time_ms)
            if lap_key not in last_lap_printed:
                last_lap_printed[lap_key] = True
                
                driver_name = driver_names.get(player_idx, f"Car {player_idx}")
                
                # Gebruik de HUIDIGE lap data (die net voltooid is)
                # Deze data zit in sector_key van de LAP die net AF is (current_lap_num - 1)
                prev_lap_key = (player_idx, player_data.current_lap_num - 1)
                
                # Format sectortijden
                sector1 = format_sector_time(player_data.sector1_time_ms, player_data.sector1_time_minutes)
                sector2 = format_sector_time(player_data.sector2_time_ms, player_data.sector2_time_minutes)
                
                # Bereken sector 3
                sector3 = "--:--.---"
                if player_data.sector1_time_ms > 0 and player_data.sector2_time_ms > 0:
                    total_ms = player_data.last_lap_time_ms
                    s1_total = (player_data.sector1_time_minutes * 60000) + player_data.sector1_time_ms
                    s2_total = (player_data.sector2_time_minutes * 60000) + player_data.sector2_time_ms
                    s3_ms = total_ms - s1_total - s2_total
                    
                    if s3_ms > 0:
                        s3_seconds = s3_ms / 1000.0
                        sector3 = f"{s3_seconds:.3f}s"
                
                print(f"\n\n{'='*70}")
                print(f"🏁 {driver_name} - RONDE {player_data.current_lap_num - 1} VOLTOOID!")
                print(f"{'='*70}")
                print(f"  Positie:    P{player_data.car_position}")
                print(f"  Status:     {'✓ GELDIG' if not player_data.current_lap_invalid else '✗ ONGELDIG'}")
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
    
    set_active_listener(listener)
    
    try:
        listener.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if "10048" not in str(e):
            print(f"\n❌ Fout: {e}")

def toernooi_stand():
    """Toernooi: Kampioenschapsstand"""
    print("\n⚠️  Toernooi Kampioenschapsstand - Nog niet geïmplementeerd")
    input("\nDruk op ENTER om terug te gaan...")

def toernooi_historie():
    """Toernooi: Race historie"""
    print("\n⚠️  Toernooi Race Historie - Nog niet geïmplementeerd")
    input("\nDruk op ENTER om terug te gaan...")

def toernooi_punten():
    """Toernooi: Punten systeem"""
    print("\n⚠️  Toernooi Punten Systeem - Nog niet geïmplementeerd")
    input("\nDruk op ENTER om terug te gaan...")

def position_chart():
    """Position Chart: Positieverloop per ronde"""
    print("\n⚠️  Position Chart - Nog niet geïmplementeerd")
    input("\nDruk op ENTER om terug te gaan...")