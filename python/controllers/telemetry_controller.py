"""
F1 25 Telemetry System - Telemetry Controller
Hoofdcontroller voor verwerking van telemetry packets
"""

from typing import Optional
from packet_parsers import *
from models import SessionModel, LapModel, DriverModel, TelemetryModel
from services import logger_service

class TelemetryController:
    """
    Controller voor verwerking van telemetry packets
    Ontvangt packets van UDP listener en verwerkt ze
    """
    
    def __init__(self):
        """Initialiseer telemetry controller"""
        self.logger = logger_service.get_logger('TelemetryController')
        
        # Models
        self.session_model = SessionModel()
        self.lap_model = LapModel()
        self.driver_model = DriverModel()
        self.telemetry_model = TelemetryModel()
        
        # Parsers
        self.session_parser = SessionParser()
        self.lap_parser = LapDataParser()
        self.history_parser = SessionHistoryParser()
        self.participants_parser = ParticipantsParser()
        self.telemetry_parser = CarTelemetryParser()
        
        # State tracking
        self.current_session_id: Optional[int] = None
        self.player_car_index: Optional[int] = None
        self.last_lap_numbers = {}  # Track laatste lap per car
        
        self.logger.info("Telemetry controller geïnitialiseerd")
    
    def handle_session_packet(self, header: PacketHeader, payload: bytes):
        """
        Verwerk Session packet (ID 1)
        
        Args:
            header: Packet header
            payload: Packet payload
        """
        session_data = self.session_parser.parse(header, payload)
        if not session_data:
            return
        
        # Check of dit een nieuwe sessie is
        session_uid = header.session_uid
        existing = self.session_model.get_session_by_uid(session_uid)
        
        if not existing:
            # Nieuwe sessie aanmaken
            session_dict = {
                'session_uid': session_uid,
                'track_id': session_data.track_id,
                'session_type': session_data.session_type,
                'weather': session_data.weather,
                'track_temperature': session_data.track_temperature,
                'air_temperature': session_data.air_temperature,
                'total_laps': session_data.total_laps,
                'session_duration': session_data.session_duration
            }
            
            self.current_session_id = self.session_model.create_session(session_dict)
            self.logger.info(
                f"Nieuwe sessie gestart: ID {self.current_session_id}, "
                f"Track {session_data.track_id}, Type {session_data.session_type}"
            )
        else:
            self.current_session_id = existing['id']
        
        self.player_car_index = header.player_car_index
    
    def handle_lap_data_packet(self, header: PacketHeader, payload: bytes):
        """
        Verwerk Lap Data packet (ID 2)
        
        Args:
            header: Packet header
            payload: Packet payload
        """
        if not self.current_session_id:
            return
        
        lap_packet = self.lap_parser.parse(header, payload)
        if not lap_packet:
            return
        
        # Verwerk alleen speler data (kan later uitgebreid worden)
        if self.player_car_index is None:
            return
        
        lap_data = lap_packet.lap_data[self.player_car_index]
        
        # Check of nieuwe lap is afgerond
        current_lap = lap_data.current_lap_num
        last_lap = self.last_lap_numbers.get(self.player_car_index, 0)
        
        if current_lap > last_lap and lap_data.last_lap_time_ms > 0:
            # Nieuwe lap afgerond - sla op in database
            lap_dict = {
                'session_id': self.current_session_id,
                'car_index': self.player_car_index,
                'lap_number': last_lap,
                'lap_time_ms': lap_data.last_lap_time_ms,
                'sector1_ms': lap_data.get_sector1_time_ms(),
                'sector2_ms': lap_data.get_sector2_time_ms(),
                'sector3_ms': lap_data.get_sector3_time_ms(),
                'is_valid': not lap_data.current_lap_invalid
            }
            
            self.lap_model.save_lap(lap_dict)
            self.logger.info(
                f"Lap {last_lap} opgeslagen: {lap_data.last_lap_time_ms}ms, "
                f"Valid: {not lap_data.current_lap_invalid}"
            )
        
        self.last_lap_numbers[self.player_car_index] = current_lap
    
    def handle_session_history_packet(self, header: PacketHeader, payload: bytes):
        """
        Verwerk Session History packet (ID 11)
        Gebruikt voor accurate sector validatie
        
        Args:
            header: Packet header
            payload: Packet payload
        """
        if not self.current_session_id:
            return
        
        history_data = self.history_parser.parse(header, payload)
        if not history_data:
            return
        
        # Update sector validatie voor alle laps in history
        for lap_idx, lap_history in enumerate(history_data.lap_history_data):
            if lap_history.lap_time_ms == 0:
                continue
            
            lap_number = lap_idx + 1
            
            lap_dict = {
                'session_id': self.current_session_id,
                'car_index': history_data.car_idx,
                'lap_number': lap_number,
                'lap_time_ms': lap_history.lap_time_ms,
                'sector1_ms': lap_history.get_sector1_total_ms(),
                'sector2_ms': lap_history.get_sector2_total_ms(),
                'sector3_ms': lap_history.get_sector3_total_ms(),
                'sector1_valid': lap_history.is_sector1_valid(),
                'sector2_valid': lap_history.is_sector2_valid(),
                'sector3_valid': lap_history.is_sector3_valid(),
                'is_valid': lap_history.is_lap_valid()
            }
            
            self.lap_model.save_lap(lap_dict)
    
    def handle_participants_packet(self, header: PacketHeader, payload: bytes):
        """
        Verwerk Participants packet (ID 4)
        
        Args:
            header: Packet header
            payload: Packet payload
        """
        if not self.current_session_id:
            return
        
        participants_packet = self.participants_parser.parse(header, payload)
        if not participants_packet:
            return
        
        # Sla alle participants op
        for car_idx, participant in enumerate(participants_packet.participants):
            if car_idx >= participants_packet.num_active_cars:
                break
            
            driver_dict = {
                'session_id': self.current_session_id,
                'car_index': car_idx,
                'driver_name': participant.name,
                'team_id': participant.team_id,
                'race_number': participant.race_number,
                'nationality': participant.nationality,
                'is_player': (car_idx == self.player_car_index)
            }
            
            self.driver_model.save_driver(driver_dict)
        
        self.logger.info(f"Participants opgeslagen: {participants_packet.num_active_cars} drivers")
    
    def handle_car_telemetry_packet(self, header: PacketHeader, payload: bytes):
        """
        Verwerk Car Telemetry packet (ID 6)
        
        Args:
            header: Packet header
            payload: Packet payload
        """
        if not self.current_session_id or self.player_car_index is None:
            return
        
        telemetry_packet = self.telemetry_parser.parse(header, payload)
        if not telemetry_packet:
            return
        
        # Sla alleen speler telemetrie op (optioneel: alle drivers)
        telemetry_data = telemetry_packet.car_telemetry_data[self.player_car_index]
        
        telemetry_dict = {
            'session_id': self.current_session_id,
            'car_index': self.player_car_index,
            'speed': telemetry_data.speed,
            'throttle': telemetry_data.throttle,
            'brake': telemetry_data.brake,
            'gear': telemetry_data.gear,
            'rpm': telemetry_data.engine_rpm,
            'drs': telemetry_data.drs
        }
        
        self.telemetry_model.save_telemetry(telemetry_dict)
    
    def get_current_session_id(self) -> Optional[int]:
        """Verkrijg huidige session ID"""
        return self.current_session_id