"""
Database Manager voor F1 25 Telemetry project
Beheert alle database operaties voor rondetijden en telemetry data
"""

import logging
import traceback
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from mysql.connector.errors import Error as MySQLError
from database_config import db_config

class LapTimeDatabase:
    """
    Database manager voor lap times en telemetry data
    """
    
    def __init__(self):
        """Initialiseer database manager"""
        self.logger = logging.getLogger(__name__)
        self.config = db_config
        
        # Test database verbinding bij opstarten
        if self.config.test_connection():
            self.logger.info("LapTimeDatabase geïnitialiseerd - Database verbinding OK")
        else:
            self.logger.warning("LapTimeDatabase geïnitialiseerd - Database verbinding probleem")
    
    def save_lap_time(self, 
                     driver_name: str,
                     lap_time: float,
                     track_name: str,
                     sector1_time: Optional[float] = None,
                     sector2_time: Optional[float] = None,
                     sector3_time: Optional[float] = None,
                     is_valid: bool = True,
                     session_date: Optional[datetime] = None) -> Optional[int]:
        """
        Sla een rondetijd op in de database
        
        Args:
            driver_name: Naam van de bestuurder
            lap_time: Rondetijd in seconden (float)
            track_name: Naam van het circuit
            sector1_time: Sector 1 tijd in seconden (optioneel)
            sector2_time: Sector 2 tijd in seconden (optioneel) 
            sector3_time: Sector 3 tijd in seconden (optioneel)
            is_valid: Of de rondetijd geldig is (default: True)
            session_date: Datum/tijd van de sessie (default: nu)
        
        Returns:
            ID van de opgeslagen record, of None bij fout
        """
        if session_date is None:
            session_date = datetime.now()
        
        connection = None
        cursor = None
        
        try:
            connection = self.config.get_connection()
            cursor = connection.cursor()
            
            # SQL query voor het invoegen van lap time data
            query = """
                INSERT INTO lap_times 
                (driver_name, lap_time, track_name, sector1_time, sector2_time, sector3_time, is_valid, session_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                driver_name,
                lap_time,
                track_name,
                sector1_time,
                sector2_time, 
                sector3_time,
                is_valid,
                session_date
            )
            
            cursor.execute(query, values)
            connection.commit()
            
            # Krijg het ID van het zojuist ingevoegde record
            lap_id = cursor.lastrowid
            
            self.logger.info(f"Rondetijd opgeslagen - Driver: {driver_name}, Tijd: {lap_time:.3f}s, Track: {track_name}, ID: {lap_id}")
            
            return lap_id
            
        except MySQLError as e:
            self.logger.error(f"Database fout bij opslaan rondetijd: {e}")
            if connection:
                connection.rollback()
            return None
            
        except Exception as e:
            self.logger.error(f"Onverwachte fout bij opslaan rondetijd: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            if connection:
                connection.rollback()
            return None
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def get_best_lap_time(self, track_name: str, driver_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Krijg de beste rondetijd voor een circuit (en optioneel een specifieke bestuurder)
        
        Args:
            track_name: Naam van het circuit
            driver_name: Naam van de bestuurder (optioneel)
        
        Returns:
            Dictionary met beste rondetijd info, of None als niet gevonden
        """
        connection = None
        cursor = None
        
        try:
            connection = self.config.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            if driver_name:
                query = """
                    SELECT * FROM lap_times 
                    WHERE track_name = %s AND driver_name = %s AND is_valid = 1
                    ORDER BY lap_time ASC 
                    LIMIT 1
                """
                values = (track_name, driver_name)
            else:
                query = """
                    SELECT * FROM lap_times 
                    WHERE track_name = %s AND is_valid = 1
                    ORDER BY lap_time ASC 
                    LIMIT 1
                """
                values = (track_name,)
            
            cursor.execute(query, values)
            result = cursor.fetchone()
            
            if result:
                self.logger.debug(f"Beste rondetijd gevonden - Track: {track_name}, Driver: {result['driver_name']}, Tijd: {result['lap_time']}")
            
            return result
            
        except MySQLError as e:
            self.logger.error(f"Database fout bij ophalen beste rondetijd: {e}")
            return None
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def get_lap_times_for_driver(self, driver_name: str, track_name: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Krijg rondetijden voor een specifieke bestuurder
        
        Args:
            driver_name: Naam van de bestuurder
            track_name: Filter op circuit naam (optioneel)
            limit: Maximum aantal resultaten (default: 50)
        
        Returns:
            Lijst met rondetijd records
        """
        connection = None
        cursor = None
        
        try:
            connection = self.config.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            if track_name:
                query = """
                    SELECT * FROM lap_times 
                    WHERE driver_name = %s AND track_name = %s AND is_valid = 1
                    ORDER BY session_date DESC, lap_time ASC
                    LIMIT %s
                """
                values = (driver_name, track_name, limit)
            else:
                query = """
                    SELECT * FROM lap_times 
                    WHERE driver_name = %s AND is_valid = 1
                    ORDER BY session_date DESC, lap_time ASC
                    LIMIT %s
                """
                values = (driver_name, limit)
            
            cursor.execute(query, values)
            results = cursor.fetchall()
            
            self.logger.debug(f"Gevonden {len(results)} rondetijden voor bestuurder {driver_name}")
            
            return results
            
        except MySQLError as e:
            self.logger.error(f"Database fout bij ophalen rondetijden voor bestuurder: {e}")
            return []
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def get_leaderboard(self, track_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Krijg leaderboard voor een circuit (beste tijd per bestuurder)
        
        Args:
            track_name: Naam van het circuit
            limit: Maximum aantal resultaten (default: 20)
        
        Returns:
            Lijst met beste tijden per bestuurder, gesorteerd op tijd
        """
        connection = None
        cursor = None
        
        try:
            connection = self.config.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    driver_name,
                    MIN(lap_time) as best_lap_time,
                    COUNT(*) as total_laps,
                    MAX(session_date) as last_session,
                    AVG(lap_time) as average_lap_time
                FROM lap_times 
                WHERE track_name = %s AND is_valid = 1
                GROUP BY driver_name
                ORDER BY best_lap_time ASC
                LIMIT %s
            """
            values = (track_name, limit)
            
            cursor.execute(query, values)
            results = cursor.fetchall()
            
            self.logger.debug(f"Leaderboard opgehaald voor {track_name} - {len(results)} bestuurders")
            
            return results
            
        except MySQLError as e:
            self.logger.error(f"Database fout bij ophalen leaderboard: {e}")
            return []
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def get_recent_sessions(self, hours: int = 24, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Krijg recente sessies/rondetijden
        
        Args:
            hours: Aantal uren terug om te zoeken (default: 24)
            limit: Maximum aantal resultaten (default: 100)
        
        Returns:
            Lijst met recente rondetijd records
        """
        connection = None
        cursor = None
        
        try:
            connection = self.config.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT * FROM lap_times 
                WHERE session_date >= DATE_SUB(NOW(), INTERVAL %s HOUR)
                ORDER BY session_date DESC
                LIMIT %s
            """
            values = (hours, limit)
            
            cursor.execute(query, values)
            results = cursor.fetchall()
            
            self.logger.debug(f"Gevonden {len(results)} recente sessies (laatste {hours} uur)")
            
            return results
            
        except MySQLError as e:
            self.logger.error(f"Database fout bij ophalen recente sessies: {e}")
            return []
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def delete_invalid_laps(self, track_name: Optional[str] = None) -> int:
        """
        Verwijder ongeldige rondetijden uit de database
        
        Args:
            track_name: Filter op circuit naam (optioneel)
        
        Returns:
            Aantal verwijderde records
        """
        connection = None
        cursor = None
        
        try:
            connection = self.config.get_connection()
            cursor = connection.cursor()
            
            if track_name:
                query = "DELETE FROM lap_times WHERE is_valid = 0 AND track_name = %s"
                values = (track_name,)
            else:
                query = "DELETE FROM lap_times WHERE is_valid = 0"
                values = ()
            
            cursor.execute(query, values)
            deleted_count = cursor.rowcount
            connection.commit()
            
            self.logger.info(f"Verwijderd {deleted_count} ongeldige rondetijden")
            
            return deleted_count
            
        except MySQLError as e:
            self.logger.error(f"Database fout bij verwijderen ongeldige rondetijden: {e}")
            return 0
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


# Globale database instantie voor gebruik in de hele applicatie
lap_db = LapTimeDatabase()