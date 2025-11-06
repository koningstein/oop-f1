"""
F1 25 Telemetry System - Controller Tests
Unit tests voor controllers
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from controllers import DataProcessor, SessionController

class TestDataProcessor(unittest.TestCase):
    """Tests voor DataProcessor"""
    
    def setUp(self):
        """Setup voor tests"""
        self.processor = DataProcessor()
    
    def test_calculate_lap_delta(self):
        """Test lap delta berekening"""
        result = self.processor.calculate_lap_delta(90000, 85000)
        self.assertEqual(result, 5000)
        
        result = self.processor.calculate_lap_delta(85000, 90000)
        self.assertEqual(result, -5000)
    
    def test_calculate_theoretical_best(self):
        """Test theoretische beste lap berekening"""
        sectors = {
            'sector1': 28000,
            'sector2': 29000,
            'sector3': 28500
        }
        
        result = self.processor.calculate_theoretical_best(sectors)
        self.assertEqual(result, 85500)
        
        # Test met None waarde
        sectors_incomplete = {
            'sector1': 28000,
            'sector2': None,
            'sector3': 28500
        }
        
        result = self.processor.calculate_theoretical_best(sectors_incomplete)
        self.assertIsNone(result)
    
    def test_calculate_pace(self):
        """Test pace berekening"""
        lap_times = [90000, 89500, 90200, 89800, 90100]
        
        pace = self.processor.calculate_pace(lap_times, exclude_outliers=False)
        self.assertIsNotNone(pace)
        self.assertAlmostEqual(pace, 89920.0, places=1)
        
        # Test met outliers excluded
        pace_no_outliers = self.processor.calculate_pace(lap_times, exclude_outliers=True)
        self.assertIsNotNone(pace_no_outliers)
    
    def test_calculate_consistency(self):
        """Test consistentie berekening"""
        # Perfecte consistentie (alle tijden gelijk)
        perfect_times = [90000, 90000, 90000, 90000]
        consistency = self.processor.calculate_consistency(perfect_times)
        self.assertEqual(consistency, 0.0)
        
        # Variabele tijden
        variable_times = [90000, 89000, 91000, 90500]
        consistency = self.processor.calculate_consistency(variable_times)
        self.assertGreater(consistency, 0)
    
    def test_find_best_lap(self):
        """Test beste lap vinden"""
        laps = [
            {'lap_time_ms': 90000, 'is_valid': True},
            {'lap_time_ms': 85000, 'is_valid': True},
            {'lap_time_ms': 88000, 'is_valid': False},  # Invalide
            {'lap_time_ms': 87000, 'is_valid': True}
        ]
        
        best = self.processor.find_best_lap(laps)
        self.assertIsNotNone(best)
        self.assertEqual(best['lap_time_ms'], 85000)
    
    def test_find_best_sectors(self):
        """Test beste sectoren vinden"""
        laps = [
            {
                'sector1_ms': 28000, 'sector1_valid': True,
                'sector2_ms': 30000, 'sector2_valid': True,
                'sector3_ms': 29000, 'sector3_valid': True
            },
            {
                'sector1_ms': 27500, 'sector1_valid': True,
                'sector2_ms': 29500, 'sector2_valid': True,
                'sector3_ms': 28500, 'sector3_valid': True
            },
            {
                'sector1_ms': 28200, 'sector1_valid': True,
                'sector2_ms': 29000, 'sector2_valid': True,
                'sector3_ms': 28000, 'sector3_valid': True
            }
        ]
        
        best = self.processor.find_best_sectors(laps)
        self.assertEqual(best['sector1'], 27500)
        self.assertEqual(best['sector2'], 29000)
        self.assertEqual(best['sector3'], 28000)
    
    def test_calculate_sector_percentages(self):
        """Test sector percentage berekening"""
        percentages = self.processor.calculate_sector_percentages(
            30000, 30000, 30000
        )
        
        self.assertAlmostEqual(percentages['sector1'], 33.333, places=2)
        self.assertAlmostEqual(percentages['sector2'], 33.333, places=2)
        self.assertAlmostEqual(percentages['sector3'], 33.333, places=2)
    
    def test_is_improving(self):
        """Test verbetering detectie"""
        # Verbeterende tijden
        improving_times = [92000, 91000, 90000, 89500, 89000]
        self.assertTrue(self.processor.is_improving(improving_times, window_size=3))
        
        # Verslechterende tijden
        worsening_times = [89000, 89500, 90000, 91000, 92000]
        self.assertFalse(self.processor.is_improving(worsening_times, window_size=3))


class TestSessionController(unittest.TestCase):
    """Tests voor SessionController"""
    
    def setUp(self):
        """Setup voor tests"""
        self.session_controller = SessionController()
    
    @patch('controllers.session_controller.SessionModel')
    def test_start_new_session(self, mock_session_model):
        """Test nieuwe sessie starten"""
        mock_model = Mock()
        mock_model.get_session_by_uid.return_value = None
        mock_model.create_session.return_value = 123
        mock_session_model.return_value = mock_model
        
        session_controller = SessionController()
        
        # Mock session data
        mock_session_data = Mock()
        mock_session_data.track_id = 5
        mock_session_data.session_type = 10
        mock_session_data.weather = 0
        mock_session_data.track_temperature = 25
        mock_session_data.air_temperature = 20
        mock_session_data.total_laps = 50
        mock_session_data.session_duration = 3600
        
        session_id = session_controller.start_session(12345, mock_session_data)
        
        self.assertEqual(session_id, 123)
        self.assertTrue(session_controller.session_active)
    
    def test_session_state_management(self):
        """Test sessie state management"""
        # Start state
        self.assertFalse(self.session_controller.is_session_active())
        self.assertIsNone(self.session_controller.get_session_id())
        
        # Simulate session start
        self.session_controller.current_session_id = 123
        self.session_controller.session_active = True
        
        self.assertTrue(self.session_controller.is_session_active())
        self.assertEqual(self.session_controller.get_session_id(), 123)
        
        # End session
        self.session_controller.session_active = False
        self.session_controller.current_session_id = None
        
        self.assertFalse(self.session_controller.is_session_active())


class TestMenuController(unittest.TestCase):
    """Tests voor MenuController"""
    
    def test_menu_controller_initialization(self):
        """Test menu controller initialisatie"""
        from controllers import MenuController
        
        controller = MenuController()
        
        self.assertEqual(controller.current_screen, 1)
        self.assertFalse(controller.running)
        self.assertEqual(len(controller.screens), 0)
    
    def test_register_screen(self):
        """Test scherm registratie"""
        from controllers import MenuController
        
        controller = MenuController()
        mock_screen = Mock()
        
        controller.register_screen(1, mock_screen)
        
        self.assertIn(1, controller.screens)
        self.assertEqual(controller.screens[1], mock_screen)
    
    def test_set_screen(self):
        """Test scherm switchen"""
        from controllers import MenuController
        
        controller = MenuController()
        mock_screen = Mock()
        
        controller.register_screen(2, mock_screen)
        result = controller.set_screen(2)
        
        self.assertTrue(result)
        self.assertEqual(controller.current_screen, 2)
        
        # Test ongeldige scherm nummer
        result = controller.set_screen(99)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()