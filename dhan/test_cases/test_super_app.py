import unittest
from unittest.mock import patch, MagicMock

import sys
import os

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)


import super_app
from Enums import Index, Option_Type

class TestSuperApp(unittest.TestCase):

    @patch('super_app.dhan')
    def test_get_order_status(self, mock_dhan):
        mock_dhan.get_order_by_id.return_value = {'status': 'COMPLETE'}
        result = super_app.get_order_status('123')
        self.assertEqual(result, {'status': 'COMPLETE'})
        mock_dhan.get_order_by_id.assert_called_once_with(order_id='123')

    @patch('super_app.db_management')
    def test_fetch_index_details_from_db(self, mock_db):
        mock_db.get_kill_switch_rules.return_value = {'kill_switch': True}
        mock_db.get_index_rules.return_value = {'index_rule': 'test'}
        result = super_app.fetch_index_details_from_db('client1', 'NIFTY')
        self.assertEqual(result, ({'kill_switch': True}, {'index_rule': 'test'}))

    @patch('super_app.risk_manager')
    @patch('super_app.Index_attributes')
    @patch('super_app.fetch_index_details_from_db')
    @patch('super_app.strike_selection')
    @patch('super_app.dhan')
    def test_placeOrder(self, mock_dhan, mock_strike, mock_fetch, mock_index, mock_risk):
        mock_risk.check_risk.return_value = True
        mock_index.get_index_attributes.return_value = MagicMock(lotsize=50, index_risk=10, profit=20, exchange_segment='NSE_FNO', current_price=15000)
        mock_fetch.return_value = ({}, [{'trading_lot': 1, 'default_qty': 50, 'stop_loss': 10, 'profit': 20, 'exchange': 'NSE_FNO', 'trading_enabled': 1}])
        mock_strike.calculate_trading_strike.return_value = {'SM_SCRIP_CODE': '123', 'SM_CUSTOM_SYMBOL': 'NIFTY22000CE'}
        mock_dhan.place_order.return_value = {'status': 'success', 'data': {'orderId': '456'}}

        result = super_app.placeOrder('NIFTY', 'CE', 'BUY', 'client123', 'dhan123', 'INTRA')
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['orderId'], '456')

    @patch('super_app.dhan')
    def test_get_open_positions(self, mock_dhan):
        mock_dhan.get_positions.return_value = {'positions': []}
        result = super_app.get_open_positions()
        self.assertEqual(result, {'positions': []})

    @patch('super_app.dhan')
    def test_get_open_orders(self, mock_dhan):
        mock_dhan.get_order_list.return_value = {'data': [{'orderStatus': 'PENDING'}]}
        result = super_app.get_open_orders()
        self.assertEqual(result, [{'orderStatus': 'PENDING'}])

    @patch('super_app.dhan')
    def test_cancel_open_order(self, mock_dhan):
        mock_dhan.cancel_order.return_value = {'status': 'success'}
        result = super_app.cancel_open_order('123')
        self.assertEqual(result, {'status': 'success'})

    @patch('super_app.dhan')
    def test_modify_open_order(self, mock_dhan):
        mock_dhan.modify_order.return_value = {'status': 'success'}
        result = super_app.modify_open_order('123', 1, 100, 'LIMIT', 'ENTRY', 1, 99, 'DAY')
        self.assertEqual(result, {'status': 'success'})

    @patch('super_app.dhan')
    def test_getFundLimit(self, mock_dhan):
        mock_dhan.get_fund_limits.return_value = {'available': 10000}
        result = super_app.getFundLimit()
        self.assertEqual(result, {'available': 10000})

if __name__ == '__main__':
    unittest.main()