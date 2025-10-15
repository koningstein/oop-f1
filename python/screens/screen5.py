"""
Screen 5: Race Strategy & Tyre Management
All functions for lap time comparison, tyre strategy and position analysis

Packets used:
- Packet 2: Lap Data (lap times, sector times both cars, delta calculation, positions)
- Packet 11: Session History (consistency metrics, lap time trends, best laps, tyre stint history)
- Packet 6: Car Telemetry (speed comparisons per sector, throttle/brake patterns, gear shifts)
- Packet 4: Participants (names both students, team info)
- Packet 5: Car Setups (setup differences between both cars)
- Packet 12: Tyre Sets (all available tyre sets, wear, lifespan, recommended session)
- Packet 7: Car Status (current tyre compound, tyre age, fuel remaining)
- Packet 10: Car Damage (tyre wear percentage per tyre)
- Packet 15: Lap Positions (position progression comparison between both drivers)
"""

from telemetry_listener import F1TelemetryListener
from packet_types import PacketID
from lap_packets import LapDataPacket, LapPositionsPacket
from car_packets import CarTelemetryPacket, CarStatusPacket, CarDamagePacket
from participants_packets import ParticipantsPacket
from other_packets import CarSetupsPacket, TyreSetsPacket, SessionHistoryPacket
import statistics

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

def format_delta(delta_ms: int) -> str:
    """Format delta tijd met + of -"""
    if delta_ms == 0:
        return "    -    "
    
    sign = "+" if delta_ms > 0 else ""
    return f"{sign}{delta_ms/1000:.3f}s"


# ==================== HOOFDFUNCTIES ====================

def toon_alle_data():
    """
    Toon alle data: Complete strategy overview met lap times, tyre info en positions
    """
    print("\n📊 SCHERM 5 - RACE STRATEGY & TYRE MANAGEMENT")
    print("=" * 80)
    print("Druk op ENTER om te stoppen\n")
    
    driver_names = {}
    lap_history = {}  # {car_idx: [lap_times]}
    
    def handle_participants(packet: ParticipantsPacket):
        nonlocal driver_names
        print("\n👥 DRIVERS:")
        for i in range(min(packet.num_active_cars, 2)):  # Toon max 2
            if i < len(packet.participants):
                driver_names[i] = packet.participants[i].name
                print(f"   Car {i+1}: {packet.participants[i].name}")
        print()
    
    def handle_lap_data(packet: LapDataPacket):
        nonlocal lap_history
        
        # Verzamel lap data voor beide cars
        for i in range(min(2, len(packet.lap_data))):
            if packet.lap_data[i].last_lap_time_ms > 0:
                if i not in lap_history:
                    lap_history[i] = []
                
                if packet.lap_data[i].last_lap_time_ms not in lap_history[i]:
                    lap_history[i].append(packet.lap_data[i].last_lap_time_ms)
        
        # Print summary elke 60 frames
        if packet.header.frame_identifier % 60 == 0:
            print(f"\r" + "=" * 80, end='')
            print(f"\r\n⏱️  LAP TIMES SUMMARY", end='')
            
            for car_idx in range(min(2, len(packet.lap_data))):
                lap_data = packet.lap_data[car_idx]
                driver_name = driver_names.get(car_idx, f"Car {car_idx+1}")
                
                print(f"\r\n\n{driver_name}:", end='')
                print(f"\r\n   Current Lap:  {lap_data.current_lap_num}", end='')
                print(f"\r\n   Position:     P{lap_data.car_position}", end='')
                print(f"\r\n   Last Lap:     {format_time(lap_data.last_lap_time_ms)}", end='')
                
                if car_idx in lap_history and len(lap_history[car_idx]) >= 2:
                    avg = statistics.mean(lap_history[car_idx])
                    best = min(lap_history[car_idx])
                    print(f"\r\n   Best:         {format_time(best)}", end='')
                    print(f"\r\n   Average:      {format_time(int(avg))}", end='')
                    print(f"\r\n   Laps:         {len(lap_history[car_idx])}", end='')
            
            print(f"\r\n" + "=" * 80, end='', flush=True)
    
    def handle_status(packet: CarStatusPacket):
        # Print tyre info elke 120 frames
        if packet.header.frame_identifier % 120 == 0:
            for car_idx in range(min(2, len(packet.car_status_data))):
                status = packet.car_status_data[car_idx]
                driver_name = driver_names.get(car_idx, f"Car {car_idx+1}")
                
                print(f"\r\n\n🏁 TYRES - {driver_name}:", end='')
                print(f"\r\n   Compound:     {status.get_tyre_compound_name()}", end='')
                print(f"\r\n   Age:          {status.tyres_age_laps} laps", end='')
                print(f"\r\n   Fuel Left:    {status.fuel_remaining_laps:.1f} laps", end='')
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.PARTICIPANTS, handle_participants)
    listener.register_handler(PacketID.LAP_DATA, handle_lap_data)
    listener.register_handler(PacketID.CAR_STATUS, handle_status)
    
    set_active_listener(listener)
    
    try:
        listener.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if "10048" not in str(e):
            print(f"\n❌ Fout: {e}")


def lap_time_comparison():
    """
    Lap Time Comparison: Side-by-side vergelijking van beide auto's
    """
    print("\n⏱️  LAP TIME COMPARISON - SIDE BY SIDE")
    print("=" * 90)
    print("Druk op ENTER om te stoppen\n")
    
    driver_names = {}
    last_lap_printed = {}
    
    def handle_participants(packet: ParticipantsPacket):
        nonlocal driver_names
        for i in range(min(packet.num_active_cars, 2)):
            if i < len(packet.participants):
                driver_names[i] = packet.participants[i].name
    
    def handle_lap_data(packet: LapDataPacket):
        nonlocal last_lap_printed
        
        # Check voor nieuwe rondetijden
        for car_idx in range(min(2, len(packet.lap_data))):
            lap_data = packet.lap_data[car_idx]
            
            if lap_data.last_lap_time_ms > 0:
                lap_key = (car_idx, lap_data.current_lap_num, lap_data.last_lap_time_ms)
                
                if lap_key not in last_lap_printed:
                    last_lap_printed[lap_key] = True
                    
                    driver_name = driver_names.get(car_idx, f"Car {car_idx+1}")
                    
                    # Sectortijden
                    s1 = format_sector_time(lap_data.sector1_time_ms, lap_data.sector1_time_minutes)
                    s2 = format_sector_time(lap_data.sector2_time_ms, lap_data.sector2_time_minutes)
                    
                    # Bereken S3
                    s3 = "--:--.---"
                    if lap_data.sector1_time_ms > 0 and lap_data.sector2_time_ms > 0:
                        s1_total = (lap_data.sector1_time_minutes * 60000) + lap_data.sector1_time_ms
                        s2_total = (lap_data.sector2_time_minutes * 60000) + lap_data.sector2_time_ms
                        s3_ms = lap_data.last_lap_time_ms - s1_total - s2_total
                        if s3_ms > 0:
                            s3 = f"{s3_ms/1000:.3f}s"
                    
                    print(f"\n🏁 Lap {lap_data.current_lap_num - 1} | {driver_name}")
                    print(f"   Total: {format_time(lap_data.last_lap_time_ms)} | "
                          f"S1: {s1} | S2: {s2} | S3: {s3}")
                    print(f"   Position: P{lap_data.car_position} | "
                          f"Valid: {'✓' if not lap_data.current_lap_invalid else '✗'}")
        
        # Live status
        if len(packet.lap_data) >= 2:
            car1 = packet.lap_data[0]
            car2 = packet.lap_data[1]
            
            name1 = driver_names.get(0, "Car 1")
            name2 = driver_names.get(1, "Car 2")
            
            print(f"\r{name1}: Lap {car1.current_lap_num} P{car1.car_position} | "
                  f"{name2}: Lap {car2.current_lap_num} P{car2.car_position}", end='', flush=True)
    
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


def lap_time_deltas():
    """
    Lap Time Comparison: Delta's per sector
    """
    print("\n📊 LAP TIME DELTAS PER SECTOR")
    print("=" * 90)
    print("Druk op ENTER om te stoppen\n")
    
    driver_names = {}
    sector_times = {0: {}, 1: {}}  # {car_idx: {lap_num: (s1, s2, s3)}}
    
    def handle_participants(packet: ParticipantsPacket):
        nonlocal driver_names
        for i in range(min(2, len(packet.participants))):
            driver_names[i] = packet.participants[i].name
    
    def handle_lap_data(packet: LapDataPacket):
        for car_idx in range(min(2, len(packet.lap_data))):
            lap_data = packet.lap_data[car_idx]
            lap_num = lap_data.current_lap_num
            
            if lap_data.last_lap_time_ms > 0 and lap_num not in sector_times[car_idx]:
                s1_total = (lap_data.sector1_time_minutes * 60000) + lap_data.sector1_time_ms
                s2_total = (lap_data.sector2_time_minutes * 60000) + lap_data.sector2_time_ms
                s3_ms = lap_data.last_lap_time_ms - s1_total - s2_total
                
                sector_times[car_idx][lap_num] = (s1_total, s2_total, s3_ms)
                
                # Als beide cars deze lap hebben, bereken delta
                if lap_num in sector_times[0] and lap_num in sector_times[1]:
                    s1_car1, s2_car1, s3_car1 = sector_times[0][lap_num]
                    s1_car2, s2_car2, s3_car2 = sector_times[1][lap_num]
                    
                    delta_s1 = s1_car2 - s1_car1
                    delta_s2 = s2_car2 - s2_car1
                    delta_s3 = s3_car2 - s3_car1
                    delta_total = delta_s1 + delta_s2 + delta_s3
                    
                    name1 = driver_names.get(0, "Car 1")
                    name2 = driver_names.get(1, "Car 2")
                    
                    print(f"\n{'='*90}")
                    print(f"Lap {lap_num} Comparison: {name1} vs {name2}")
                    print(f"{'='*90}")
                    print(f"{'Sector':<15} {name1:<20} {name2:<20} {'Delta':<15}")
                    print(f"{'-'*90}")
                    print(f"{'S1':<15} {format_time(s1_car1):<20} {format_time(s1_car2):<20} {format_delta(delta_s1):<15}")
                    print(f"{'S2':<15} {format_time(s2_car1):<20} {format_time(s2_car2):<20} {format_delta(delta_s2):<15}")
                    print(f"{'S3':<15} {format_time(int(s3_car1)):<20} {format_time(int(s3_car2)):<20} {format_delta(int(delta_s3)):<15}")
                    print(f"{'-'*90}")
                    print(f"{'TOTAL':<15} {format_time(s1_car1+s2_car1+int(s3_car1)):<20} "
                          f"{format_time(s1_car2+s2_car2+int(s3_car2)):<20} {format_delta(int(delta_total)):<15}")
                    print(f"{'='*90}\n")
    
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


def consistency_metrics():
    """
    Lap Time Comparison: Consistency metrics (standaarddeviatie)
    """
    print("\n📈 CONSISTENCY METRICS")
    print("=" * 80)
    print("Druk op ENTER om te stoppen\n")
    
    driver_names = {}
    all_laps = {0: [], 1: []}  # {car_idx: [lap_times]}
    
    def handle_participants(packet: ParticipantsPacket):
        nonlocal driver_names
        for i in range(min(2, len(packet.participants))):
            driver_names[i] = packet.participants[i].name
    
    def handle_lap_data(packet: LapDataPacket):
        for car_idx in range(min(2, len(packet.lap_data))):
            lap_data = packet.lap_data[car_idx]
            
            if lap_data.last_lap_time_ms > 0 and not lap_data.current_lap_invalid:
                if lap_data.last_lap_time_ms not in all_laps[car_idx]:
                    all_laps[car_idx].append(lap_data.last_lap_time_ms)
        
        # Print analyse elke 120 frames
        if packet.header.frame_identifier % 120 == 0:
            print(f"\n{'='*80}")
            print(f"CONSISTENCY ANALYSIS")
            print(f"{'='*80}")
            
            for car_idx in range(2):
                if len(all_laps[car_idx]) >= 3:
                    driver_name = driver_names.get(car_idx, f"Car {car_idx+1}")
                    laps = all_laps[car_idx]
                    
                    avg = statistics.mean(laps)
                    std_dev = statistics.stdev(laps)
                    best = min(laps)
                    worst = max(laps)
                    
                    print(f"\n{driver_name}:")
                    print(f"   Laps:         {len(laps)}")
                    print(f"   Best:         {format_time(best)}")
                    print(f"   Worst:        {format_time(worst)}")
                    print(f"   Average:      {format_time(int(avg))}")
                    print(f"   Std Dev:      {std_dev/1000:.3f}s  {'(Very Consistent)' if std_dev < 500 else '(Inconsistent)' if std_dev > 1000 else '(Consistent)'}")
            
            print(f"\n{'='*80}\n")
    
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


def tyre_status():
    """
    Tyre Strategy: Current tyre status voor beide auto's
    """
    print("\n🏁 CURRENT TYRE STATUS")
    print("=" * 80)
    print("Druk op ENTER om te stoppen\n")
    
    driver_names = {}
    
    def handle_participants(packet: ParticipantsPacket):
        nonlocal driver_names
        for i in range(min(2, len(packet.participants))):
            driver_names[i] = packet.participants[i].name
    
    def handle_status(packet: CarStatusPacket):
        print(f"\r" + "=" * 80, end='')
        print(f"\r\n🏁 TYRE STATUS", end='')
        
        for car_idx in range(min(2, len(packet.car_status_data))):
            status = packet.car_status_data[car_idx]
            driver_name = driver_names.get(car_idx, f"Car {car_idx+1}")
            
            print(f"\r\n\n{driver_name}:", end='')
            print(f"\r\n   Compound:     {status.get_tyre_compound_name()}", end='')
            print(f"\r\n   Visual:       {status.get_visual_tyre_compound_name()}", end='')
            print(f"\r\n   Age:          {status.tyres_age_laps} laps", end='')
            print(f"\r\n   Temp (avg):   [calculating from telemetry...]", end='')
        
        print(f"\r\n" + "=" * 80, end='', flush=True)
    
    def handle_damage(packet: CarDamagePacket):
        # Voeg tyre wear toe elke 60 frames
        if packet.header.frame_identifier % 60 == 0:
            for car_idx in range(min(2, len(packet.car_damage_data))):
                damage = packet.car_damage_data[car_idx]
                driver_name = driver_names.get(car_idx, f"Car {car_idx+1}")
                
                print(f"\r\n\n{driver_name} - Tyre Wear:", end='')
                print(f"\r\n   RL: {damage.tyres_damage[0]:.1f}%", end='')
                print(f"\r\n   RR: {damage.tyres_damage[1]:.1f}%", end='')
                print(f"\r\n   FL: {damage.tyres_damage[2]:.1f}%", end='')
                print(f"\r\n   FR: {damage.tyres_damage[3]:.1f}%", end='')
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.PARTICIPANTS, handle_participants)
    listener.register_handler(PacketID.CAR_STATUS, handle_status)
    listener.register_handler(PacketID.CAR_DAMAGE, handle_damage)
    
    set_active_listener(listener)
    
    try:
        listener.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if "10048" not in str(e):
            print(f"\n❌ Fout: {e}")


# ==================== PLACEHOLDER FUNCTIES ====================

def setup_analyse():
    """Lap Time Comparison: Setup analyse"""
    print("\n⚠️  Setup Analyse - Nog niet geïmplementeerd")
    print("(Packet 5: Car Setups - Setup verschillen tussen beide auto's)")
    input("\nDruk op ENTER om terug te gaan...")

def tyre_set_overview():
    """Tyre Strategy: Band set overview"""
    print("\n⚠️  Tyre Set Overview - Nog niet geïmplementeerd")
    print("(Packet 12: Tyre Sets - Alle beschikbare band sets)")
    input("\nDruk op ENTER om terug te gaan...")

def stint_comparison():
    """Tyre Strategy: Stint comparison"""
    print("\n⚠️  Stint Comparison - Nog niet geïmplementeerd")
    print("(Vergelijking bandkeuzes tussen beide rijders)")
    input("\nDruk op ENTER om terug te gaan...")

def degradation_curves():
    """Tyre Strategy: Degradation curves"""
    print("\n⚠️  Degradation Curves - Nog niet geïmplementeerd")
    print("(Grafiek van bandslijtage over tijd)")
    input("\nDruk op ENTER om terug te gaan...")

def position_battle_chart():
    """Position & Strategy: Position battle chart"""
    print("\n⚠️  Position Battle Chart - Nog niet geïmplementeerd")
    print("(Packet 15: Lap Positions - Grafische weergave posities per ronde)")
    input("\nDruk op ENTER om terug te gaan...")

def stint_timeline():
    """Position & Strategy: Stint timeline"""
    print("\n⚠️  Stint Timeline - Nog niet geïmplementeerd")
    print("(Visualisatie van tyre stints en pitstops)")
    input("\nDruk op ENTER om terug te gaan...")

def optimal_strategy():
    """Position & Strategy: Optimal strategy suggestion"""
    print("\n⚠️  Optimal Strategy - Nog niet geïmplementeerd")
    print("(Aanbevolen pitstop timing gebaseerd op slijtage)")
    input("\nDruk op ENTER om terug te gaan...")

def fuel_vs_tyre_strategy():
    """Position & Strategy: Fuel vs tyre strategy"""
    print("\n⚠️  Fuel vs Tyre Strategy - Nog niet geïmplementeerd")
    print("(Correlatie tussen brandstof management en band strategie)")
    input("\nDruk op ENTER om terug te gaan...")