"""
Screen 2: Input / Tournament Management
All functions for student registration, simulator selection, session control and tournament setup

Packets used:
- Packet 4: Participants (active participants display)
- Packet 1: Session (session status, track info, session type)
- Packet 3: Event (session started/ended triggers)
"""

from telemetry_listener import F1TelemetryListener
from packet_types import PacketID
from session_packets import SessionPacket, EventPacket
from participants_packets import ParticipantsPacket
import json
import os
from datetime import datetime

# Global variabele om de actieve listener bij te houden
active_listener = None

# Bestandspaden voor data opslag
DATA_DIR = "data"
STUDENTS_FILE = os.path.join(DATA_DIR, "students.json")
TOURNAMENT_FILE = os.path.join(DATA_DIR, "tournament.json")

def get_active_listener():
    """Geef de actieve listener terug"""
    global active_listener
    return active_listener

def set_active_listener(listener):
    """Sla de actieve listener op"""
    global active_listener
    active_listener = listener


# ==================== DATA MANAGEMENT ====================

def ensure_data_dir():
    """Zorg dat data directory bestaat"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_students():
    """Laad studenten uit JSON bestand"""
    ensure_data_dir()
    if os.path.exists(STUDENTS_FILE):
        with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_students(students):
    """Sla studenten op naar JSON bestand"""
    ensure_data_dir()
    with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(students, f, indent=2, ensure_ascii=False)

def load_tournament():
    """Laad toernooi data uit JSON bestand"""
    ensure_data_dir()
    if os.path.exists(TOURNAMENT_FILE):
        with open(TOURNAMENT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'races': [],
        'participants': [],
        'points_system': [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]  # F1 punten systeem
    }

def save_tournament(tournament):
    """Sla toernooi data op naar JSON bestand"""
    ensure_data_dir()
    with open(TOURNAMENT_FILE, 'w', encoding='utf-8') as f:
        json.dump(tournament, f, indent=2, ensure_ascii=False)


# ==================== HOOFDFUNCTIES ====================

def toon_alle_data():
    """
    Toon alle data: Actieve sessie info + geregistreerde studenten + toernooi status
    """
    print("\n📊 SCHERM 2 - INVOER & TOERNOOI BEHEER")
    print("=" * 80)
    print("Druk op ENTER om te stoppen\n")
    
    # Laad opgeslagen data
    students = load_students()
    tournament = load_tournament()
    
    print("👥 GEREGISTREERDE STUDENTEN:")
    if students:
        for sim, student in students.items():
            print(f"   {sim}: {student['name']} (geregistreerd: {student['timestamp']})")
    else:
        print("   (Nog geen studenten geregistreerd)")
    
    print(f"\n🏆 TOERNOOI STATUS:")
    print(f"   Aantal races: {len(tournament['races'])}")
    print(f"   Deelnemers: {len(tournament['participants'])}")
    print()
    
    # Live sessie info
    def handle_session(packet: SessionPacket):
        print(f"\n📍 ACTIEVE SESSIE:")
        print(f"   Type:        {packet.get_session_type_name()}")
        print(f"   Circuit:     {packet.get_track_name()}")
        print(f"   Totaal laps: {packet.total_laps}")
        print(f"   Tijd over:   {packet.session_time_left}s")
        print(f"   Weer:        {packet.get_weather_name()}")
        print(f"   Track temp:  {packet.track_temperature}°C")
        print()
    
    def handle_participants(packet: ParticipantsPacket):
        print(f"\n🎮 ACTIEVE DEELNEMERS IN GAME ({packet.num_active_cars}):")
        for i in range(min(packet.num_active_cars, 10)):  # Max 10 tonen
            if i < len(packet.participants):
                p = packet.participants[i]
                status = "👤" if not p.ai_controlled else "🤖"
                print(f"   {status} #{p.race_number:2d} {p.name}")
        print()
    
    def handle_event(packet: EventPacket):
        event_code = packet.event_string_code
        
        if event_code == "SSTA":  # Session Started
            print(f"\n▶️  SESSIE GESTART!\n")
        elif event_code == "SEND":  # Session Ended
            print(f"\n⏹️  SESSIE BEËINDIGD!\n")
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.SESSION, handle_session)
    listener.register_handler(PacketID.PARTICIPANTS, handle_participants)
    listener.register_handler(PacketID.EVENT, handle_event)
    
    set_active_listener(listener)
    
    try:
        listener.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if "10048" not in str(e):
            print(f"\n❌ Fout: {e}")


def student_registratie():
    """
    Student registratie: Naam invoeren en koppelen aan simulator
    """
    print("\n👤 STUDENT REGISTRATIE")
    print("=" * 80)
    
    students = load_students()
    
    # Toon huidige registraties
    print("\nHuidige registraties:")
    if students:
        for sim, student in students.items():
            print(f"   {sim}: {student['name']}")
    else:
        print("   (Nog geen studenten geregistreerd)")
    
    print("\n" + "-" * 80)
    
    # Kies simulator
    print("\nKies simulator:")
    print("  1. Simulator 1")
    print("  2. Simulator 2")
    print("  0. Annuleren")
    
    sim_choice = input("\n➤ Keuze: ").strip()
    
    if sim_choice == "0":
        return
    elif sim_choice not in ["1", "2"]:
        print("\n❌ Ongeldige keuze!")
        input("\nDruk op ENTER om terug te gaan...")
        return
    
    sim_name = f"Simulator {sim_choice}"
    
    # Vraag naam
    print(f"\nRegistratie voor {sim_name}")
    student_name = input("Voer studentnaam in: ").strip()
    
    if not student_name:
        print("\n❌ Naam mag niet leeg zijn!")
        input("\nDruk op ENTER om terug te gaan...")
        return
    
    # Opslaan
    students[sim_name] = {
        'name': student_name,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    save_students(students)
    
    print(f"\n✓ Student '{student_name}' geregistreerd voor {sim_name}!")
    input("\nDruk op ENTER om terug te gaan...")


def simulator_selectie():
    """
    Simulator selectie: Toon welke student op welke simulator zit
    """
    print("\n🎮 SIMULATOR SELECTIE")
    print("=" * 80)
    
    students = load_students()
    
    print("\nActieve toewijzingen:")
    print("-" * 80)
    
    if students:
        for sim in ["Simulator 1", "Simulator 2"]:
            if sim in students:
                print(f"   {sim}: {students[sim]['name']}")
            else:
                print(f"   {sim}: (Niet toegewezen)")
    else:
        print("   (Nog geen studenten geregistreerd)")
    
    print("\n" + "=" * 80)
    print("\nActies:")
    print("  1. Student verwijderen van simulator")
    print("  0. Terug")
    
    choice = input("\n➤ Keuze: ").strip()
    
    if choice == "1":
        print("\nKies simulator om te wissen:")
        print("  1. Simulator 1")
        print("  2. Simulator 2")
        
        sim_choice = input("\n➤ Keuze: ").strip()
        
        if sim_choice in ["1", "2"]:
            sim_name = f"Simulator {sim_choice}"
            if sim_name in students:
                del students[sim_name]
                save_students(students)
                print(f"\n✓ {sim_name} gewist!")
            else:
                print(f"\n⚠️  {sim_name} was niet toegewezen")
        
        input("\nDruk op ENTER om terug te gaan...")


def sessie_beheer():
    """
    Sessie beheer: Toon live sessie status
    (Start/stop gebeurt in de game zelf)
    """
    print("\n▶️  SESSIE BEHEER")
    print("=" * 80)
    print("Druk op ENTER om te stoppen\n")
    
    print("⚠️  Let op: Sessies starten/stoppen gebeurt in F1 25 zelf")
    print("Dit scherm toont live de sessie status\n")
    
    session_active = False
    
    def handle_session(packet: SessionPacket):
        print(f"\r📍 Sessie: {packet.get_session_type_name()} @ {packet.get_track_name()} | "
              f"Tijd over: {packet.session_time_left}s", end='', flush=True)
    
    def handle_event(packet: EventPacket):
        nonlocal session_active
        event_code = packet.event_string_code
        
        if event_code == "SSTA":  # Session Started
            session_active = True
            print(f"\n\n▶️  SESSIE GESTART!\n")
        elif event_code == "SEND":  # Session Ended
            session_active = False
            print(f"\n\n⏹️  SESSIE BEËINDIGD!\n")
        elif event_code == "CHQF":  # Chequered Flag
            print(f"\n\n🏁 CHEQUERED FLAG!\n")
    
    listener = F1TelemetryListener()
    listener.register_handler(PacketID.SESSION, handle_session)
    listener.register_handler(PacketID.EVENT, handle_event)
    
    set_active_listener(listener)
    
    try:
        listener.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if "10048" not in str(e):
            print(f"\n❌ Fout: {e}")


def toernooi_race_toevoegen():
    """
    Toernooi setup: Race toevoegen aan toernooi
    """
    print("\n➕ RACE TOEVOEGEN AAN TOERNOOI")
    print("=" * 80)
    
    tournament = load_tournament()
    
    print("\nNieuwe race toevoegen:")
    
    race_name = input("Race naam (bijv. 'Race 1 - Monaco'): ").strip()
    if not race_name:
        print("\n❌ Race naam mag niet leeg zijn!")
        input("\nDruk op ENTER om terug te gaan...")
        return
    
    circuit = input("Circuit naam: ").strip()
    date = datetime.now().strftime("%Y-%m-%d")
    
    race = {
        'id': len(tournament['races']) + 1,
        'name': race_name,
        'circuit': circuit,
        'date': date,
        'results': []
    }
    
    tournament['races'].append(race)
    save_tournament(tournament)
    
    print(f"\n✓ Race '{race_name}' toegevoegd aan toernooi!")
    print(f"   Circuit: {circuit}")
    print(f"   Datum: {date}")
    
    input("\nDruk op ENTER om terug te gaan...")


def toernooi_circuit_selectie():
    """
    Toernooi setup: Toon beschikbare circuits
    """
    print("\n🏁 CIRCUIT SELECTIE")
    print("=" * 80)
    
    circuits = [
        "Bahrain", "Saudi Arabia", "Australia", "Japan", "China",
        "Miami", "Imola", "Monaco", "Canada", "Spain",
        "Austria", "Great Britain", "Hungary", "Belgium", "Netherlands",
        "Italy", "Azerbaijan", "Singapore", "USA", "Mexico",
        "Brazil", "Las Vegas", "Qatar", "Abu Dhabi"
    ]
    
    print("\nBeschikbare F1 circuits:")
    print("-" * 80)
    
    for i, circuit in enumerate(circuits, 1):
        print(f"   {i:2d}. {circuit}")
    
    print("\n" + "=" * 80)
    input("\nDruk op ENTER om terug te gaan...")


def toernooi_deelnemers():
    """
    Toernooi setup: Deelnemers beheren
    """
    print("\n👥 TOERNOOI DEELNEMERS BEHEER")
    print("=" * 80)
    
    tournament = load_tournament()
    students = load_students()
    
    print("\nHuidige deelnemers:")
    if tournament['participants']:
        for i, participant in enumerate(tournament['participants'], 1):
            print(f"   {i}. {participant}")
    else:
        print("   (Nog geen deelnemers)")
    
    print("\n" + "-" * 80)
    print("\nActies:")
    print("  1. Deelnemer toevoegen")
    print("  2. Deelnemer verwijderen")
    print("  0. Terug")
    
    choice = input("\n➤ Keuze: ").strip()
    
    if choice == "1":
        # Toon geregistreerde studenten
        print("\nGeregistreerde studenten:")
        student_list = [s['name'] for s in students.values()]
        
        if student_list:
            for i, name in enumerate(student_list, 1):
                print(f"   {i}. {name}")
            
            try:
                idx = int(input("\nSelecteer student (nummer): ").strip()) - 1
                if 0 <= idx < len(student_list):
                    name = student_list[idx]
                    if name not in tournament['participants']:
                        tournament['participants'].append(name)
                        save_tournament(tournament)
                        print(f"\n✓ {name} toegevoegd aan toernooi!")
                    else:
                        print(f"\n⚠️  {name} is al deelnemer!")
                else:
                    print("\n❌ Ongeldige keuze!")
            except ValueError:
                print("\n❌ Ongeldige invoer!")
        else:
            print("   (Nog geen studenten geregistreerd)")
        
        input("\nDruk op ENTER om terug te gaan...")
    
    elif choice == "2":
        if tournament['participants']:
            for i, participant in enumerate(tournament['participants'], 1):
                print(f"   {i}. {participant}")
            
            try:
                idx = int(input("\nSelecteer deelnemer om te verwijderen (nummer): ").strip()) - 1
                if 0 <= idx < len(tournament['participants']):
                    removed = tournament['participants'].pop(idx)
                    save_tournament(tournament)
                    print(f"\n✓ {removed} verwijderd uit toernooi!")
                else:
                    print("\n❌ Ongeldige keuze!")
            except ValueError:
                print("\n❌ Ongeldige invoer!")
        else:
            print("\n⚠️  Geen deelnemers om te verwijderen!")
        
        input("\nDruk op ENTER om terug te gaan...")


def toernooi_punten_configuratie():
    """
    Toernooi setup: Punten systeem configureren
    """
    print("\n🎯 PUNTEN SYSTEEM CONFIGURATIE")
    print("=" * 80)
    
    tournament = load_tournament()
    
    print("\nHuidig punten systeem:")
    print("Positie -> Punten")
    print("-" * 40)
    for i, points in enumerate(tournament['points_system'], 1):
        print(f"   P{i:2d} -> {points:2d} punten")
    
    print("\n" + "=" * 80)
    print("\nBeschikbare systemen:")
    print("  1. F1 Standaard (25, 18, 15, 12, 10, 8, 6, 4, 2, 1)")
    print("  2. Aangepast systeem (zelf invoeren)")
    print("  0. Terug")
    
    choice = input("\n➤ Keuze: ").strip()
    
    if choice == "1":
        tournament['points_system'] = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
        save_tournament(tournament)
        print("\n✓ F1 Standaard punten systeem ingesteld!")
        input("\nDruk op ENTER om terug te gaan...")
    
    elif choice == "2":
        print("\n⚠️  Aangepast punten systeem - Nog niet geïmplementeerd")
        input("\nDruk op ENTER om terug te gaan...")