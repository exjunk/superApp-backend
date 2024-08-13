# test_risk_manager.py

import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from risk_manager import RiskManager

class TestRiskManager(unittest.TestCase):

    def setUp(self):
        self.mock_dhan = Mock()
        self.mock_logger = Mock()
        self.client_id = "test_client_id"
        
        # Patch the logger in risk_manager
        self.logger_patcher = patch('risk_manager.logger', self.mock_logger)
        self.logger_patcher.start()
        
        self.risk_manager = RiskManager(self.mock_dhan, self.client_id)

    def tearDown(self):
        self.logger_patcher.stop()

    def test_risk_management_normal(self):
        self.mock_dhan.get_fund_limits.return_value = {
            'data': {
                'sodLimit': 100000,
                'availabelBalance': 98000
            }
        }
        result = self.risk_manager.risk_management()
        self.assertTrue(result)

    def test_risk_management_minor_loss(self):
        self.mock_dhan.get_fund_limits.return_value = {
            'data': {
                'sodLimit': 100000,
                'availabelBalance': 94000
            }
        }
        result = self.risk_manager.risk_management()
        self.assertFalse(result)
        self.assertIsNotNone(self.risk_manager.resting_until)
        self.assertAlmostEqual(self.risk_manager.resting_until, datetime.now() + timedelta(minutes=30), delta=timedelta(seconds=1))

    def test_risk_management_major_loss(self):
        self.mock_dhan.get_fund_limits.return_value = {
            'data': {
                'sodLimit': 100000,
                'availabelBalance': 91000
            }
        }
        result = self.risk_manager.risk_management()
        self.assertFalse(result)
        self.assertIsNotNone(self.risk_manager.resting_until)
        self.assertAlmostEqual(self.risk_manager.resting_until, datetime.now() + timedelta(hours=1), delta=timedelta(seconds=1))

    def test_risk_management_critical_loss(self):
        self.mock_dhan.get_fund_limits.return_value = {
            'data': {
                'sodLimit': 100000,
                'availabelBalance': 89000
            }
        }
        with patch.object(self.risk_manager, 'close_all_positions_and_orders') as mock_close, \
             patch.object(self.risk_manager, 'send_kill_switch_request') as mock_kill_switch:
            result = self.risk_manager.risk_management()
            self.assertFalse(result)
            self.assertTrue(self.risk_manager.kill_switch_activated)
            mock_close.assert_called_once()
            mock_kill_switch.assert_called_once()

    def test_close_all_positions_and_orders(self):
        self.mock_dhan.get_positions.return_value = {
            'data': [
                {'securityId': '123', 'exchangeSegment': 'NSE', 'quantity': 10, 'productType': 'INTRADAY'},
                {'securityId': '456', 'exchangeSegment': 'BSE', 'quantity': -5, 'productType': 'DELIVERY'}
            ]
        }
        self.mock_dhan.get_order_list.return_value = {
            'data': [
                {'orderId': '789', 'orderStatus': 'PENDING'},
                {'orderId': '101', 'orderStatus': 'EXECUTED'}
            ]
        }
        self.risk_manager.close_all_positions_and_orders()
        self.assertEqual(self.mock_dhan.place_order.call_count, 2)
        self.assertEqual(self.mock_dhan.cancel_order.call_count, 1)

    def test_send_kill_switch_request(self):
        self.risk_manager.send_kill_switch_request()
        self.mock_dhan.kill_switch.assert_called_once_with(kill_switch_status='ACTIVATE')

if __name__ == '__main__':
    unittest.main()