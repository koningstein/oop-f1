"""
F1 2025 UDP Telemetry Listener
===============================
Gebruikt f1-packets API om telemetrie data te ontvangen en op te slaan in MySQL

Installatie: pip install -r requirements.txt
Gebruik: python f1_telemetry_listener.py
"""

import socket
import mysql.connector
from datetime import datetime
from f1.packets import PacketHeader, HEADER_FIELD_TO_PACKET_TYPE
from config import config

# Optional: colorama for pretty output
try:
    from colorama import init, Fore, Style
    init()
except ImportError:
    class Fore:
        GREEN = RED = YELLOW = CYAN = RESET = ""
    class Style:
        BRIGHT = RESET_ALL = ""


class F1TelemetryListener:
    """
    Hoofdklasse voor F1 telemetrie ontvangst met f1-packets API
    """
    
    def __init__(self):
        # UDP Socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((config.UDP_IP, config.UDP_PORT))
        
         # Voeg deze regel toe om een timeout van 1 seconde in te stellen
        self.socket.settimeout(1.0) # <--- NIEUW: 1 seconde timeout
        # NIEUW: Staat voor console output filtering
        self.is_waiting_for_data = False # <--- TOEGEVOEGD

        # Database
        self.db = None
        self.cursor = None
        
        # Session data (wordt gevuld door packets)
        self.current_track = None
        self.track_id = None
        self.session_type = None
        self.participants = {}  # {index: name}
        self.player_index = None
        
        # Cache om dubbele opslag te voorkomen
        self.processed_laps = set()
        
        # Statistieken
        self.packets_received = 0
        self.laps_saved = 0

        # STATE MANAGEMENT VOOR CONSOLE OUTPUT
        self.seen_packet_types = set() # <--- TOEGEVOEGD: voor unieke packet melding
        self.session_info_printed = False # <--- TOEGEVOEGD: voor eenmalige sessie print
        self.player_info_printed = False # <--- TOEGEVOEGD: voor eenmalige speler print
        
        
        print(f"\n{Fore.CYAN}{'='*60}")
        print("🏎️  F1 2025 TELEMETRY LISTENER")
        print(f"{'='*60}{Style.RESET_ALL}")
        config.print_config()
    
    # ==================== PACKET PARSING ====================
    
    def parse_packet(self, data):
        """Parse UDP packet met f1-packets library"""
        try:
            # Parse header eerst
            header = PacketHeader.from_buffer_copy(data)
            
            # Haal juiste packet type op
            packet_type = HEADER_FIELD_TO_PACKET_TYPE.get(header.packet_id)
            
            if packet_type:
                # Parse volledig packet
                packet = packet_type.from_buffer_copy(data)
                return packet
            else:
                return None
                
        except Exception as e:
            if config.DEBUG:
                print(f"{Fore.RED}Parse error: {e}{Style.RESET_ALL}")
            return None
    
    # ==================== DATABASE ====================
    
    def connect_database(self):
        """Verbind met MySQL database"""
        print(f"{Fore.YELLOW}📡 Verbinden met database...{Style.RESET_ALL}")
        
        try:
            self.db = mysql.connector.connect(
                host=config.DB_HOST,
                port=config.DB_PORT,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                database=config.DB_NAME
            )
            self.cursor = self.db.cursor()
            print(f"{Fore.GREEN}✓ Database verbinding succesvol{Style.RESET_ALL}\n")
            return True
            
        except mysql.connector.Error as e:
            print(f"{Fore.RED}✗ Database fout: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}⚠️  Draait zonder database (data wordt niet opgeslagen){Style.RESET_ALL}\n")
            return False
    
    def save_lap_time(self, driver_index, lap_data):
        """
        Sla rondetijd op in database
        lap_data komt van PacketLapData uit f1-packets API
        """
        if not self.db or not lap_data.last_lap_time_in_ms:
            return
        
        # Converteer ms naar seconden
        lap_time = lap_data.last_lap_time_in_ms / 1000.0
        
        # Skip als geen geldige tijd
        if lap_time <= 0:
            return
        
        # Voorkom dubbele opslag
        lap_key = (driver_index, lap_time, lap_data.current_lap_num)
        if lap_key in self.processed_laps:
            return
        
        # Bereken sectortijden
        sector1 = lap_data.sector1_time_in_ms / 1000.0 if lap_data.sector1_time_in_ms > 0 else None
        sector2 = lap_data.sector2_time_in_ms / 1000.0 if lap_data.sector2_time_in_ms > 0 else None
        sector3 = None
        if sector1 and sector2:
            sector3 = lap_time - sector1 - sector2
        
        # Check of lap geldig is (result_status == 3 betekent finished)
        is_valid = lap_data.result_status == 3
        
        # Haal driver naam op
        driver_name = self.participants.get(driver_index, f"Driver {driver_index}")
        
        try:
            query = """
                INSERT INTO lap_times 
                (driver_name, lap_time, track_name, sector1_time, sector2_time, 
                 sector3_time, is_valid, session_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                driver_name,
                lap_time,
                self.current_track or "Unknown",
                sector1,
                sector2,
                sector3,
                is_valid,
                datetime.now()
            )
            
            self.cursor.execute(query, values)
            self.db.commit()
            
            # Cache update
            self.processed_laps.add(lap_key)
            if len(self.processed_laps) > config.MAX_CACHE_SIZE:
                self.processed_laps.clear()
            
            self.laps_saved += 1
            
            # Print
            valid_icon = f"{Fore.GREEN}✓" if is_valid else f"{Fore.RED}✗"
            print(f"{valid_icon} Lap #{self.laps_saved}: {driver_name} - {lap_time:.3f}s op {self.current_track}{Style.RESET_ALL}")
            
        except mysql.connector.Error as e:
            print(f"{Fore.RED}❌ Database error: {e}{Style.RESET_ALL}")
    
    # ==================== PACKET HANDLERS (f1-packets API) ====================
    
    # def handle_session_packet(self, packet):
    #     """
    #     PacketSessionData (Packet ID 1)
    #     Bevat: track info, weather, session type
    #     """
    #     self.track_id = packet.track_id
    #     self.current_track = config.TRACK_NAMES.get(self.track_id, f"Unknown Track {self.track_id}")
    #     self.session_type = packet.session_type
        
    #     session_name = config.SESSION_TYPES.get(self.session_type, "Unknown")
        
    #     print(f"\n{Fore.CYAN}📍 SESSION INFO:{Style.RESET_ALL}")
    #     print(f"   Track:        {self.current_track}")
    #     print(f"   Session:      {session_name}")
    #     print(f"   Weather:      {packet.weather}")
    #     print(f"   Track Temp:   {packet.track_temperature}°C")
    #     print(f"   Air Temp:     {packet.air_temperature}°C\n")

    def handle_session_packet(self, packet):
        """
        PacketSessionData (Packet ID 1)
        Bevat: track info, weather, session type
        """
        current_track_id = packet.track_id
        current_session_type = packet.session_type
        
        # Controleer of de sessie is veranderd. Zo ja, reset de printvlaggen.
        if current_track_id != self.track_id or current_session_type != self.session_type:
            self.session_info_printed = False
            self.player_info_printed = False 
            self.processed_laps.clear()
            self.seen_packet_types.clear() # Reset de set voor nieuwe sessie

        self.track_id = current_track_id
        self.current_track = config.TRACK_NAMES.get(self.track_id, f"Unknown Track {self.track_id}")
        self.session_type = current_session_type
        
        # Print ALLEEN als de sessie informatie nog niet geprint is
        if not self.session_info_printed:
            session_name = config.SESSION_TYPES.get(self.session_type, "Unknown")
            
            print(f"\n{Fore.CYAN}📍 SESSION INFO:{Style.RESET_ALL}")
            print(f"   Track:        {self.current_track}")
            print(f"   Session:      {session_name}")
            print(f"   Weather:      {packet.weather} # (0=Clear, 1=Light Cloud, etc.)")
            print(f"   Track Temp:   {packet.track_temperature}°C")
            print(f"   Air Temp:     {packet.air_temperature}°C\n")
            
            self.session_info_printed = True
    
    def handle_lap_data_packet(self, packet):
        """
        PacketLapData (Packet ID 2)
        Bevat: rondetijden, sectortijden, posities
        """
        # Loop door alle coureurs
        for i, lap_data in enumerate(packet.lap_data):
            # Debug: print als er een lap time is
            if lap_data.last_lap_time_in_ms > 0:
                driver = self.participants.get(i, f"Driver {i}")
                lap_time = lap_data.last_lap_time_in_ms / 1000.0
                print(f"{Fore.CYAN}📊 Lap ontvangen: {driver} - {lap_time:.3f}s (Status: {lap_data.result_status}){Style.RESET_ALL}")
                self.save_lap_time(i, lap_data)
    
    def handle_event_packet(self, packet):
        """
        PacketEventData (Packet ID 3)
        Bevat: fastest lap, retirement, DRS, chequered flag, etc.
        """
        event_codes = {
            b'SSTA': "🏁 Session Started",
            b'SEND': "🏁 Session Ended",
            b'FTLP': "⚡ Fastest Lap",
            b'RTMT': "🔧 Retirement",
            b'DRSE': "💨 DRS Enabled",
            b'DRSD': "💨 DRS Disabled",
            b'CHQF': "🏁 Chequered Flag",
            b'RCWN': "🏆 Race Winner",
            b'PENA': "⚠️  Penalty Issued",
            b'SPTP': "📊 Speed Trap",
            b'LGOT': "🚦 Lights Out!",
        }
        
        event_name = event_codes.get(packet.event_string_code, f"Event: {packet.event_string_code}")
        print(f"{Fore.YELLOW}{event_name}{Style.RESET_ALL}")
    
    # def handle_participants_packet(self, packet):
    #     """
    #     PacketParticipantsData (Packet ID 4)
    #     Bevat: driver namen, teams, AI/human info
    #     """
    #     self.participants = {}
        
    #     for i in range(packet.num_active_cars):
    #         participant = packet.participants[i]
            
    #         # Decode naam (remove null bytes)
    #         try:
    #             name = participant.name.decode('utf-8').rstrip('\x00')
    #             if name:
    #                 self.participants[i] = name
                    
    #                 # Check of dit de speler is (ai_controlled == 1 = human)
    #                 if participant.ai_controlled == 1:
    #                     self.player_index = i
                        
    #         except:
    #             self.participants[i] = f"Driver {i}"
        
    #     if self.player_index is not None:
    #         player_name = self.participants.get(self.player_index, "Unknown")
    #         print(f"{Fore.GREEN}👤 Speler: {player_name} (Index {self.player_index}){Style.RESET_ALL}")
    
    def handle_participants_packet(self, packet):
        """
        PacketParticipantsData (Packet ID 4)
        Bevat: driver namen, teams, AI/human info
        """
        self.participants = {}
        
        for i in range(packet.num_active_cars):
            participant = packet.participants[i]
            
            # Decode naam (remove null bytes)
            try:
                name = participant.name.decode('utf-8').rstrip('\x00')
                if name:
                    self.participants[i] = name
                    
                    # Check of dit de speler is (ai_controlled == 1 = human)
                    if participant.ai_controlled == 1:
                        self.player_index = i
                        
            except:
                self.participants[i] = f"Driver {i}"
        
        if self.player_index is not None:
            player_name = self.participants.get(self.player_index, "Unknown")
            
            # Print ALLEEN als de spelerinformatie nog niet geprint is
            # De oude print: print(f"{Fore.GREEN}👤 Speler: {player_name} (Index {self.player_index}){Style.RESET_ALL}") moet weg
            if self.session_info_printed and not self.player_info_printed:
                print(f"{Fore.GREEN}👤 Speler: {player_name} (Index {self.player_index}) # Dit bevestigt wie je bent{Style.RESET_ALL}")
                self.player_info_printed = True

    def handle_car_setups_packet(self, packet):
        """
        PacketCarSetupData (Packet ID 5)
        Later implementeren voor setup vergelijking
        """
        pass
    
    def handle_car_telemetry_packet(self, packet):
        """
        PacketCarTelemetryData (Packet ID 6)
        Later implementeren voor real-time telemetrie displays
        """
        pass
    
    def handle_car_status_packet(self, packet):
        """
        PacketCarStatusData (Packet ID 7)
        Later implementeren voor fuel/ERS management
        """
        pass
    
    def handle_final_classification_packet(self, packet):
        """
        PacketFinalClassificationData (Packet ID 8)
        Bevat: eindklassement, beste rondetijd, penalties
        """
        print(f"\n{Fore.CYAN}🏁 FINAL CLASSIFICATION:{Style.RESET_ALL}")
        
        for i in range(packet.num_cars):
            result = packet.classification_data[i]
            driver_name = self.participants.get(result.driver_id, f"Driver {result.driver_id}")
            best_lap = result.best_lap_time_in_ms / 1000.0 if result.best_lap_time_in_ms > 0 else 0
            
            print(f"   P{result.position}: {driver_name} - Best: {best_lap:.3f}s")
        print()
    
    def handle_car_damage_packet(self, packet):
        """
        PacketCarDamageData (Packet ID 10)
        Later implementeren voor damage monitoring
        """
        pass
    
    def handle_session_history_packet(self, packet):
        """
        PacketSessionHistoryData (Packet ID 11)
        Later implementeren voor consistency analysis
        """
        pass
    
    # ==================== MAIN LOOP ====================
    
    def listen(self):
        """
        Hoofdloop: ontvang en verwerk UDP packets met f1-packets API
        """
        self.connect_database()
        
        print(f"{Fore.GREEN}{'='*60}")
        print("✅ LISTENER ACTIEF - Wachtend op F1 2025 data...")
        print(f"{'='*60}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}⚙️  F1 2025 Settings:{Style.RESET_ALL}")
        print("   1. Settings > Telemetry Settings")
        print("   2. UDP Telemetry: ON")
        print("   3. IP Address: 127.0.0.1")
        print(f"   4. Port: {config.UDP_PORT}")
        print("   5. Format: 2025\n")
        
        try:
            while True:
                try:
                    # Ontvang UDP packet (zal na 1 seconde falen als er niks is)
                    data, addr = self.socket.recvfrom(2048)
                    self.packets_received += 1

                    # LOGICA BIJ SUCCESVOLLE ONTVANGST (Herstelmelding):
                    if self.is_waiting_for_data:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] {Fore.GREEN}✓ Dataverbinding hersteld! ({len(data)} bytes ontvangen){Style.RESET_ALL}")
                        self.is_waiting_for_data = False
                    
                    # Parse packet met f1-packets API
                    packet = self.parse_packet(data)
                    
                    if packet is None:
                        print(f"{Fore.RED}DEBUG: Packet is None!{Style.RESET_ALL}")
                        continue
                    
                    packet_type = type(packet).__name__
                    print(f"{Fore.YELLOW}DEBUG: Ontvangen packet type = {packet_type}{Style.RESET_ALL}")  # <--- DEBUG


                     # *** UNIEKE PACKET TYPE MELDING (Jouw verzoek) ***
                    if packet_type not in self.seen_packet_types:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] {Fore.MAGENTA}*** NIEUW UNIEK PACKET TYPE: {packet_type} ***{Style.RESET_ALL}")
                        self.seen_packet_types.add(packet_type)
                    # *************************************************

                    # Route naar juiste handler
                    if packet_type == 'PacketSessionData':
                        self.handle_session_packet(packet)
                        
                    elif packet_type == 'PacketLapData':
                        self.handle_lap_data_packet(packet)
                        
                    elif packet_type == 'PacketEventData':
                        self.handle_event_packet(packet)
                        
                    elif packet_type == 'PacketParticipantsData':
                        self.handle_participants_packet(packet)
                        
                    elif packet_type == 'PacketCarSetupData':
                        self.handle_car_setups_packet(packet)
                        
                    elif packet_type == 'PacketCarTelemetryData':
                        self.handle_car_telemetry_packet(packet)
                        
                    elif packet_type == 'PacketCarStatusData':
                        self.handle_car_status_packet(packet)
                        
                    elif packet_type == 'PacketFinalClassificationData':
                        self.handle_final_classification_packet(packet)
                        
                    elif packet_type == 'PacketCarDamageData':
                        self.handle_car_damage_packet(packet)
                        
                    elif packet_type == 'PacketSessionHistoryData':
                        self.handle_session_history_packet(packet)
                
                except socket.timeout:
                    # LOGICA BIJ TIMEOUT (1 seconde is verstreken):
                    if not self.is_waiting_for_data:
                        # Print alleen de EERSTE keer de waarschuwing
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] {Fore.YELLOW}⚠️ GEEN DATA ONTVANGEN. Wacht op F1 2025 telemetrie op poort {config.UDP_PORT}...{Style.RESET_ALL}")
                        self.is_waiting_for_data = True
                
                except Exception as e:
                    # Andere socketfouten opvangen
                    if config.DEBUG:
                        print(f"{Fore.RED}Fout in ontvangst: {e}{Style.RESET_ALL}")

        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}⛔ Listener gestopt door gebruiker (Ctrl+C){Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}📊 STATISTIEKEN:{Style.RESET_ALL}")
            print(f"   Packets ontvangen: {self.packets_received}")
            print(f"   Laps opgeslagen:   {self.laps_saved}")
            
        finally:
            # Sluit connecties
            if self.db:
                self.cursor.close()
                self.db.close()
                print(f"{Fore.GREEN}✓ Database verbinding gesloten{Style.RESET_ALL}")
            
            self.socket.close()
            print(f"{Fore.GREEN}✓ Socket gesloten{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}👋 Tot ziens!{Style.RESET_ALL}\n")


# ==================== START ====================

if __name__ == "__main__":
    listener = F1TelemetryListener()
    listener.listen()
