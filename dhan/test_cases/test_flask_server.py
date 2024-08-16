import unittest
from unittest.mock import patch, MagicMock

import sys
import os

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)


from flask import Flask
from flask_testing import TestCase
import flask_server
import json

class TestFlaskServer(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    @patch('flask_server.my_app')
    def test_getAllOrders(self, mock_my_app):
        mock_my_app.getOrders.return_value = {'orders': []}
        response = self.client.get('/orders')
        self.assertEqual(response.json, {'orders': []})

    @patch('flask_server.my_app')
    def test_getAllOpenOrders(self, mock_my_app):
        mock_my_app.get_open_orders.return_value = [{'id': '123'}]
        response = self.client.get('/openOrders')
        self.assertEqual(response.json, {'data': [{'id': '123'}]})

    @patch('flask_server.my_app')
    def test_cancelOpenOrders(self, mock_my_app):
        mock_my_app.cancel_open_order.return_value = {'status': 'success'}
        response = self.client.get('/cancelOpenOrders?order_id=123')
        self.assertEqual(response.json, {'data': {'status': 'success'}})

    @patch('flask_server.my_app')
    def test_modifyOpenOrders(self, mock_my_app):
        mock_my_app.modify_open_order.return_value = {'status': 'modified'}
        response = self.client.get('/modifyOpenOrders?order_id=123&quantity=1&price=100&order_type=LIMIT&trigger=99&leg=ENTRY&validity=DAY&disclosed=1')
        self.assertEqual(response.json, {'data': {'status': 'modified'}})

    @patch('flask_server.my_app')
    def test_get_order_status(self, mock_my_app):
        mock_my_app.get_order_status.return_value = {'status': 'COMPLETE'}
        response = self.client.get('/orderstatus?order_id=123')
        self.assertEqual(response.json, {'status': 'COMPLETE'})

    @patch('flask_server.my_app')
    def test_getOpenPosition(self, mock_my_app):
        mock_my_app.get_open_positions.return_value = {'positions': []}
        response = self.client.get('/openPosition')
        self.assertEqual(response.json, {'positions': []})

    @patch('flask_server.my_app')
    def test_closePosition(self, mock_my_app):
        mock_my_app.closeAllPositions.return_value = {'status': 'closed'}
        response = self.client.get('/closePosition?security_id=123&exchange_segment=NSE&transaction_type=SELL&quantity=1&product_type=INTRA')
        self.assertEqual(response.json, {'status': 'closed'})

    @patch('flask_server.my_app')
    def test_placeOrder(self, mock_my_app):
        mock_my_app.placeOrder.return_value = {'status': 'success', 'data': {'orderId': '456'}}
        response = self.client.get('/placeOrder?index=NIFTY&option_type=CE&transaction_type=BUY&client_order_id=123&socket_client_id=456&dhan_client_id=789&product_type=INTRA')
        self.assertEqual(response.json, {'status': 'success', 'data': {'orderId': '456'}, 'client_order_id': '123'})

    @patch('flask_server.my_app')
    def test_add_trade_level(self, mock_my_app):
        mock_my_app.add_trade_level.return_value = {'id': '123'}
        response = self.client.get('/addLevels?index_name=NIFTY&option_type=CE&price_level=15000&dhan_client_id=789&trade_confidence=0.8&id=123')
        self.assertEqual(response.json, {'data': {'id': '123'}})

    @patch('flask_server.my_app')
    def test_get_trade_level(self, mock_my_app):
        mock_my_app.get_trade_levels.return_value = [{'level': 15000}]
        response = self.client.get('/getLevels?dhan_client_id=789')
        self.assertEqual(response.json, {'data': '[{"level": 15000}]'})

    @patch('flask_server.my_app')
    def test_delete_trade_level(self, mock_my_app):
        response = self.client.get('/deleteLevels?index_name=NIFTY&price_level=15000&dhan_client_id=789')
        self.assertEqual(response.json, {'data': {'result': 'success'}})

    @patch('flask_server.my_app')
    def test_fundLimit(self, mock_my_app):
        mock_my_app.getFundLimit.return_value = {'available': 10000}
        response = self.client.get('/fundLimits')
        self.assertEqual(response.json, {'available': 10000})

    @patch('flask_server.my_app')
    def test_index_rule(self, mock_my_app):
        mock_my_app.get_index_rules.return_value = {'rule': 'test'}
        response = self.client.get('/indexRule?dhan_client_id=789')
        self.assertEqual(response.json, {'data': {'rule': 'test'}})

    @patch('flask_server.my_app')
    def test_kill_switch_rule(self, mock_my_app):
        mock_my_app.get_kill_switch_rule.return_value = {'kill_switch': True}
        response = self.client.get('/killSwitchRule?dhan_client_id=789')
        self.assertEqual(response.json, {'data': {'kill_switch': True}})

if __name__ == '__main__':
    unittest.main()