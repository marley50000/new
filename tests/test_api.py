import unittest
import json
from app import app

class TestFlaskEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_get_stops(self):
        response = self.client.get('/api/trotro/stops')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(data['count'], 0)

    def test_get_routes(self):
        response = self.client.get('/api/trotro/routes')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(data['count'], 0)

    def test_nearest_stop_endpoint(self):
        response = self.client.get('/api/trotro/nearest_stop?lat=5.5586&lng=-0.2137')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['nearest_stops'][0]['stop']['id'], 'acc_circle')

    def test_calculate_route_endpoint(self):
        payload = {
            "origin": {"lat": 5.6698, "lng": -0.1662},
            "destination": {"lat": 5.5586, "lng": -0.2137}
        }
        response = self.client.post('/api/trotro/route', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('journey', data)
        self.assertEqual(data['journey']['pickup_stop']['id'], 'acc_madina')

if __name__ == '__main__':
    unittest.main()
