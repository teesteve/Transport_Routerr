import requests
import openrouteservice
from openrouteservice import convert

class RouteGenerator:
    """ Handles geocoding and route generation using the OpenRouteService API"""
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = openrouteservice.Client(key=api_key)

    def geocode(self, place_name):
        """ Converts a human-readable place name to geographical coordinates,
            Returns a (lat,lon) tuple or None if geocoding fails"""
        try:
            url = "https://api.openrouteservice.org/geocode/search"
            headers = {
                "Authorization": self.api_key
            }
            params = {
                "text": place_name,
                "boundary.country": "NG",
                "layers": "venue,address,locality"
            }
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            coords = data['features'][0]['geometry']['coordinates']
            return coords[1], coords[0]  # lat, lon
        except Exception as e:
            print(f"Geocoding error for '{place_name}':", e)
            return None

    def get_route_info(self, start_coords, end_coords, mode='driving-car'):
        """ Fetches routing information between two coordiante points.
            Returns tuple: distance(km), duration(min), route coordinates, steps"""
        try:
            coordinates = [start_coords[::-1], end_coords[::-1]]  # lon, lat
            response = self.client.directions(
                coordinates=coordinates,
                profile=mode,
                format='json',
                geometry=True  # Ensure geometry is included
            )
            summary = response['routes'][0]['summary']
            geometry = response['routes'][0]['geometry']
            steps = response['routes'][0]['segments'][0]['steps']

            decoded = convert.decode_polyline(geometry)
            route_coords = decoded['coordinates']  # [[lon, lat], ...]

            duration = summary['duration'] / 60  # minutes
            distance = summary['distance'] / 1000  # km
            return round(distance, 2), round(duration, 2), route_coords, steps
        except Exception as e:
            print("Routing error:", e)
            return None, None, None, None





