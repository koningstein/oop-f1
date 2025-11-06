# F1 25 Telemetry System

Telemetry systeem voor F1 25 game - Techniek College Rotterdam  
Software Developer MBO-4 Project

## Overzicht

Dit systeem ontvangt live telemetry data via UDP van de F1 25 game en toont:
- Real-time rondetijden en sectortijden met validatie
- Live telemetrie (snelheid, RPM, gear, throttle, brake)
- Klassementen en vergelijkingen
- Sessie historie

## Functionaliteit

### 6 Schermen
1. **Overzicht** - Sessie informatie en algemene status
2. **Timing & Sectors** - Rondetijden en sectortijden met validatie markers
3. **Live Telemetrie** - Real-time speed, RPM, gear, inputs
4. **Klassement** - Leaderboard van alle drivers
5. **Vergelijking** - Vergelijk prestaties met leider
6. **Sessie Historie** - Overzicht van vorige sessies

## Installatie

### Vereisten
- Python 3.8 of hoger
- MySQL/MariaDB database
- F1 25 game
- WampServer (of andere MySQL server)

### Stappen

1. **Clone/Download project**
```bash
cd racesimulator
```

2. **Installeer dependencies**
```bash
pip install -r requirements.txt
```

3. **Configureer database**
- Start WampServer
- Maak database aan: `racesimulator`
- Pas `config.py` aan indien nodig (host, user, password)

4. **Start applicatie**
```bash
python main.py
```

## F1 25 Configuratie

Zet UDP telemetry aan in F1 25:

1. Game Options > Settings > Telemetry Settings
2. UDP Telemetry: **On**
3. UDP Port: **20777**
4. UDP Format: **2025**
5. UDP IP: **127.0.0.1** (localhost)

## Gebruik

### Menu Navigatie
- Kies **1-6** om naar een scherm te gaan
- Kies **0** of **Q** om af te sluiten
- Kies **R** voor auto-refresh (experimenteel)

### Logging
Alle events worden gelogd naar: `logs/telemetry.log`
- Maximum 10 MB per bestand
- 5 backup bestanden
- Bevat debug info, errors, packet ontvangst

## Project Structuur

```
racesimulator/
├── main.py                     # Startpunt
├── config.py                   # Configuratie
├── requirements.txt            # Dependencies
│
├── logs/                       # Log bestanden
│
├── models/                     # Database models (MVC)
│   ├── database.py
│   ├── session_model.py
│   ├── lap_model.py
│   ├── driver_model.py
│   └── telemetry_model.py
│
├── views/                      # User interface (MVC)
│   ├── menu_view.py
│   └── screens/
│       ├── screen1_overview.py
│       ├── screen2_timing.py
│       ├── screen3_telemetry.py
│       ├── screen4_standings.py
│       ├── screen5_comparison.py
│       └── screen6_history.py
│
├── controllers/                # Business logic (MVC)
│   ├── telemetry_controller.py
│   └── menu_controller.py
│
├── parsers/                    # F1 25 packet parsers
│   ├── packet_header.py
│   ├── packet_types.py
│   ├── base_parser.py
│   ├── session_parser.py
│   ├── lap_parser.py
│   ├── history_parser.py
│   ├── participant_parser.py
│   └── car_parser.py
│
├── services/                   # Services
│   ├── logger_service.py
│   └── udp_listener.py
│
└── utils/                      # Utilities
    ├── time_formatter.py
    └── constants.py
```

## Database Schema

### sessions
- Sessie informatie (track, weather, type)

### drivers
- Driver/participant informatie

### laps
- Rondetijden en sectortijden
- Validatie flags per sector

### telemetry_live
- Live telemetrie snapshots

## Technische Details

### Architectuur
- **MVC Pattern**: Model-View-Controller scheiding
- **OOP**: Object-georiënteerd met classes
- **Threading**: UDP listener draait in aparte thread
- **Connection Pooling**: Efficiënte database connecties

### F1 25 Packets
Verwerkt de volgende packet types:
- **Session (ID 1)**: Track en sessie info
- **Lap Data (ID 2)**: Rondetijden en sectoren
- **Participants (ID 4)**: Driver informatie
- **Car Telemetry (ID 6)**: Live telemetrie
- **Session History (ID 11)**: Sector validatie (belangrijk!)

### Sector Validatie
Gebruikt Session History packets (ID 11) met bitwise validatie flags voor accurate sector validatie, precies zoals in de game.

## Troubleshooting

### Geen data ontvangen?
- Check of F1 25 draait en een sessie actief is
- Controleer UDP settings in game
- Check firewall instellingen
- Bekijk logs in `logs/telemetry.log`

### Database errors?
- Check of MySQL/WampServer draait
- Controleer database credentials in `config.py`
- Tabellen worden automatisch aangemaakt

### Packets errors?
- Zorg dat UDP Format op **2025** staat in game
- Oudere formats (2023, 2024) worden niet ondersteund
- Check packet IDs in logs

## Ontwikkeling

### Dependencies installeren
```bash
pip install -r requirements.txt
```

### Logs bekijken
```bash
tail -f logs/telemetry.log
```

### Database resetten
```sql
DROP DATABASE racesimulator;
CREATE DATABASE racesimulator;
```

## Credits

**Ontwikkeld voor Techniek College Rotterdam**  
Software Developer MBO-4  
Educational F1 Telemetry System

## Licentie

Educational use only - Techniek College Rotterdam