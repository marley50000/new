import unittest
from trotro_router import TrotroRouter, haversine_km

class TestTrotroRouter(unittest.TestCase):
    def setUp(self):
        self.router = TrotroRouter()

    def test_haversine_distance(self):
        # Distance between Kwame Nkrumah Circle (5.5586, -0.2137) and UG Legon (5.6515, -0.1837)
        dist = haversine_km(5.5586, -0.2137, 5.6515, -0.1837)
        self.assertGreater(dist, 10.0)
        self.assertLess(dist, 15.0)

    def test_find_nearest_stop(self):
        # Coordinates near Circle
        nearest = self.router.find_nearest_stop(5.5580, -0.2130, limit=3)
        self.assertEqual(len(nearest), 3)
        self.assertEqual(nearest[0]['stop']['id'], 'acc_circle')

    def test_direct_route(self):
        # Madina (5.6698, -0.1662) to Circle (5.5586, -0.2137)
        journey = self.router.find_route_by_coords(5.6698, -0.1662, 5.5586, -0.2137)
        self.assertNotIn("error", journey)
        self.assertEqual(journey["pickup_stop"]["id"], "acc_madina")
        self.assertEqual(journey["dropoff_stop"]["id"], "acc_circle")
        self.assertGreater(journey["total_fare_ghs"], 0)
        self.assertTrue(len(journey["trotro_legs"]) >= 1)

    def test_transfer_route(self):
        # Route from Adenta (5.7112, -0.1585) to Tema Community 1 (5.6450, -0.0030)
        journey = self.router.find_route_by_coords(5.7112, -0.1585, 5.6450, -0.0030)
        self.assertNotIn("error", journey)
        self.assertGreater(len(journey["path_coords"]), 2)

if __name__ == '__main__':
    unittest.main()
