from typing import Dict, List
import requests
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Famous locations with their coordinates and descriptions
SAMPLE_LOCATIONS: List[Dict] = [
    {
        "name": "Eiffel Tower",
        "latitude": 48.858370,
        "longitude": 2.294481,
        "description": "Famous iron lattice tower in Paris, France",
        "heading": 70,
        "pitch": 0
    },
    {
        "name": "Times Square",
        "latitude": 40.758896,
        "longitude": -73.985130,
        "description": "Major commercial intersection in New York City",
        "heading": 180,
        "pitch": 10
    },
    {
        "name": "Taj Mahal",
        "latitude": 27.175277,
        "longitude": 78.042128,
        "description": "Famous ivory-white marble mausoleum in Agra, India",
        "heading": 0,
        "pitch": 0
    },
    {
        "name": "Colosseum",
        "latitude": 41.890251,
        "longitude": 12.492373,
        "description": "Ancient amphitheatre in Rome, Italy",
        "heading": 90,
        "pitch": 0
    },
    {
        "name": "Christ the Redeemer",
        "latitude": -22.951916,
        "longitude": -43.210487,
        "description": "Art Deco statue of Jesus Christ in Rio de Janeiro, Brazil",
        "heading": 120,
        "pitch": 10
    },
    {
        "name": "Machu Picchu",
        "latitude": -13.163141,
        "longitude": -72.545870,
        "description": "15th-century Inca citadel in Peru",
        "heading": 45,
        "pitch": 0
    },
    {
        "name": "Sydney Opera House",
        "latitude": -33.856784,
        "longitude": 151.215297,
        "description": "Multi-venue performing arts centre in Sydney, Australia",
        "heading": 330,
        "pitch": 0
    },
    {
        "name": "Petra",
        "latitude": 30.328960,
        "longitude": 35.444832,
        "description": "Ancient city in Jordan",
        "heading": 90,
        "pitch": 0
    },
    {
        "name": "Great Wall of China",
        "latitude": 40.431908,
        "longitude": 116.570374,
        "description": "Series of fortification systems in China",
        "heading": 270,
        "pitch": 0
    },
    {
        "name": "Grand Canal Venice",
        "latitude": 45.440847,
        "longitude": 12.332235,
        "description": "Main water-traffic corridor in Venice, Italy",
        "heading": 180,
        "pitch": 0
    }
]

class LocationManager:
    def __init__(self):
        self.api_key = GOOGLE_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api/streetview"
        self.locations = SAMPLE_LOCATIONS

    def get_street_view_image(self, location: Dict) -> bytes:
        """Fetch Street View image for a given location"""
        params = {
            "size": "600x400",
            "location": f"{location['latitude']},{location['longitude']}",
            "fov": 80,
            "heading": location["heading"],
            "pitch": location["pitch"],
            "key": self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Failed to fetch image for {location['name']}: {response.status_code}")

    def test_all_locations(self):
        """Test all locations to ensure they return valid Street View images"""
        for location in self.locations:
            try:
                image_data = self.get_street_view_image(location)
                print(f"✅ Successfully fetched image for {location['name']}")
            except Exception as e:
                print(f"❌ Failed to fetch image for {location['name']}: {str(e)}")

    def initialize_database(self, db_manager):
        """Initialize the database with sample locations"""
        for location in self.locations:
            db_manager.add_location(
                location["name"],
                location["latitude"],
                location["longitude"],
                location["description"]
            )
