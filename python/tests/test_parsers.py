"""
F1 25 Telemetry System - Parser Tests
Unit tests voor packet parsers
"""

import unittest
import struct
from parsers import PacketHeader, PacketID
from parsers.packet_types import PACKET_FORMAT_2025, GAME_YEAR

class TestPacketHeader(unittest.TestCase):
    """Tests voor PacketHeader parser"""
    
    def test_valid_header_parsing(self):
        """Test parsing van valide header"""
        # Maak test header data
        header_data = struct.pack(
            "<HBBBBBQfIIBB",
            PACKET_FORMAT_2025,  # packet_format
            GAME_YEAR,  # game_year
            1,  # game_major_version
            0,  # game_minor_version
            1,  # packet_version
            PacketID.SESSION,  # packet_id
            12345678,  # session_uid
            100.5,  # session_time
            1000,  # frame_identifier
            1000,  # overall_frame_identifier
            0,  # player_car_index
            255  # secondary_player_car_index
        )
        
        header = PacketHeader.from_bytes(header_data)
        
        self.assertIsNotNone(header)
        self.assertEqual(header.packet_format, PACKET_FORMAT_2025)
        self.assertEqual(header.game_year, GAME_YEAR)
        self.assertEqual(header.packet_id, PacketID.SESSION)
        self.assertEqual(header.player_car_index, 0)
        self.assertTrue(header.is_valid())
    
    def test_invalid_packet_format(self):
        """Test header met verkeerd packet format"""
        header_data = struct.pack(
            "<HBBBBBQfIIBB",
            2024,  # Verkeerd packet format
            GAME_YEAR,
            1, 0, 1,
            PacketID.SESSION,
            12345678,
            100.5,
            1000, 1000,
            0, 255
        )
        
        header = PacketHeader.from_bytes(header_data)
        self.assertIsNotNone(header)
        self.assertFalse(header.is_valid())
    
    def test_invalid_car_index(self):
        """Test header met ongeldige car index"""
        header_data = struct.pack(
            "<HBBBBBQfIIBB",
            PACKET_FORMAT_2025,
            GAME_YEAR,
            1, 0, 1,
            PacketID.SESSION,
            12345678,
            100.5,
            1000, 1000,
            50,  # Ongeldige car index (> 21)
            255
        )
        
        header = PacketHeader.from_bytes(header_data)
        self.assertIsNotNone(header)
        self.assertFalse(header.is_valid())
    
    def test_header_too_short(self):
        """Test te korte header data"""
        header_data = b"short"
        header = PacketHeader.from_bytes(header_data)
        self.assertIsNone(header)
    
    def test_get_payload(self):
        """Test payload extractie"""
        header_data = struct.pack(
            "<HBBBBBQfIIBB",
            PACKET_FORMAT_2025, GAME_YEAR,
            1, 0, 1, PacketID.SESSION,
            12345678, 100.5,
            1000, 1000, 0, 255
        )
        payload_data = b"TEST_PAYLOAD_DATA"
        full_packet = header_data + payload_data
        
        header = PacketHeader.from_bytes(full_packet)
        payload = header.get_payload(full_packet)
        
        self.assertEqual(payload, payload_data)


class TestLapDataParser(unittest.TestCase):
    """Tests voor LapDataParser"""
    
    def setUp(self):
        """Setup voor tests"""
        from parsers import LapDataParser
        self.parser = LapDataParser()
    
    def test_parse_valid_lap_data(self):
        """Test parsing van valide lap data"""
        # Maak test header
        header_data = struct.pack(
            "<HBBBBBQfIIBB",
            PACKET_FORMAT_2025, GAME_YEAR,
            1, 0, 1, PacketID.LAP_DATA,
            12345678, 100.5,
            1000, 1000, 0, 255
        )
        header = PacketHeader.from_bytes(header_data)
        
        # Maak lap data voor 22 auto's (50 bytes per auto) + 2 bytes
        lap_data_size = 50 * 22 + 2
        payload = b'\x00' * lap_data_size
        
        result = self.parser.parse(header, payload)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result.lap_data), 22)
    
    def test_parse_invalid_payload_size(self):
        """Test parsing met te kleine payload"""
        header_data = struct.pack(
            "<HBBBBBQfIIBB",
            PACKET_FORMAT_2025, GAME_YEAR,
            1, 0, 1, PacketID.LAP_DATA,
            12345678, 100.5,
            1000, 1000, 0, 255
        )
        header = PacketHeader.from_bytes(header_data)
        
        # Te kleine payload
        payload = b'short'
        
        result = self.parser.parse(header, payload)
        self.assertIsNone(result)


class TestSessionHistoryParser(unittest.TestCase):
    """Tests voor SessionHistoryParser"""
    
    def setUp(self):
        """Setup voor tests"""
        from parsers import SessionHistoryParser
        self.parser = SessionHistoryParser()
    
    def test_sector_validation_flags(self):
        """Test sector validatie bit flags"""
        from parsers.history_parser import LapHistoryData
        
        # Alle sectoren valide (0x07 = 0b111)
        lap_history = LapHistoryData(
            lap_time_ms=90000,
            sector1_time_ms=500,
            sector1_time_minutes=0,
            sector2_time_ms=800,
            sector2_time_minutes=0,
            sector3_time_ms=700,
            sector3_time_minutes=0,
            lap_valid_bit_flags=0x07
        )
        
        self.assertTrue(lap_history.is_sector1_valid())
        self.assertTrue(lap_history.is_sector2_valid())
        self.assertTrue(lap_history.is_sector3_valid())
        self.assertTrue(lap_history.is_lap_valid())
        
        # Alleen sector 1 en 2 valide (0x03 = 0b011)
        lap_history_invalid = LapHistoryData(
            lap_time_ms=90000,
            sector1_time_ms=500,
            sector1_time_minutes=0,
            sector2_time_ms=800,
            sector2_time_minutes=0,
            sector3_time_ms=700,
            sector3_time_minutes=0,
            lap_valid_bit_flags=0x03
        )
        
        self.assertTrue(lap_history_invalid.is_sector1_valid())
        self.assertTrue(lap_history_invalid.is_sector2_valid())
        self.assertFalse(lap_history_invalid.is_sector3_valid())
        self.assertFalse(lap_history_invalid.is_lap_valid())


if __name__ == '__main__':
    unittest.main()