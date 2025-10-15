"""
Screen 3: Realtime Data Car 1
All functions for displaying realtime telemetry data for Car 1

Packets used:
- Packet 6: Car Telemetry (speed, RPM, gear, throttle, brake, steer, DRS, temperatures, tyre pressures)
- Packet 7: Car Status (fuel, ERS, DRS allowed, tyre compound, tyre age)
- Packet 10: Car Damage (tyre wear, wing damage, engine wear, floor damage, gearbox damage)
- Packet 2: Lap Data (current lap time, sector times, lap number, position)
- Packet 5: Car Setups (wing settings, brake bias, differential, suspension, tyre pressures)
- Packet 12: Tyre Sets (available tyre sets, wear per set, recommended session, expected lifespan)
- Packet 13: Motion Ex (wheel speeds, slip ratios, wheel forces, suspension positions)
"""

from telemetry_listener import F1TelemetryListener
from packet_types import PacketID
from car_packets import CarTelemetryPacket, CarStatusPacket, CarDamagePacket
from lap_packets import LapDataPacket
from other_packets import CarSetupsPacket, TyreSetsPacket
from motion_packets import MotionExPacket

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


# ==================== HOOFDFUNCTIES ====================

def toon_alle_data():
    """
    Toon alle data: Complete dashboard met telemetrie, status, schade en lap data
    """
    print("\n📊 SCHERM 3 - REALTIME DATA AUTO 1")
    print("=" * 80)
    print("Druk op ENTER om te stoppen\n")
    
    def handle_telemetry(packet: CarTelemetryPacket):
        player = packet.get_player_telemetry()
        
        # Basis telemetrie
        print(f"\r🏎️  Speed: {player.speed:3d} km/h | "
              f"G{player.gear} | "
              f"{player.engine_rpm:5d} RPM | "
              f"🎮 {player.throttle:4.0%} | "
              f"🔴 {player.brake:4.0%} | "
              f"DRS: {'✓' if player.drs else '✗'}", end='', flush=True)
    
    def handle_status(packet: CarStatusPacket):
        player = packet.get_player_status()
        
        # Print status elke 60 frames
        if packet.header.frame_identifier % 60 == 0:
            print(f"\n\n⛽ FUEL & ERS:")
            print(f"   Fuel:        {player.fuel_in_tank:.1f}L / {player.fuel_capacity:.1f}L")
            print(f"   Laps left:   {player.fuel_remaining_laps:.1f}")
            print(f"   ERS Store:   {player.ers_store_energy:.0f}J")
            print(f"   ERS Deploy:  {player.ers_deployed_this_lap:.0f}J")
            print(f"\n🏁 TYRES:")
            print(f"   Compound:    {player.get_tyre_compound_name()}")
            print(f"   Age:         {player.tyres_age_laps} laps")
            print(f"   DRS:         {'✓ Available' if player.drs_allowed else '✗ Not allowed'}")
            print()
    
    def handle_damage(packet: CarDamagePacket):
        player = packet.get_player_damage()
        
        # Print schade elke 120 frames als er schade is
        if packet.header.frame_identifier % 120 == 0 and player.has_damage():
            print(f"\n⚠️  DAMAGE DETECTED:")
            print(f"   Total:       {player.get_total_damage_percentage():.1f}%")
            
            if max(player.tyres_damage) > 5:
                print(f"   Tyres:       RL:{player.tyres_damage[0]}% "
                      f"RR:{player.tyres_damage[1]}% "
                      f"FL:{player.tyres_damage[2]}% "
                      f"FR:{player.tyres_damage[3]}%")
            
            if player.front_left_wing_damage > 5:
                print(f"   FL Wing:     {player.front_left_wing_damage}%")
            if player.front_right_wing_damage > 5:
                print(f"   FR Wing:     {player.front_right_wing_damage}%")
            if player.rear_wing_damage > 5:
                print(f"   Rear Wing:   {player.rear_wing_damage}%")
            if player.engine_damage > 5:
                print(f"   Engine:      {player.engine_damage}%")
            print()
    
    def handle_lap_data(packet: LapDataPacket):
        player = packet.get_player_lap_data()
        
        # Print lap info elke 90 frames
        if packet.header.frame_identifier % 90 == 0:
            print(f"\n📍 LAP INFO:")
            print(f"   Lap:         {player.current_lap_num}")
            print(f"   Position:    P{player.car_position}")
            print(f"   Current:     {player.get_current_lap_time_str()}")
            print(f"   Last:        {player.get_last_lap_time_str()}")
            print()
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.CAR_TELEMETRY, handle_telemetry)
    listener.register_handler(PacketID.CAR_STATUS, handle_status)
    listener.register_handler(PacketID.CAR_DAMAGE, handle_damage)
    listener.register_handler(PacketID.LAP_DATA, handle_lap_data)
    
    set_active_listener(listener)
    
    try:
        listener.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if "10048" not in str(e):
            print(f"\n❌ Fout: {e}")


def dashboard_live_telemetrie():
    """
    Dashboard: Live telemetrie met primaire data
    """
    print("\n🏎️  DASHBOARD - LIVE TELEMETRIE AUTO 1")
    print("=" * 80)
    print("Druk op ENTER om te stoppen\n")
    
    def handle_telemetry(packet: CarTelemetryPacket):
        player = packet.get_player_telemetry()
        
        # Bereken gemiddelde band temperatuur
        avg_tyre_temp = sum(player.tyres_surface_temperature) / 4
        
        # DRS status
        drs_status = "ON " if player.drs else "OFF"
        
        print(f"\r┌─────────────────────────────────────────────────────────┐", end='')
        print(f"\r\n│ Speed: {player.speed:3d} km/h  │  Gear: {player.gear:2d}  │  RPM: {player.engine_rpm:5d}  │", end='')
        print(f"\r\n├─────────────────────────────────────────────────────────┤", end='')
        print(f"\r\n│ 🎮 Throttle: {player.throttle:5.1%}  │  🔴 Brake: {player.brake:5.1%}      │", end='')
        print(f"\r\n│ 🎯 Steer: {player.steer:6.3f}  │  💨 DRS: {drs_status}             │", end='')
        print(f"\r\n├─────────────────────────────────────────────────────────┤", end='')
        print(f"\r\n│ 🌡️  Engine: {player.engine_temperature:3d}°C  │  Tyres: {avg_tyre_temp:5.1f}°C   │", end='')
        print(f"\r\n└─────────────────────────────────────────────────────────┘", end='', flush=True)
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.CAR_TELEMETRY, handle_telemetry)
    
    set_active_listener(listener)
    
    try:
        listener.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if "10048" not in str(e):
            print(f"\n❌ Fout: {e}")


def fuel_ers_management():
    """
    Fuel & ERS Management: Real-time brandstof en ERS data
    """
    print("\n⛽ FUEL & ERS MANAGEMENT AUTO 1")
    print("=" * 80)
    print("Druk op ENTER om te stoppen\n")
    
    def handle_status(packet: CarStatusPacket):
        player = packet.get_player_status()
        
        # Bereken fuel percentage
        fuel_percent = (player.fuel_in_tank / player.fuel_capacity * 100) if player.fuel_capacity > 0 else 0
        
        # ERS percentage
        ers_percent = (player.ers_store_energy / 4000000 * 100)  # Max ~4MJ
        
        # Fuel bar
        fuel_bar_length = 30
        fuel_filled = int(fuel_bar_length * fuel_percent / 100)
        fuel_bar = "█" * fuel_filled + "░" * (fuel_bar_length - fuel_filled)
        
        # ERS bar
        ers_filled = int(fuel_bar_length * ers_percent / 100)
        ers_bar = "█" * ers_filled + "░" * (fuel_bar_length - ers_filled)
        
        print(f"\r" + "=" * 80, end='')
        print(f"\r\n⛽ FUEL", end='')
        print(f"\r\n   Tank:        {player.fuel_in_tank:.1f}L / {player.fuel_capacity:.1f}L ({fuel_percent:.1f}%)", end='')
        print(f"\r\n   [{fuel_bar}]", end='')
        print(f"\r\n   Laps left:   {player.fuel_remaining_laps:.1f} laps", end='')
        print(f"\r\n   Mix:         {player.fuel_mix}", end='')
        print(f"\r\n", end='')
        print(f"\r\n⚡ ERS", end='')
        print(f"\r\n   Store:       {player.ers_store_energy:.0f}J ({ers_percent:.1f}%)", end='')
        print(f"\r\n   [{ers_bar}]", end='')
        print(f"\r\n   Deployed:    {player.ers_deployed_this_lap:.0f}J this lap", end='')
        print(f"\r\n   Mode:        {player.ers_deploy_mode}", end='')
        print(f"\r\n" + "=" * 80, end='', flush=True)
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.CAR_STATUS, handle_status)
    
    set_active_listener(listener)
    
    try:
        listener.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if "10048" not in str(e):
            print(f"\n❌ Fout: {e}")


def damage_monitoring():
    """
    Damage Monitoring: Visuele weergave van schade per onderdeel
    """
    print("\n🔧 DAMAGE MONITORING AUTO 1")
    print("=" * 80)
    print("Druk op ENTER om te stoppen\n")
    
    def handle_damage(packet: CarDamagePacket):
        player = packet.get_player_damage()
        
        print(f"\r" + "=" * 80, end='')
        print(f"\r\n⚠️  DAMAGE OVERVIEW", end='')
        print(f"\r\n   Total Damage: {player.get_total_damage_percentage():.1f}%", end='')
        print(f"\r\n", end='')
        print(f"\r\n🏁 TYRES:", end='')
        print(f"\r\n   RL: {player.tyres_damage[0]:3.0f}%  [{self._damage_bar(player.tyres_damage[0])}]", end='')
        print(f"\r\n   RR: {player.tyres_damage[1]:3.0f}%  [{self._damage_bar(player.tyres_damage[1])}]", end='')
        print(f"\r\n   FL: {player.tyres_damage[2]:3.0f}%  [{self._damage_bar(player.tyres_damage[2])}]", end='')
        print(f"\r\n   FR: {player.tyres_damage[3]:3.0f}%  [{self._damage_bar(player.tyres_damage[3])}]", end='')
        print(f"\r\n", end='')
        print(f"\r\n🛫 WINGS:", end='')
        print(f"\r\n   Front L: {player.front_left_wing_damage:3.0f}%  [{self._damage_bar(player.front_left_wing_damage)}]", end='')
        print(f"\r\n   Front R: {player.front_right_wing_damage:3.0f}%  [{self._damage_bar(player.front_right_wing_damage)}]", end='')
        print(f"\r\n   Rear:    {player.rear_wing_damage:3.0f}%  [{self._damage_bar(player.rear_wing_damage)}]", end='')
        print(f"\r\n", end='')
        print(f"\r\n🔧 COMPONENTS:", end='')
        print(f"\r\n   Engine:  {player.engine_damage:3.0f}%  [{self._damage_bar(player.engine_damage)}]", end='')
        print(f"\r\n   Gearbox: {player.gearbox_damage:3.0f}%  [{self._damage_bar(player.gearbox_damage)}]", end='')
        print(f"\r\n   Floor:   {player.floor_damage:3.0f}%  [{self._damage_bar(player.floor_damage)}]", end='')
        print(f"\r\n", end='')
        
        if player.drs_fault:
            print(f"\r\n   ❌ DRS FAULT!", end='')
        if player.ers_fault:
            print(f"\r\n   ❌ ERS FAULT!", end='')
        
        print(f"\r\n" + "=" * 80, end='', flush=True)
    
    def _damage_bar(damage_percent):
        """Maak een visuele damage bar"""
        bar_length = 20
        filled = int(bar_length * damage_percent / 100)
        
        if damage_percent < 20:
            return "█" * filled + "░" * (bar_length - filled)
        elif damage_percent < 50:
            return "▓" * filled + "░" * (bar_length - filled)
        else:
            return "▓" * filled + "░" * (bar_length - filled)
    
    # Maak _damage_bar beschikbaar in handle_damage
    handle_damage._damage_bar = _damage_bar
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.CAR_DAMAGE, handle_damage)
    
    set_active_listener(listener)
    
    try:
        listener.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if "10048" not in str(e):
            print(f"\n❌ Fout: {e}")


def setup_tab():
    """
    Setup Tab: Setup data tonen
    """
    print("\n⚙️  SETUP TAB AUTO 1")
    print("=" * 80)
    print("Druk op ENTER om te stoppen\n")
    
    def handle_setups(packet: CarSetupsPacket):
        player = packet.get_player_setup()
        
        # Print setup elke 120 frames
        if packet.header.frame_identifier % 120 == 0:
            print(f"\r" + "=" * 80, end='')
            print(f"\r\n⚙️  CAR SETUP", end='')
            print(f"\r\n", end='')
            print(f"\r\n🛫 AERODYNAMICS:", end='')
            print(f"\r\n   Front Wing:  {player.front_wing}", end='')
            print(f"\r\n   Rear Wing:   {player.rear_wing}", end='')
            print(f"\r\n", end='')
            print(f"\r\n🔧 MECHANICAL:", end='')
            print(f"\r\n   Diff On:     {player.on_throttle}", end='')
            print(f"\r\n   Diff Off:    {player.off_throttle}", end='')
            print(f"\r\n   Brake Bias:  {player.brake_bias}%", end='')
            print(f"\r\n", end='')
            print(f"\r\n🏁 SUSPENSION:", end='')
            print(f"\r\n   FL Height:   {player.front_suspension}", end='')
            print(f"\r\n   RL Height:   {player.rear_suspension}", end='')
            print(f"\r\n   FL Camber:   {player.front_camber}", end='')
            print(f"\r\n   RL Camber:   {player.rear_camber}", end='')
            print(f"\r\n   FL Toe:      {player.front_toe}", end='')
            print(f"\r\n   RL Toe:      {player.rear_toe}", end='')
            print(f"\r\n", end='')
            print(f"\r\n📊 TYRE PRESSURE:", end='')
            print(f"\r\n   RL: {player.rear_left_tyre_pressure:.1f} PSI", end='')
            print(f"\r\n   RR: {player.rear_right_tyre_pressure:.1f} PSI", end='')
            print(f"\r\n   FL: {player.front_left_tyre_pressure:.1f} PSI", end='')
            print(f"\r\n   FR: {player.front_right_tyre_pressure:.1f} PSI", end='')
            print(f"\r\n" + "=" * 80, end='', flush=True)
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.CAR_SETUPS, handle_setups)
    
    set_active_listener(listener)
    
    try:
        listener.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if "10048" not in str(e):
            print(f"\n❌ Fout: {e}")


# ==================== PLACEHOLDER FUNCTIES ====================

def tyre_management():
    """Tyre Management: Overzicht band sets"""
    print("\n⚠️  Tyre Management - Nog niet geïmplementeerd")
    print("(Packet 12: Tyre Sets - Beschikbare band sets met slijtage)")
    input("\nDruk op ENTER om terug te gaan...")

def advanced_telemetry():
    """Advanced Telemetry: Wielspecifieke data"""
    print("\n⚠️  Advanced Telemetry - Nog niet geïmplementeerd")
    print("(Packet 13: Motion Ex - Wielsnelheden, slip ratios, wielkrachten)")
    input("\nDruk op ENTER om terug te gaan...")