import json
import math
import os
import networkx as nx

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'trotro_routes.json')

def haversine_km(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points on the earth in kilometers.
    """
    R = 6371.0  # Earth radius in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class TrotroRouter:
    def __init__(self, data_file=DATA_PATH):
        with open(data_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        self.stops = {stop['id']: stop for stop in self.data['stops']}
        self.routes = {route['id']: route for route in self.data['routes']}
        self._build_graph()

    def _build_graph(self):
        """
        Build a multi-modal transport graph where nodes are stops and edges represent trotro legs.
        """
        self.graph = nx.DiGraph()
        for stop_id, stop in self.stops.items():
            self.graph.add_node(stop_id, **stop)

        # Add directed edges for consecutive stops on trotro routes
        for route_id, route in self.routes.items():
            stops_list = route['stops']
            num_segments = len(stops_list) - 1
            if num_segments <= 0:
                continue

            fare_per_segment = route['fare_ghs'] / num_segments
            time_per_segment = route['est_time_mins'] / num_segments
            waypoints = route.get('waypoints', [])

            # Forward and backward direction (trotros run both ways)
            for i in range(num_segments):
                u, v = stops_list[i], stops_list[i+1]
                u_stop, v_stop = self.stops[u], self.stops[v]
                dist_km = haversine_km(u_stop['lat'], u_stop['lng'], v_stop['lat'], v_stop['lng'])

                # Edge from u to v
                self.graph.add_edge(u, v, route_id=route_id, route_name=route['name'],
                                    fare=fare_per_segment, time=time_per_segment, dist_km=dist_km,
                                    waypoints=waypoints)
                # Edge from v to u
                self.graph.add_edge(v, u, route_id=route_id, route_name=route['name'],
                                    fare=fare_per_segment, time=time_per_segment, dist_km=dist_km,
                                    waypoints=list(reversed(waypoints)) if waypoints else [])

    def find_nearest_stop(self, lat, lng, limit=5, max_dist_km=None):
        """
        Find closest trotro stops to a given coordinate.
        Optionally filter by maximum distance in kilometers.
        """
        stop_distances = []
        for stop_id, stop in self.stops.items():
            dist = haversine_km(lat, lng, stop['lat'], stop['lng'])
            if max_dist_km and dist > max_dist_km:
                continue
            stop_distances.append({
                "stop": stop,
                "distance_km": round(dist, 3),
                "walking_time_mins": round((dist / 4.5) * 60, 1) # Assumes 4.5 km/h walking speed
            })
        stop_distances.sort(key=lambda x: x['distance_km'])
        return stop_distances[:limit]

    def find_route_by_coords(self, start_lat, start_lng, end_lat, end_lng):
        """
        Find optimal trotro journey given current user GPS coordinates and target destination GPS coordinates.
        """
        origin_stops = self.find_nearest_stop(start_lat, start_lng, limit=3)
        dest_stops = self.find_nearest_stop(end_lat, end_lng, limit=3)

        if not origin_stops or not dest_stops:
            return {"error": "No nearby trotro stations found within reasonable range."}

        best_journey = None
        min_total_cost = float('inf')

        for orig in origin_stops:
            for dest in dest_stops:
                orig_id = orig['stop']['id']
                dest_id = dest['stop']['id']

                # Same stop
                if orig_id == dest_id:
                    total_time = orig['walking_time_mins'] + dest['walking_time_mins']
                    if orig['distance_km'] + dest['distance_km'] < 5.0:
                        journey = {
                            "type": "walk_only",
                            "pickup_stop": orig['stop'],
                            "dropoff_stop": dest['stop'],
                            "walk_to_pickup_km": orig['distance_km'],
                            "walk_to_pickup_mins": orig['walking_time_mins'],
                            "walk_from_dropoff_km": dest['distance_km'],
                            "walk_from_dropoff_mins": dest['walking_time_mins'],
                            "trotro_legs": [],
                            "total_fare_ghs": 0.0,
                            "total_time_mins": total_time,
                            "path_coords": [
                                {"lat": start_lat, "lng": start_lng},
                                {"lat": orig['stop']['lat'], "lng": orig['stop']['lng']},
                                {"lat": end_lat, "lng": end_lng}
                            ]
                        }
                        if total_time < min_total_cost:
                            min_total_cost = total_time
                            best_journey = journey
                        continue

                if nx.has_path(self.graph, orig_id, dest_id):
                    try:
                        path = nx.shortest_path(self.graph, orig_id, dest_id, weight='time')

                        trotro_legs = []
                        total_fare = 0.0
                        total_trotro_time = 0.0
                        total_trotro_dist = 0.0

                        path_coords = [{"lat": start_lat, "lng": start_lng}]
                        current_leg = None

                        for i in range(len(path) - 1):
                            u, v = path[i], path[i+1]
                            edge = self.graph[u][v]
                            u_stop = self.stops[u]
                            v_stop = self.stops[v]

                            # Append start node
                            if not path_coords or path_coords[-1] != {"lat": u_stop['lat'], "lng": u_stop['lng']}:
                                path_coords.append({"lat": u_stop['lat'], "lng": u_stop['lng']})

                            # Append edge waypoints if available
                            if edge.get('waypoints'):
                                for wp in edge['waypoints']:
                                    if path_coords[-1] != wp:
                                        path_coords.append(wp)

                            if path_coords[-1] != {"lat": v_stop['lat'], "lng": v_stop['lng']}:
                                path_coords.append({"lat": v_stop['lat'], "lng": v_stop['lng']})

                            # Merge consecutive edges on the same trotro line
                            if current_leg and current_leg['route_id'] == edge['route_id']:
                                current_leg['dropoff_stop'] = v_stop
                                current_leg['fare_ghs'] += edge['fare']
                                current_leg['est_time_mins'] += edge['time']
                                current_leg['dist_km'] += edge['dist_km']
                                current_leg['intermediate_stops'].append(v_stop['name'])
                            else:
                                if current_leg:
                                    trotro_legs.append(current_leg)
                                current_leg = {
                                    "route_id": edge['route_id'],
                                    "route_name": edge['route_name'],
                                    "pickup_stop": u_stop,
                                    "dropoff_stop": v_stop,
                                    "fare_ghs": edge['fare'],
                                    "est_time_mins": edge['time'],
                                    "dist_km": edge['dist_km'],
                                    "intermediate_stops": [v_stop['name']]
                                }

                            total_fare += edge['fare']
                            total_trotro_time += edge['time']
                            total_trotro_dist += edge['dist_km']

                        if current_leg:
                            trotro_legs.append(current_leg)

                        path_coords.append({"lat": end_lat, "lng": end_lng})

                        total_time = orig['walking_time_mins'] + total_trotro_time + dest['walking_time_mins']

                        if total_time < min_total_cost:
                            min_total_cost = total_time
                            best_journey = {
                                "type": "trotro_route",
                                "pickup_stop": orig['stop'],
                                "dropoff_stop": dest['stop'],
                                "walk_to_pickup_km": orig['distance_km'],
                                "walk_to_pickup_mins": orig['walking_time_mins'],
                                "walk_from_dropoff_km": dest['distance_km'],
                                "walk_from_dropoff_mins": dest['walking_time_mins'],
                                "trotro_legs": trotro_legs,
                                "total_fare_ghs": round(total_fare, 2),
                                "total_trotro_dist_km": round(total_trotro_dist, 2),
                                "total_time_mins": round(total_time, 1),
                                "path_coords": path_coords
                            }
                    except nx.NetworkXNoPath:
                        continue

        if not best_journey:
            return {"error": "No trotro route found connecting those locations. Try selecting stops nearer to major terminals."}

        return best_journey

    def find_route_by_stop_ids(self, origin_stop_id, dest_stop_id):
        """
        Find route when user picks specific stops from dropdown/search.
        """
        if origin_stop_id not in self.stops or dest_stop_id not in self.stops:
            return {"error": "Invalid origin or destination stop ID"}

        orig_stop = self.stops[origin_stop_id]
        dest_stop = self.stops[dest_stop_id]

        return self.find_route_by_coords(orig_stop['lat'], orig_stop['lng'], dest_stop['lat'], dest_stop['lng'])
