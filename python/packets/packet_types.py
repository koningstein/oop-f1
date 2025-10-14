"""
F1 25 Telemetry - Packet Types en Constanten
Bevat alle enums en constanten voor F1 25 UDP telemetry
"""

from enum import IntEnum

# Constanten
MAX_CARS = 22
MAX_PARTICIPANT_NAME_LENGTH = 32
MAX_TYRE_STINTS = 8
MAX_TYRE_SETS = 20  # 13 slick + 7 wet

class PacketID(IntEnum):
    """Packet Type IDs"""
    MOTION = 0                  # Realtime - alleen tijdens speler control
    SESSION = 1                 # Bij sessie start
    LAP_DATA = 2                # Elke frame
    EVENT = 3                   # Bij specifieke events
    PARTICIPANTS = 4            # Bij sessie start
    CAR_SETUPS = 5              # 2x per seconde
    CAR_TELEMETRY = 6           # Realtime
    CAR_STATUS = 7              # Rate as specified in menus
    FINAL_CLASSIFICATION = 8    # Einde race
    LOBBY_INFO = 9              # 2x per seconde in lobby
    CAR_DAMAGE = 10             # 2x per seconde
    SESSION_HISTORY = 11        # Op aanvraag
    TYRE_SETS = 12              # Op aanvraag
    MOTION_EX = 13              # Realtime extended motion
    TIME_TRIAL = 14             # Time trial data
    LAP_POSITIONS = 15          # Lap positions chart

class TeamID(IntEnum):
    """Team IDs"""
    MERCEDES = 0
    FERRARI = 1
    RED_BULL = 2
    WILLIAMS = 3
    ASTON_MARTIN = 4
    ALPINE = 5
    ALPHA_TAURI = 6
    HAAS = 7
    MCLAREN = 8
    ALFA_ROMEO = 9
    UNKNOWN = 255

class SessionType(IntEnum):
    """Sessie Types"""
    UNKNOWN = 0
    P1 = 1
    P2 = 2
    P3 = 3
    SHORT_P = 4
    Q1 = 5
    Q2 = 6
    Q3 = 7
    SHORT_Q = 8
    OSQ = 9
    RACE = 10
    RACE2 = 11
    RACE3 = 12
    TIME_TRIAL = 13

class Weather(IntEnum):
    """Weersomstandigheden"""
    CLEAR = 0
    LIGHT_CLOUD = 1
    OVERCAST = 2
    LIGHT_RAIN = 3
    HEAVY_RAIN = 4
    STORM = 5

class TrackID(IntEnum):
    """Circuit IDs"""
    MELBOURNE = 0
    PAUL_RICARD = 1
    SHANGHAI = 2
    SAKHIR_BAHRAIN = 3
    CATALUNYA = 4
    MONACO = 5
    MONTREAL = 6
    SILVERSTONE = 7
    HOCKENHEIM = 8
    HUNGARORING = 9
    SPA = 10
    MONZA = 11
    SINGAPORE = 12
    SUZUKA = 13
    ABU_DHABI = 14
    TEXAS = 15
    BRAZIL = 16
    AUSTRIA = 17
    SOCHI = 18
    MEXICO = 19
    BAKU = 20
    SAKHIR_SHORT = 21
    SILVERSTONE_SHORT = 22
    TEXAS_SHORT = 23
    SUZUKA_SHORT = 24
    HANOI = 25
    ZANDVOORT = 26
    IMOLA = 27
    PORTIMAO = 28
    JEDDAH = 29
    MIAMI = 30
    LAS_VEGAS = 31
    LOSAIL = 32

class PitStatus(IntEnum):
    """Pit status"""
    NONE = 0
    PITTING = 1
    IN_PIT_AREA = 2

class Sector(IntEnum):
    """Sector nummers"""
    SECTOR1 = 0
    SECTOR2 = 1
    SECTOR3 = 2

class DriverStatus(IntEnum):
    """Driver status"""
    IN_GARAGE = 0
    FLYING_LAP = 1
    IN_LAP = 2
    OUT_LAP = 3
    ON_TRACK = 4

class ResultStatus(IntEnum):
    """Result status"""
    INVALID = 0
    INACTIVE = 1
    ACTIVE = 2
    FINISHED = 3
    DNF = 4
    DISQUALIFIED = 5
    NOT_CLASSIFIED = 6
    RETIRED = 7

class SurfaceType(IntEnum):
    """Oppervlakte types"""
    TARMAC = 0
    RUMBLE_STRIP = 1
    CONCRETE = 2
    ROCK = 3
    GRAVEL = 4
    MUD = 5
    SAND = 6
    GRASS = 7
    WATER = 8
    COBBLESTONE = 9
    METAL = 10
    RIDGED = 11

class TyreCompound(IntEnum):
    """Band compounds"""
    C0 = 16
    C1 = 17
    C2 = 18
    C3 = 19
    C4 = 20
    C5 = 21
    C6 = 22
    INTER = 7
    WET = 8

class EventCode:
    """Event codes (4 character strings)"""
    SESSION_STARTED = "SSTA"
    SESSION_ENDED = "SEND"
    FASTEST_LAP = "FTLP"
    RETIREMENT = "RTMT"
    DRS_ENABLED = "DRSE"
    DRS_DISABLED = "DRSD"
    TEAM_MATE_IN_PITS = "TMPT"
    CHEQUERED_FLAG = "CHQF"
    RACE_WINNER = "RCWN"
    PENALTY_ISSUED = "PENA"
    SPEED_TRAP_TRIGGERED = "SPTP"
    START_LIGHTS = "STLG"
    LIGHTS_OUT = "LGOT"
    DRIVE_THROUGH_SERVED = "DTSV"
    STOP_GO_SERVED = "SGSV"
    FLASHBACK = "FLBK"
    BUTTON_STATUS = "BUTN"
    RED_FLAG = "RDFL"
    OVERTAKE = "OVTK"

class FiaFlag(IntEnum):
    """FIA Vlaggen"""
    NONE = 0
    GREEN = 1
    BLUE = 2
    YELLOW = 3
    RED = 4