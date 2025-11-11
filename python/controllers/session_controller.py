"""
F1 25 Telemetry System - Session Controller
Controller voor sessie lifecycle management
(Versie 9.4: Correctie AttributeError 'game_version' -> 'packet_version')
"""

from typing import Optional, Dict, Any
from models import SessionModel, DriverModel, LapModel
from services import logger_service

# --- AANGEPAST: Imports uitgebreid ---
from packet_parsers import SessionData

# We hebben de Header nodig voor de UID
try:
    from packet_parsers.packet_header import PacketHeader
except ImportError:
    print("[FATAL ERROR] SessionController kon PacketHeader niet importeren.")


    class PacketHeader:
        pass


# --- EINDE AANPASSING ---


class SessionController:
    """
    Controller voor sessie management
    Beheert sessie lifecycle en state
    """

    def __init__(self):
        """Initialiseer session controller"""
        self.logger = logger_service.get_logger('SessionController')

        self.session_model = SessionModel()
        self.driver_model = DriverModel()
        self.lap_model = LapModel()

        self.current_session_uid: Optional[int] = None
        self.current_session_id: Optional[int] = None
        self.session_active = False

        self.logger.info("Session controller geïnitialiseerd")

    # --- NIEUWE METHODE (STAP 7) ---
    def process_session_packet(self, packet: SessionData, header: PacketHeader):
        """
        Entry point voor de DataProcessor (verwerkt Packet 1).
        Bepaalt of een sessie gestart of geüpdatet moet worden.
        """
        new_uid = header.session_uid

        if not new_uid or new_uid == 0:
            self.logger.debug("Sessie-pakket (P1) met UID 0 ontvangen, genegeerd.")
            return

        # Check of de UID nieuw is
        if new_uid != self.current_session_uid:
            # Dit is een nieuwe sessie, of we starten de app
            # midden in een bestaande sessie.
            self.logger.info(f"Nieuwe/actieve sessie-UID gedetecteerd: {new_uid}")
            # start_session() handelt zowel 'create' als 'get existing' af
            self.start_session(new_uid, packet)

        # Check of de sessie wel actief is
        elif self.session_active:
            # Dit is een update-pakket (bv. weer) voor de reeds actieve sessie
            self.logger.debug(f"Update voor actieve sessie {new_uid}")
            self.update_session(packet)

        else:
            # UID is hetzelfde, maar sessie is niet 'actief'.
            # Dit kan gebeuren als start_session() faalt.
            self.logger.warning(f"Sessie-update (P1) ontvangen voor {new_uid}, maar sessie staat niet als 'actief'.")

    # --- EINDE NIEUWE METHODE ---

    def start_session(self, session_uid: int, session_data: SessionData) -> Optional[int]:
        """
        Start nieuwe sessie of heractiveer bestaande

        Args:
            session_uid: Unieke sessie identifier
            session_data: Session packet data

        Returns:
            Session ID (int) or None if failed
        """
        # Check of sessie al bestaat
        existing = self.session_model.get_session_by_uid(session_uid)

        if existing:
            self.logger.info(f"Bestaande sessie heractiveerd: ID {existing['id']} (UID {session_uid})")
            self.current_session_id = existing['id']
            self.current_session_uid = session_uid
            self.session_active = True
            return existing['id']

        # Maak nieuwe sessie
        session_dict = {
            'session_uid': session_uid,
            'track_id': session_data.track_id,
            'session_type': session_data.session_type,
            'weather': session_data.weather,
            'track_temperature': session_data.track_temperature,
            'air_temperature': session_data.air_temperature,
            'total_laps': session_data.total_laps,
            'session_duration': getattr(session_data, 'session_duration', 0)
        }

        # We gaan ervan uit dat session_model.create_session de ID retourneert
        session_id = self.session_model.create_session(session_dict)

        if session_id:
            self.current_session_id = session_id
            self.current_session_uid = session_uid
            self.session_active = True
            self.logger.info(
                f"Nieuwe sessie gestart: ID {session_id}, "
                f"UID {session_uid}, Track {session_data.track_id}"
            )
        else:
            self.logger.error(f"Kon sessie niet aanmaken voor UID {session_uid}")
            return None

        return session_id

    def update_session(self, session_data: SessionData):
        """
        Update huidige sessie informatie

        Args:
            session_data: Session packet data
        """
        if not self.current_session_id:
            self.logger.warning("Geen actieve sessie om te updaten")
            return

        updates = {
            'weather': session_data.weather,
            'track_temperature': session_data.track_temperature,
            'air_temperature': session_data.air_temperature
        }

        self.session_model.update_session(self.current_session_id, updates)

    def end_session(self):
        """Beëindig huidige sessie"""
        if not self.current_session_id:
            self.logger.warning("Geen actieve sessie om te beëindigen")
            return

        self.session_model.end_session(self.current_session_id)
        self.logger.info(f"Sessie beëindigd: ID {self.current_session_id}")
        self.session_active = False
        self.current_session_id = None
        self.current_session_uid = None

    def get_session_id(self) -> Optional[int]:
        """
        Verkrijg huidige session ID

        Returns:
            Session ID of None
        """
        return self.current_session_id

    def is_session_active(self) -> bool:
        """
        Check of er een actieve sessie is

        Returns:
            True als sessie actief is
        """
        return self.session_active

    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """
        Verkrijg informatie over huidige sessie

        Returns:
            Session dict of None
        """
        if not self.current_session_uid:
            return None
        return self.session_model.get_session_by_uid(self.current_session_uid)

    def get_session_statistics(self) -> Dict[str, Any]:
        """
        Verkrijg statistieken van huidige sessie

        Returns:
            Dict met statistieken
        """
        if not self.current_session_id:
            return {
                'active': False,
                'total_drivers': 0,
                'total_laps': 0
            }

        leaderboard = self.lap_model.get_session_leaderboard(self.current_session_id)
        total_laps = 0
        for entry in leaderboard:
            lap_count = self.lap_model.get_lap_count(
                self.current_session_id,
                entry['car_index']
            )
            total_laps += lap_count

        return {
            'active': self.session_active,
            'session_id': self.current_session_id,
            'total_drivers': len(leaderboard),
            'total_laps': total_laps,
            'fastest_lap': leaderboard[0] if leaderboard else None
        }

    # --- AANPASSING V9.2: NIEUWE METHODE ---
    # --- AANPASSING V9.4: FIX ATTRIBUTEERROR ---
    def create_placeholder_session(self, header: PacketHeader) -> Optional[int]:
        """
        Aangeroepen door TelemetryController (vanuit P11) als P1 blijkbaar
        heeft gefaald. Maakt een 'placeholder' sessie aan.

        Retourneert de nieuwe database 'id' (PK) van de sessie.
        """
        session_uid = header.session_uid
        if not session_uid or session_uid == 0:
            self.logger.warning("create_placeholder_session: Header (P11) bevat geen geldige session_uid.")
            return None

        # Controleer EERST of hij niet al bestaat (race condition)
        existing = self.session_model.get_session_by_uid(session_uid)
        if existing:
            self.logger.info(
                f"create_placeholder_session: Sessie {session_uid} bestond al (race condition opgelost). ID: {existing.get('id')}")
            return existing.get('id')

        self.logger.info(f"create_placeholder_session: P1-parser falen gedetecteerd. "
                         f"Placeholder sessie wordt aangemaakt voor UID {session_uid}")

        # Maak een minimaal data-object.
        session_data = {
            'session_uid': session_uid,
            'track_id': -1,  # Onbekend
            'session_type': 0,  # Onbekend
            'weather': 0,
            'track_temperature': 0,
            'air_temperature': 0,
            'total_laps': 0,
            'session_duration': 0,
            'packet_format': header.packet_format,

            # --- FIX V9.4 ---
            # De log (en jouw class) zegt dat het 'packet_version' is,
            # niet 'game_version'.
            'game_version': str(header.packet_version)
            # --- EINDE FIX V9.4 ---
        }

        try:
            # Probeer de sessie aan te maken
            db_session_id = self.session_model.create_session(session_data)

            if db_session_id:
                self.logger.info(
                    f"Placeholder sessie succesvol aangemaakt met DB ID {db_session_id} voor UID {session_uid}")
                return db_session_id
            else:
                self.logger.error(f"session_model.create_session retourneerde geen ID voor UID {session_uid}")
                return None

        except Exception as e:
            if 'Duplicate' in str(e) or 'UNIQUE' in str(e):
                self.logger.warning(
                    f"Race condition in create_placeholder_session: Sessie {session_uid} bestaat al. Opnieuw proberen op te halen.")
                existing_session = self.session_model.get_session_by_uid(session_uid)
                if existing_session:
                    return existing_session.get('id')

            self.logger.error(f"Onverwachte DB-fout bij aanmaken placeholder sessie voor UID {session_uid}: {e}",
                              exc_info=True)
            return None

    # --- EINDE METHODE ---

    def cleanup_session_data(self):
        """Ruim oude sessie data op"""
        pass