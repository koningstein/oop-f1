"""
Database configuratie manager voor F1 25 Telemetry project
Centraal punt voor alle database instellingen en verbindingen
"""

import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling
from mysql.connector.errors import Error as MySQLError

class DatabaseConfig:
    """
    Centraal configuratie punt voor database instellingen
    """
    
    def __init__(self, env_file: str = ".env"):
        """
        Initialiseer database configuratie
        
        Args:
            env_file: Pad naar .env bestand (relatief of absoluut)
        """
        self.logger = logging.getLogger(__name__)
        
        # Laad environment variabelen
        if not os.path.isabs(env_file):
            # Als het een relatief pad is, zoek vanaf de directory van dit script
            env_file = os.path.join(os.path.dirname(__file__), env_file)
        
        load_dotenv(env_file)
        
        # Database configuratie uit environment
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '3306'))
        self.database = os.getenv('DB_NAME', 'f1_telemetry')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.charset = os.getenv('DB_CHARSET', 'utf8mb4')
        self.collation = os.getenv('DB_COLLATION', 'utf8mb4_unicode_ci')
        
        # Debug modus
        self.debug = os.getenv('DEBUG', 'False').lower() == 'true'
        
        # Connection pool configuratie
        self.pool_name = "f1_telemetry_pool"
        self.pool_size = 5
        self.pool_reset_session = True
        
        # Connection pool
        self._connection_pool: Optional[pooling.MySQLConnectionPool] = None
        
        self.logger.info(f"Database configuratie geladen - Host: {self.host}, Database: {self.database}")
    
    def get_connection_config(self) -> Dict[str, Any]:
        """
        Krijg database connection configuratie als dictionary
        
        Returns:
            Dictionary met connection parameters
        """
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'password': self.password,
            'charset': self.charset,
            'collation': self.collation,
            'autocommit': True,
            'raise_on_warnings': True
        }
    
    def create_connection_pool(self) -> pooling.MySQLConnectionPool:
        """
        Maak een connection pool voor hergebruik van database verbindingen
        
        Returns:
            MySQL connection pool
            
        Raises:
            MySQLError: Bij database verbindingsproblemen
        """
        if self._connection_pool is not None:
            return self._connection_pool
        
        try:
            config = self.get_connection_config()
            config.update({
                'pool_name': self.pool_name,
                'pool_size': self.pool_size,
                'pool_reset_session': self.pool_reset_session
            })
            
            self._connection_pool = pooling.MySQLConnectionPool(**config)
            self.logger.info(f"Database connection pool aangemaakt met {self.pool_size} verbindingen")
            
            return self._connection_pool
            
        except MySQLError as e:
            self.logger.error(f"Fout bij aanmaken connection pool: {e}")
            raise
    
    def get_connection(self) -> mysql.connector.MySQLConnection:
        """
        Krijg een database verbinding uit de pool
        
        Returns:
            MySQL database verbinding
            
        Raises:
            MySQLError: Bij verbindingsproblemen
        """
        try:
            if self._connection_pool is None:
                self.create_connection_pool()
            
            connection = self._connection_pool.get_connection()
            
            if self.debug:
                self.logger.debug("Database verbinding uit pool gehaald")
            
            return connection
            
        except MySQLError as e:
            self.logger.error(f"Fout bij ophalen database verbinding: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test de database verbinding
        
        Returns:
            True als verbinding succesvol is, False anders
        """
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            
            success = result is not None
            self.logger.info(f"Database verbinding test: {'Succesvol' if success else 'Gefaald'}")
            return success
            
        except Exception as e:
            self.logger.error(f"Database verbinding test gefaald: {e}")
            return False
    
    def close_pool(self):
        """Sluit de connection pool"""
        if self._connection_pool is not None:
            self._connection_pool.close()
            self._connection_pool = None
            self.logger.info("Database connection pool gesloten")


# Globale database configuratie instantie
# Dit zorgt ervoor dat de configuratie overal in de applicatie gebruikt kan worden
db_config = DatabaseConfig()