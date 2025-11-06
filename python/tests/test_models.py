"""
F1 25 Telemetry System - Model Tests
Unit tests voor database models
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from models import SessionModel, LapModel, DriverModel

class TestSessionModel(unittest.TestCase):
    """Tests voor SessionModel"""
    
    def setUp(self):
        """Setup voor tests"""
        self.session_model = SessionModel()
    
    @patch('models.session_model.database')
    def test_create_session(self, mock_db):
        """Test sessie aanmaken"""
        # Mock database response
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 123
        mock_connection.cursor.return_value = mock_cursor
        mock_db.get_connection.return_value = mock_connection
        
        session_data = {
            'session_uid': 12345,
            'track_id': 5,
            'session_type': 10,
            'weather': 0,
            'track_temperature': 25,
            'air_temperature': 20,
            'total_laps': 50,
            'session_duration': 3600
        }
        
        session_id = self.session_model.create_session(session_data)
        
        self.assertEqual(session_id, 123)
        self.assertEqual(self.session_model.current_session_id, 123)
    
    @patch('models.session_model.database')
    def test_get_session_by_uid(self, mock_db):
        """Test sessie ophalen op UID"""
        mock_db.fetch_one.return_value = {
            'id': 123,
            'session_uid': 12345,
            'track_id': 5
        }
        
        result = self.session_model.get_session_by_uid(12345)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], 123)
        self.assertEqual(self.session_model.current_session_id, 123)
    
    @patch('models.session_model.database')
    def test_end_session(self, mock_db):
        """Test sessie beëindigen"""
        mock_db.execute_query.return_value = True
        
        self.session_model.current_session_id = 123
        result = self.session_model.end_session(123)
        
        self.assertTrue(result)


class TestLapModel(unittest.TestCase):
    """Tests voor LapModel"""
    
    def setUp(self):
        """Setup voor tests"""
        self.lap_model = LapModel()
    
    @patch('models.lap_model.database')
    def test_save_lap(self, mock_db):
        """Test lap opslaan"""
        mock_db.execute_query.return_value = True
        
        lap_data = {
            'session_id': 123,
            'car_index': 0,
            'lap_number': 5,
            'lap_time_ms': 90000,
            'sector1_ms': 30000,
            'sector2_ms': 30000,
            'sector3_ms': 30000,
            'sector1_valid': True,
            'sector2_valid': True,
            'sector3_valid': True,
            'is_valid': True
        }
        
        result = self.lap_model.save_lap(lap_data)
        
        self.assertTrue(result)
    
    @patch('models.lap_model.database')
    def test_get_best_lap(self, mock_db):
        """Test beste lap ophalen"""
        mock_db.fetch_one.return_value = {
            'lap_number': 5,
            'lap_time_ms': 85000,
            'is_valid': True
        }
        
        result = self.lap_model.get_best_lap(123, 0)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['lap_time_ms'], 85000)
    
    @patch('models.lap_model.database')
    def test_get_best_sectors(self, mock_db):
        """Test beste sectoren ophalen"""
        mock_db.fetch_one.side_effect = [
            {'best': 28000},  # sector 1
            {'best': 29000},  # sector 2
            {'best': 28500}   # sector 3
        ]
        
        result = self.lap_model.get_best_sectors(123, 0)
        
        self.assertEqual(result['sector1'], 28000)
        self.assertEqual(result['sector2'], 29000)
        self.assertEqual(result['sector3'], 28500)
    
    @patch('models.lap_model.database')
    def test_get_session_leaderboard(self, mock_db):
        """Test leaderboard ophalen"""
        mock_db.fetch_all.return_value = [
            {'car_index': 0, 'driver_name': 'Driver 1', 'best_lap_time': 85000},
            {'car_index': 1, 'driver_name': 'Driver 2', 'best_lap_time': 86000}
        ]
        
        result = self.lap_model.get_session_leaderboard(123)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['best_lap_time'], 85000)


class TestDriverModel(unittest.TestCase):
    """Tests voor DriverModel"""
    
    def setUp(self):
        """Setup voor tests"""
        self.driver_model = DriverModel()
    
    @patch('models.driver_model.database')
    def test_save_driver(self, mock_db):
        """Test driver opslaan"""
        mock_db.execute_query.return_value = True
        
        driver_data = {
            'session_id': 123,
            'car_index': 0,
            'driver_name': 'Test Driver',
            'team_id': 0,
            'race_number': 33,
            'nationality': 10,
            'is_player': True
        }
        
        result = self.driver_model.save_driver(driver_data)
        
        self.assertTrue(result)
    
    @patch('models.driver_model.database')
    def test_get_driver(self, mock_db):
        """Test driver ophalen"""
        mock_db.fetch_one.return_value = {
            'car_index': 0,
            'driver_name': 'Test Driver',
            'team_id': 0,
            'is_player': True
        }
        
        result = self.driver_model.get_driver(123, 0)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['driver_name'], 'Test Driver')
    
    @patch('models.driver_model.database')
    def test_get_player_driver(self, mock_db):
        """Test speler driver ophalen"""
        mock_db.fetch_one.return_value = {
            'car_index': 0,
            'driver_name': 'Player',
            'is_player': True
        }
        
        result = self.driver_model.get_player_driver(123)
        
        self.assertIsNotNone(result)
        self.assertTrue(result['is_player'])


if __name__ == '__main__':
    unittest.main()