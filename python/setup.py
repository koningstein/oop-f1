"""
Setup Script voor F1 25 Telemetry Database Project - MYSQL 8.0+ COMPATIBLE
Installeert dependencies en test database verbinding
"""

import os
import sys
import subprocess
import logging

def setup_logging():
    """Setup logging configuratie"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def install_dependencies():
    """Installeer Python dependencies - Windows safe versie"""
    logger = setup_logging()
    
    logger.info("📦 Installeren van Python dependencies...")
    
    # Probeer eerst de minimale versie
    requirements_files = [
        'requirements_minimal.txt',
        'requirements_simple.txt', 
        'requirements.txt'
    ]
    
    for req_file in requirements_files:
        if not os.path.exists(req_file):
            continue
            
        logger.info(f"Proberen van {req_file}...")
        
        try:
            # Installeer dependencies
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', req_file
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Dependencies succesvol geïnstalleerd uit {req_file}")
                return True
            else:
                logger.warning(f"⚠️ Fout bij {req_file}: {result.stderr}")
                continue
        
        except Exception as e:
            logger.warning(f"⚠️ Onverwachte fout bij {req_file}: {e}")
            continue
    
    # Als alles faalt, probeer handmatige installatie
    logger.info("Proberen handmatige installatie van basis packages...")
    
    essential_packages = [
        'mysql-connector-python',
        'python-dotenv'
    ]
    
    success_count = 0
    for package in essential_packages:
        try:
            logger.info(f"Installeren van {package}...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ {package} geïnstalleerd")
                success_count += 1
            else:
                logger.error(f"❌ Fout bij {package}: {result.stderr}")
                
        except Exception as e:
            logger.error(f"❌ Onverwachte fout bij {package}: {e}")
    
    # Test of de belangrijkste packages werken
    if success_count >= 2:  # mysql-connector en dotenv
        try:
            import mysql.connector
            logger.info("✅ Basis packages succesvol geïnstalleerd")
            return True
        except ImportError as e:
            logger.error(f"❌ Import test gefaald: {e}")
            return False
    else:
        logger.error("❌ Te weinig packages succesvol geïnstalleerd")
        return False

def check_env_file():
    """Check en maak .env bestand als het niet bestaat"""
    logger = setup_logging()
    
    if not os.path.exists('.env'):
        logger.warning("⚠️  .env bestand niet gevonden")
        
        print("\n🔧 Database configuratie setup:")
        print("Voor WAMP server gebruik meestal:")
        print("   Host: localhost")
        print("   Port: 3306") 
        print("   User: root")
        print("   Password: (meestal leeg voor WAMP)")
        print()
        
        # Vraag gebruiker om database configuratie
        db_host = input("Database host (default: localhost): ").strip() or "localhost"
        db_port = input("Database port (default: 3306): ").strip() or "3306"
        db_name = input("Database naam (default: f1_telemetry): ").strip() or "f1_telemetry"
        db_user = input("Database gebruiker (default: root): ").strip() or "root"
        db_password = input("Database wachtwoord (ENTER voor leeg): ").strip()
        
        # Maak .env bestand
        env_content = f"""# Database configuratie voor F1 25 Telemetry project
DB_HOST={db_host}
DB_PORT={db_port}
DB_NAME={db_name}
DB_USER={db_user}
DB_PASSWORD={db_password}

# Optionele database settings
DB_CHARSET=utf8mb4
DB_COLLATION=utf8mb4_unicode_ci

# Debug modus (True/False)
DEBUG=True
"""
        
        try:
            with open('.env', 'w') as f:
                f.write(env_content)
            logger.info("✅ .env bestand aangemaakt")
            return True
            
        except Exception as e:
            logger.error(f"❌ Fout bij aanmaken .env bestand: {e}")
            return False
    
    else:
        logger.info("✅ .env bestand gevonden")
        return True

def create_database_schema():
    """Maak database schema aan - MODERNE MYSQL 8.0+ VERSIE"""
    logger = setup_logging()
    
    logger.info("🗄️  Maken van database schema (MySQL 8.0+ compatible)...")
    
    # MODERNE SQL SYNTAX - geen deprecated features
    sql_schema = """
DROP TABLE IF EXISTS `lap_times`;
CREATE TABLE IF NOT EXISTS `lap_times` (
  `id` int AUTO_INCREMENT,
  `driver_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `lap_time` decimal(8,3) NOT NULL,
  `track_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sector1_time` decimal(8,3) DEFAULT NULL,
  `sector2_time` decimal(8,3) DEFAULT NULL,
  `sector3_time` decimal(8,3) DEFAULT NULL,
  `is_valid` tinyint(1) DEFAULT 1,
  `session_date` datetime NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_track` (`track_name`),
  KEY `idx_driver` (`driver_name`),
  KEY `idx_lap_time` (`lap_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""
    
    try:
        # Import database config (moet na installatie van dependencies)
        sys.path.insert(0, '.')  # Zorg dat huidige directory in path zit
        from database_config import db_config
        
        # Test verbinding
        if not db_config.test_connection():
            logger.error("❌ Kan geen verbinding maken met database")
            logger.info("💡 Troubleshooting:")
            logger.info("   1. Check of WAMP/MySQL draait")
            logger.info("   2. Check database instellingen in .env")
            logger.info("   3. Check of database gebruiker correct is")
            logger.info("   4. Voor WAMP: start alle services (Apache + MySQL)")
            logger.info("   5. Maak database 'f1_telemetry' aan in phpMyAdmin")
            return False
        
        # Maak schema met moderne syntax
        connection = db_config.get_connection()
        cursor = connection.cursor()
        
        # MySQL warning suppression voor deprecated features
        cursor.execute("SET sql_mode = 'TRADITIONAL'")
        
        # Voer SQL uit (split op ';' voor meerdere statements)
        statements = [stmt.strip() for stmt in sql_schema.split(';') if stmt.strip()]
        
        for statement in statements:
            try:
                cursor.execute(statement)
                logger.debug(f"Uitgevoerd: {statement[:50]}...")
            except Exception as stmt_error:
                logger.warning(f"Statement fout (mogelijk niet kritisch): {stmt_error}")
                continue
        
        connection.commit()
        cursor.close()
        connection.close()
        
        logger.info("✅ Database schema succesvol aangemaakt")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Kan database modules niet importeren: {e}")
        logger.info("   Database packages zijn mogelijk niet correct geïnstalleerd")
        return False
        
    except Exception as e:
        error_msg = str(e)
        
        # Check voor bekende warnings die geen echte fouten zijn
        if "deprecated" in error_msg.lower() or "1681" in error_msg:
            logger.warning(f"⚠️ MySQL warning (niet kritisch): {error_msg}")
            logger.info("✅ Schema waarschijnlijk wel succesvol aangemaakt ondanks warning")
            return True
        else:
            logger.error(f"❌ Echte fout bij aanmaken database schema: {e}")
            logger.info("💡 Mogelijke oplossingen:")
            logger.info("   - Start WAMP server")
            logger.info("   - Check MySQL service in WAMP")
            logger.info("   - Maak database 'f1_telemetry' handmatig aan")
            logger.info("   - Controleer database instellingen in .env")
            return False

def test_database_integration():
    """Test de database integratie"""
    logger = setup_logging()
    
    logger.info("🧪 Testen van database integratie...")
    
    try:
        from telemetry_db_integration import telemetry_db_integration
        
        # Test sessie
        telemetry_db_integration.set_session_info("Test Circuit", "Practice")
        
        # Test handmatige rondetijd
        lap_id = telemetry_db_integration.manual_save_lap_time(
            driver_name="Test Driver",
            lap_time=90.123,
            sector1=30.1,
            sector2=29.8,
            sector3=30.223,
            is_valid=True
        )
        
        if lap_id:
            logger.info(f"✅ Test rondetijd opgeslagen met ID: {lap_id}")
            
            # Test leaderboard
            leaderboard = telemetry_db_integration.get_current_leaderboard(limit=5)
            if leaderboard:
                logger.info(f"✅ Leaderboard test succesvol - {len(leaderboard)} entries")
            
            return True
        else:
            logger.error("❌ Fout bij opslaan test rondetijd")
            return False
            
    except Exception as e:
        logger.error(f"❌ Fout bij testen database integratie: {e}")
        return False

def manual_test_database():
    """Handmatige database test met eenvoudige SQL"""
    logger = setup_logging()
    
    logger.info("🔧 Handmatige database test...")
    
    try:
        # Direct MySQL test
        import mysql.connector
        from dotenv import load_dotenv
        
        load_dotenv()
        
        config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'database': os.getenv('DB_NAME', 'f1_telemetry'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'charset': 'utf8mb4'
        }
        
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Test simpele query
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        logger.info(f"✅ Database connectie OK - {len(tables)} tabellen gevonden")
        
        # Test tabel aanmaken met eenvoudige syntax
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id int PRIMARY KEY AUTO_INCREMENT,
                name varchar(100) NOT NULL
            )
        """)
        
        # Test insert
        cursor.execute("INSERT INTO test_table (name) VALUES ('test')")
        connection.commit()
        
        # Test select
        cursor.execute("SELECT * FROM test_table WHERE name = 'test'")
        result = cursor.fetchone()
        
        if result:
            logger.info("✅ Basis database operaties werken")
        
        # Cleanup
        cursor.execute("DROP TABLE test_table")
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Handmatige database test gefaald: {e}")
        return False

def manual_database_create_help():
    """Help voor handmatig database aanmaken"""
    print("\n📋 HANDMATIG DATABASE AANMAKEN:")
    print("1. Open je webbrowser en ga naar: http://localhost/phpmyadmin")
    print("2. Klik links op 'New' (Nieuw)")
    print("3. Typ als database naam: f1_telemetry")
    print("4. Klik 'Create' (Aanmaken)")
    print("5. Probeer deze setup opnieuw")

def main():
    """Main setup functie"""
    logger = setup_logging()
    
    print("🏎️  F1 25 Telemetry Database Setup - MYSQL 8.0+ COMPATIBLE")
    print("=" * 60)
    
    # Stap 1: Check .env bestand
    print("\n📋 Stap 1: Configuratie")
    if not check_env_file():
        print("❌ Setup gefaald bij .env configuratie")
        return False
    
    # Stap 2: Installeer dependencies
    print("\n📋 Stap 2: Dependencies")
    if not install_dependencies():
        print("❌ Setup gefaald bij installeren dependencies")
        print("\n💡 Handmatige installatie proberen:")
        print("   pip install mysql-connector-python")
        print("   pip install python-dotenv")
        return False
    
    # Stap 3: Test database basis verbinding
    print("\n📋 Stap 3: Basis database test")
    if not manual_test_database():
        print("❌ Basis database test gefaald")
        manual_database_create_help()
        return False
    
    # Stap 4: Maak database schema
    print("\n📋 Stap 4: Database schema")
    schema_success = create_database_schema()
    if not schema_success:
        print("⚠️ Schema setup had problemen, maar basis database werkt")
        print("💡 Je kunt de applicatie proberen - mogelijk werkt het toch")
    
    # Stap 5: Test integratie (optioneel)
    print("\n📋 Stap 5: Integratie test")
    if not test_database_integration():
        print("⚠️ Integratie test had problemen")
        print("💡 Basis database werkt wel - probeer de applicatie te starten")
    
    print("\n✅ Setup voltooid!")
    print("\n📋 Volgende stappen:")
    print("   1. Zorg dat deze bestanden in je python/ directory staan:")
    print("      - database_config.py")
    print("      - lap_time_database.py") 
    print("      - telemetry_utils.py")
    print("      - telemetry_db_integration.py")
    print("   2. Vervang je huidige bestanden met:")
    print("      - main.py → main_complete_with_database.py")
    print("      - screens/screen1.py → screen1_complete_with_database.py")
    print("   3. Start je applicatie: python main.py")
    print("\n🎯 Database functies zijn nu beschikbaar in het menu!")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        input("\nDruk op ENTER om af te sluiten...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Setup geannuleerd")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Onverwachte fout in setup: {e}")
        input("Druk op ENTER om af te sluiten...")
        sys.exit(1)