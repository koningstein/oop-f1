"""
F1 25 Telemetry - Packet Types & Enums
Definities voor alle packet IDs en constanten
"""

from enum import IntEnum

class PacketID(IntEnum):
    """F1 25 Packet IDs"""
    MOTION = 0
    SESSION = 1
    LAP_DATA = 2
    EVENT = 3
    PARTICIPANTS = 4
    CAR_SETUPS = 5
    CAR_TELEMETRY = 6
    CAR_STATUS = 7
    FINAL_CLASSIFICATION = 8
    LOBBY_INFO = 9
    CAR_DAMAGE = 10
    SESSION_HISTORY = 11
    TYRE_SETS = 12
    MOTION_EX = 13
    TIME_TRIAL = 14
    LAP_POSITIONS = 15

class SessionType(IntEnum):
    """Sessie types"""
    UNKNOWN = 0
    PRACTICE_1 = 1
    PRACTICE_2 = 2
    PRACTICE_3 = 3
    SHORT_PRACTICE = 4
    QUALIFYING_1 = 5
    QUALIFYING_2 = 6
    QUALIFYING_3 = 7
    SHORT_QUALIFYING = 8
    ONE_SHOT_QUALIFYING = 9
    RACE = 10
    RACE_2 = 11
    RACE_3 = 12
    TIME_TRIAL = 13

class Weather(IntEnum):
    """Weersomstandigheden"""
    CLEAR = 0
    LIGHT_CLOUD = 1
    OVERCAST = 2
    LIGHT_RAIN = 3
    HEAVY_RAIN = 4
    STORM = 5

class DriverStatus(IntEnum):
    """Status van de driver"""
    IN_GARAGE = 0
    FLYING_LAP = 1
    IN_LAP = 2
    OUT_LAP = 3
    ON_TRACK = 4

class ResultStatus(IntEnum):
    """Result status van driver"""
    INVALID = 0
    INACTIVE = 1
    ACTIVE = 2
    FINISHED = 3
    DID_NOT_FINISH = 4
    DISQUALIFIED = 5
    NOT_CLASSIFIED = 6
    RETIRED = 7

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

# Packet header constanten
PACKET_FORMAT_2025 = 2025
GAME_YEAR = 25
MAX_CARS = 22
MAX_NAME_LENGTH = 32

# Packet sizes (in bytes) voor validatie
PACKET_SIZES = {
    PacketID.MOTION: 1349,
    PacketID.SESSION: 644,
    PacketID.LAP_DATA: 1131,
    PacketID.EVENT: 45,
    PacketID.PARTICIPANTS: 1306,
    PacketID.CAR_SETUPS: 1107,
    PacketID.CAR_TELEMETRY: 1352,
    PacketID.CAR_STATUS: 1239,
    PacketID.FINAL_CLASSIFICATION: 1020,
    PacketID.LOBBY_INFO: 1218,
    PacketID.CAR_DAMAGE: 953,
    PacketID.SESSION_HISTORY: 1460,
    PacketID.TYRE_SETS: 231,
    PacketID.MOTION_EX: 217,
    PacketID.TIME_TRIAL: 101,
    PacketID.LAP_POSITIONS: 1131
}

def get_packet_name(packet_id: int) -> str:
    """Verkrijg leesbare naam voor packet ID"""
    names = {
        PacketID.MOTION: "Motion",
        PacketID.SESSION: "Session",
        PacketID.LAP_DATA: "Lap Data",
        PacketID.EVENT: "Event",
        PacketID.PARTICIPANTS: "Participants",
        PacketID.CAR_SETUPS: "Car Setups",
        PacketID.CAR_TELEMETRY: "Car Telemetry",
        PacketID.CAR_STATUS: "Car Status",
        PacketID.FINAL_CLASSIFICATION: "Final Classification",
        PacketID.LOBBY_INFO: "Lobby Info",
        PacketID.CAR_DAMAGE: "Car Damage",
        PacketID.SESSION_HISTORY: "Session History",
        PacketID.TYRE_SETS: "Tyre Sets",
        PacketID.MOTION_EX: "Motion Extended",
        PacketID.TIME_TRIAL: "Time Trial",
        PacketID.LAP_POSITIONS: "Lap Positions"
    }
    return names.get(packet_id, f"Unknown ({packet_id})")