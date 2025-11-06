"""
F1 25 Telemetry System - Database Model
Database connectie en basis operaties
"""

import mysql.connector
from mysql.connector import Error, pooling
from typing import Optional, List, Dict, Any
from config import DATABASE
from services import logger_service

class Database:
    """
    Database connectie manager met connection pooling
    """
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialiseer database connectie pool"""
        if self._initialized:
            return
            
        self._initialized = True
        self.logger = logger_service.get_logger('Database')
        self._create_pool()
        self._initialize_tables()
    
    def _create_pool(self):
        """Maak connection pool aan"""
        try:
            self._pool = pooling.MySQLConnectionPool(
                pool_name="telemetry_pool",
                pool_size=5,
                pool_reset_session=True,
                **DATABASE
            )
            self.logger.info("Database connection pool aangemaakt")
        except Error as e:
            self.logger.error(f"Fout bij aanmaken connection pool: {e}")
            raise
    
    def get_connection(self):
        """Verkrijg connectie uit pool"""
        try:
            return self._pool.get_connection()
        except Error as e:
            self.logger.error(f"Fout bij ophalen connectie: {e}")
            raise
    
    def _initialize_tables(self):
        """Maak benodigde tabellen aan als ze niet bestaan"""
        tables = {
            'sessions': """
                CREATE TABLE IF NOT EXISTS sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_uid BIGINT UNSIGNED UNIQUE NOT NULL,
                    track_id TINYINT UNSIGNED,
                    session_type TINYINT UNSIGNED,
                    weather TINYINT UNSIGNED,
                    track_temperature TINYINT,
                    air_temperature TINYINT,
                    total_laps TINYINT UNSIGNED,
                    session_duration INT UNSIGNED,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ended_at TIMESTAMP NULL,
                    INDEX idx_session_uid (session_uid),
                    INDEX idx_started_at (started_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,
            'drivers': """
                CREATE TABLE IF NOT EXISTS drivers (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id INT NOT NULL,
                    car_index TINYINT UNSIGNED NOT NULL,
                    driver_name VARCHAR(50),
                    team_id TINYINT UNSIGNED,
                    race_number TINYINT UNSIGNED,
                    nationality TINYINT UNSIGNED,
                    is_player BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_driver (session_id, car_index),
                    INDEX idx_session_car (session_id, car_index)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,
            'laps': """
                CREATE TABLE IF NOT EXISTS laps (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id INT NOT NULL,
                    car_index TINYINT UNSIGNED NOT NULL,
                    lap_number TINYINT UNSIGNED NOT NULL,
                    lap_time_ms INT UNSIGNED,
                    sector1_ms INT UNSIGNED,
                    sector2_ms INT UNSIGNED,
                    sector3_ms INT UNSIGNED,
                    sector1_valid BOOLEAN DEFAULT TRUE,
                    sector2_valid BOOLEAN DEFAULT TRUE,
                    sector3_valid BOOLEAN DEFAULT TRUE,
                    is_valid BOOLEAN DEFAULT TRUE,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
                    INDEX idx_session_car_lap (session_id, car_index, lap_number),
                    INDEX idx_session_valid (session_id, is_valid)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,
            'telemetry_live': """
                CREATE TABLE IF NOT EXISTS telemetry_live (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    session_id INT NOT NULL,
                    car_index TINYINT UNSIGNED NOT NULL,
                    speed SMALLINT UNSIGNED,
                    throttle FLOAT,
                    brake FLOAT,
                    gear TINYINT,
                    rpm SMALLINT UNSIGNED,
                    drs BOOLEAN,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
                    INDEX idx_session_car_time (session_id, car_index, recorded_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        }
        
        connection = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            for table_name, create_query in tables.items():
                cursor.execute(create_query)
                self.logger.info(f"Tabel '{table_name}' gecontroleerd/aangemaakt")
            
            connection.commit()
            cursor.close()
            
        except Error as e:
            self.logger.error(f"Fout bij initialiseren tabellen: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def execute_query(self, query: str, params: tuple = None) -> bool:
        """
        Voer INSERT/UPDATE/DELETE query uit
        
        Returns:
            bool: True als succesvol
        """
        connection = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params or ())
            connection.commit()
            cursor.close()
            return True
        except Error as e:
            self.logger.error(f"Query fout: {e}\nQuery: {query}")
            if connection:
                connection.rollback()
            return False
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Haal één rij op als dictionary"""
        connection = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            self.logger.error(f"Fetch fout: {e}")
            return None
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Haal alle rijen op als list van dictionaries"""
        connection = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            self.logger.error(f"Fetch fout: {e}")
            return []
        finally:
            if connection and connection.is_connected():
                connection.close()


# Singleton instance
database = Database()