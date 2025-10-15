"""
Screen 6: Live Track Map + Telemetry Compare
All functions for track visualization and telemetry comparison

Packets used:
- Packet 0: Motion (world position X, Y, Z for track map, velocities)
- Packet 2: Lap Data (lap distance - position on circuit, sector info)
- Packet 6: Car Telemetry (speed, throttle, brake, steer for graphical overlay)
- Packet 1: Session (track ID, track length, session info)
- Packet 4: Participants (driver identification, team colors)
- Packet 13: Motion Ex (slip angles, wheel forces for advanced analysis)
"""

from telemetry_listener import F1TelemetryListener
from packet_types import PacketID
from motion_packets import MotionPacket, MotionExPacket
from lap_packets import LapDataPacket
from car_packets import CarTelemetryPacket
from session_packets import SessionPacket
from participants_packets import ParticipantsPacket
import math

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

def normalize_position(x, y, min_x, max_x, min_y, max_y, width, height):
    """Normaliseer world coordinates naar screen coordinates"""
    # Voorkom division by zero
    range_x = max_x - min_x if max_x != min_x else 1
    range_y = max_y - min_y if max_y != min_y else 1
    
    norm_x = int((x - min_x) / range_x * (width - 1))
    norm_y = int((y - min_y) / range_y * (height - 1))
    
    return norm_x, norm_y

def create_simple_track_map(positions, width=60, height=20):
    """Maak een simpele ASCII track map"""
    if not positions:
        return ["No data yet..."]
    
    # Vind min/max coordinates
    min_x = min(p[0] for p in positions)
    max_x = max(p[0] for p in positions)
    min_y = min(p[1] for p in positions)
    max_y = max(p[1] for p in positions)
    
    # Maak lege grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Plot posities
    for x, y, car_idx in positions:
        norm_x, norm_y = normalize_position(x, y, min_x, max_x, min_y, max_y, width, height)
        
        # Bounds check
        if 0 <= norm_x < width and 0 <= norm_y < height:
            if car_idx == 0:
                grid[norm_y][norm_x] = '1'
            elif car_idx == 1:
                grid[norm_y][norm_x] = '2'
            else:
                grid[norm_y][norm_x] = '·'
    
    # Convert grid naar strings
    return [''.join(row) for row in grid]

def draw_bar(value, max_value, length=20):
    """Teken een horizontale bar"""
    if max_value == 0:
        max_value = 1
    
    filled = int((value / max_value) * length)
    return '█' * filled + '░' * (length - filled)


# ==================== HOOFDFUNCTIES ====================

def toon_alle_data():
    """
    Toon alle data: Track map met posities + live telemetrie overlay
    """
    print("\n📊 SCHERM 6 - LIVE TRACK MAP + TELEMETRIE VERGELIJKING")
    print("=" * 80)
    print("Druk op ENTER om te stoppen\n")
    
    driver_names = {}
    positions = []  # [(x, y, car_idx), ...]
    track_name = "Unknown"
    
    def handle_session(packet: SessionPacket):
        nonlocal track_name
        track_name = packet.get_track_name()
        print(f"\n🗺️  Track: {track_name}")
        print(f"   Length: {packet.track_length}m\n")
    
    def handle_participants(packet: ParticipantsPacket):
        nonlocal driver_names
        for i in range(min(2, packet.num_active_cars)):
            if i < len(packet.participants):
                driver_names[i] = packet.participants[i].name
    
    def handle_motion(packet: MotionPacket):
        nonlocal positions
        
        # Verzamel posities (max laatste 50 voor performance)
        for car_idx in range(min(2, len(packet.car_motion_data))):
            motion = packet.car_motion_data[car_idx]
            positions.append((motion.world_position_x, motion.world_position_z, car_idx))
        
        # Houd lijst beperkt
        if len(positions) > 50:
            positions = positions[-50:]
        
        # Print track map elke 30 frames
        if packet.header.frame_identifier % 30 == 0 and len(positions) > 10:
            print(f"\r" + "=" * 80)
            print(f"🗺️  TRACK MAP - {track_name}")
            print("=" * 80)
            
            track_lines = create_simple_track_map(positions, width=70, height=20)
            for line in track_lines:
                print(f"  {line}")
            
            print("=" * 80)
            print(f"Legend: 1 = {driver_names.get(0, 'Car 1')} | 2 = {driver_names.get(1, 'Car 2')}")
    
    def handle_telemetry(packet: CarTelemetryPacket):
        # Print live telemetrie overlay
        if packet.header.frame_identifier % 10 == 0:
            print(f"\r", end='')
            
            for car_idx in range(min(2, len(packet.car_telemetry_data))):
                telemetry = packet.car_telemetry_data[car_idx]
                driver_name = driver_names.get(car_idx, f"Car {car_idx+1}")
                
                print(f"{driver_name}: {telemetry.speed:3d} km/h G{telemetry.gear} | ", end='')
            
            print(end='', flush=True)
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.SESSION, handle_session)
    listener.register_handler(PacketID.PARTICIPANTS, handle_participants)
    listener.register_handler(PacketID.MOTION, handle_motion)
    listener.register_handler(PacketID.CAR_TELEMETRY, handle_telemetry)
    
    set_active_listener(listener)
    
    try:
        listener.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if "10048" not in str(e):
            print(f"\n❌ Fout: {e}")


def circuit_layout():
    """
    Circuit Layout: 2D track map met real-time posities
    """
    print("\n🗺️  CIRCUIT LAYOUT - 2D TRACK MAP")
    print("=" * 80)
    print("Druk op ENTER om te stoppen\n")
    
    positions = []
    driver_names = {}
    track_info = {}
    
    def handle_session(packet: SessionPacket):
        nonlocal track_info
        track_info = {
            'name': packet.get_track_name(),
            'length': packet.track_length
        }
    
    def handle_participants(packet: ParticipantsPacket):
        nonlocal driver_names
        for i in range(min(2, packet.num_active_cars)):
            if i < len(packet.participants):
                driver_names[i] = packet.participants[i].name
    
    def handle_motion(packet: MotionPacket):
        nonlocal positions
        
        # Update posities
        positions = []
        for car_idx in range(min(2, len(packet.car_motion_data))):
            motion = packet.car_motion_data[car_idx]
            positions.append((motion.world_position_x, motion.world_position_z, car_idx))
        
        # Print map elke 20 frames
        if packet.header.frame_identifier % 20 == 0:
            print("\033[H\033[J")  # Clear screen (ANSI escape)
            
            print("=" * 80)
            print(f"🗺️  {track_info.get('name', 'Track')} - {track_info.get('length', 0)}m")
            print("=" * 80)
            
            if len(positions) >= 2:
                # Maak grotere map
                track_lines = create_simple_track_map(positions, width=75, height=25)
                for line in track_lines:
                    print(f"  {line}")
            else:
                print("\n  Waiting for position data...\n")
            
            print("=" * 80)
            print(f"  1 = {driver_names.get(0, 'Car 1')}")
            print(f"  2 = {driver_names.get(1, 'Car 2')}")
            print("=" * 80)
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.SESSION, handle_session)
    listener.register_handler(PacketID.PARTICIPANTS, handle_participants)
    listener.register_handler(PacketID.MOTION, handle_motion)
    
    set_active_listener(listener)
    
    try:
        listener.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if "10048" not in str(e):
            print(f"\n❌ Fout: {e}")


def throttle_brake_overlay():
    """
    Live Telemetrie Overlay: Throttle/brake inputs
    """
    print("\n🎮 THROTTLE/BRAKE INPUTS")
    print("=" * 80)
    print("Druk op ENTER om te stoppen\n")
    
    driver_names = {}
    
    def handle_participants(packet: ParticipantsPacket):
        nonlocal driver_names
        for i in range(min(2, packet.num_active_cars)):
            if i < len(packet.participants):
                driver_names[i] = packet.participants[i].name
    
    def handle_telemetry(packet: CarTelemetryPacket):
        print(f"\r" + "=" * 80, end='')
        
        for car_idx in range(min(2, len(packet.car_telemetry_data))):
            telemetry = packet.car_telemetry_data[car_idx]
            driver_name = driver_names.get(car_idx, f"Car {car_idx+1}")
            
            throttle_bar = draw_bar(telemetry.throttle, 1.0, 30)
            brake_bar = draw_bar(telemetry.brake, 1.0, 30)
            
            print(f"\r\n\n{driver_name}:", end='')
            print(f"\r\n  🎮 Throttle: {telemetry.throttle:5.1%}  [{throttle_bar}]", end='')
            print(f"\r\n  🔴 Brake:    {telemetry.brake:5.1%}  [{brake_bar}]", end='')
        
        print(f"\r\n" + "=" * 80, end='', flush=True)
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.PARTICIPANTS, handle_participants)
    listener.register_handler(PacketID.CAR_TELEMETRY, handle_telemetry)
    
    set_active_listener(listener)
    
    try:
        listener.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if "10048" not in str(e):
            print(f"\n❌ Fout: {e}")


def speed_comparison():
    """
    Live Telemetrie Overlay: Speed comparison graph
    """
    print("\n💨 SPEED COMPARISON")
    print("=" * 80)
    print("Druk op ENTER om te stoppen\n")
    
    driver_names = {}
    speed_history = {0: [], 1: []}
    
    def handle_participants(packet: ParticipantsPacket):
        nonlocal driver_names
        for i in range(min(2, packet.num_active_cars)):
            if i < len(packet.participants):
                driver_names[i] = packet.participants[i].name
    
    def handle_telemetry(packet: CarTelemetryPacket):
        nonlocal speed_history
        
        # Verzamel speed data
        for car_idx in range(min(2, len(packet.car_telemetry_data))):
            telemetry = packet.car_telemetry_data[car_idx]
            speed_history[car_idx].append(telemetry.speed)
            
            # Houd laatste 50 metingen
            if len(speed_history[car_idx]) > 50:
                speed_history[car_idx] = speed_history[car_idx][-50:]
        
        # Print comparison elke 15 frames
        if packet.header.frame_identifier % 15 == 0:
            print(f"\r" + "=" * 80, end='')
            print(f"\r\n💨 SPEED COMPARISON", end='')
            
            for car_idx in range(min(2, len(packet.car_telemetry_data))):
                telemetry = packet.car_telemetry_data[car_idx]
                driver_name = driver_names.get(car_idx, f"Car {car_idx+1}")
                
                # Bereken avg speed over laatste samples
                avg_speed = 0
                if speed_history[car_idx]:
                    avg_speed = sum(speed_history[car_idx]) / len(speed_history[car_idx])
                
                speed_bar = draw_bar(telemetry.speed, 350, 40)
                
                print(f"\r\n\n{driver_name}:", end='')
                print(f"\r\n  Current: {telemetry.speed:3d} km/h", end='')
                print(f"\r\n  Average: {avg_speed:5.1f} km/h", end='')
                print(f"\r\n  [{speed_bar}]", end='')
            
            print(f"\r\n" + "=" * 80, end='', flush=True)
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.PARTICIPANTS, handle_participants)
    listener.register_handler(PacketID.CAR_TELEMETRY, handle_telemetry)
    
    set_active_listener(listener)
    
    try:
        listener.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if "10048" not in str(e):
            print(f"\n❌ Fout: {e}")


def steering_input():
    """
    Live Telemetrie Overlay: Steering input visualization
    """
    print("\n🎯 STEERING INPUT VISUALIZATION")
    print("=" * 80)
    print("Druk op ENTER om te stoppen\n")
    
    driver_names = {}
    
    def handle_participants(packet: ParticipantsPacket):
        nonlocal driver_names
        for i in range(min(2, packet.num_active_cars)):
            if i < len(packet.participants):
                driver_names[i] = packet.participants[i].name
    
    def handle_telemetry(packet: CarTelemetryPacket):
        print(f"\r" + "=" * 80, end='')
        
        for car_idx in range(min(2, len(packet.car_telemetry_data))):
            telemetry = packet.car_telemetry_data[car_idx]
            driver_name = driver_names.get(car_idx, f"Car {car_idx+1}")
            
            # Steer is -1.0 (left) to 1.0 (right)
            # Center is 0
            steer_pos = int((telemetry.steer + 1.0) / 2.0 * 40)  # Scale to 0-40
            
            steer_bar = ' ' * steer_pos + '│' + ' ' * (40 - steer_pos)
            
            direction = "LEFT" if telemetry.steer < -0.1 else "RIGHT" if telemetry.steer > 0.1 else "CENTER"
            
            print(f"\r\n\n{driver_name}:", end='')
            print(f"\r\n  Steer: {telemetry.steer:6.3f}  ({direction})", end='')
            print(f"\r\n  L [{steer_bar}] R", end='')
        
        print(f"\r\n" + "=" * 80, end='', flush=True)
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.PARTICIPANTS, handle_participants)
    listener.register_handler(PacketID.CAR_TELEMETRY, handle_telemetry)
    
    set_active_listener(listener)
    
    try:
        listener.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if "10048" not in str(e):
            print(f"\n❌ Fout: {e}")


def gear_indicator():
    """
    Live Telemetrie Overlay: Gear indicator
    """
    print("\n⚙️  GEAR INDICATOR + RPM")
    print("=" * 80)
    print("Druk op ENTER om te stoppen\n")
    
    driver_names = {}
    
    def handle_participants(packet: ParticipantsPacket):
        nonlocal driver_names
        for i in range(min(2, packet.num_active_cars)):
            if i < len(packet.participants):
                driver_names[i] = packet.participants[i].name
    
    def handle_telemetry(packet: CarTelemetryPacket):
        print(f"\r" + "=" * 80, end='')
        
        for car_idx in range(min(2, len(packet.car_telemetry_data))):
            telemetry = packet.car_telemetry_data[car_idx]
            driver_name = driver_names.get(car_idx, f"Car {car_idx+1}")
            
            # RPM bar (max ~15000 RPM voor F1)
            rpm_bar = draw_bar(telemetry.engine_rpm, 15000, 40)
            
            # Rev lights percentage
            rev_bar = draw_bar(telemetry.rev_lights_percent, 100, 20)
            
            print(f"\r\n\n{driver_name}:", end='')
            print(f"\r\n  ⚙️  Gear:       {telemetry.gear:2d}", end='')
            print(f"\r\n  🔄 RPM:        {telemetry.engine_rpm:5d}", end='')
            print(f"\r\n      [{rpm_bar}]", end='')
            print(f"\r\n  💡 Rev Lights: [{rev_bar}] {telemetry.rev_lights_percent}%", end='')
        
        print(f"\r\n" + "=" * 80, end='', flush=True)
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.PARTICIPANTS, handle_participants)
    listener.register_handler(PacketID.CAR_TELEMETRY, handle_telemetry)
    
    set_active_listener(listener)
    
    try:
        listener.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if "10048" not in str(e):
            print(f"\n❌ Fout: {e}")


# ==================== PLACEHOLDER FUNCTIES ====================

def corner_analysis():
    """Corner Analysis: Visualisatie bocht aanpak verschillen"""
    print("\n⚠️  Corner Analysis - Nog niet geïmplementeerd")
    print("(Analyse van throttle/brake patronen per bocht)")
    input("\nDruk op ENTER om terug te gaan...")

def corner_by_corner():
    """Corner-by-corner vergelijking"""
    print("\n⚠️  Corner-by-Corner Comparison - Nog niet geïmplementeerd")
    print("(Delta's per bocht segment)")
    input("\nDruk op ENTER om terug te gaan...")

def slip_analysis():
    """Slip Analysis: Slip angles en grip levels"""
    print("\n⚠️  Slip Analysis - Nog niet geïmplementeerd")
    print("(Packet 13: Motion Ex - Visualisatie slip angles en grip per wiel)")
    input("\nDruk op ENTER om terug te gaan...")