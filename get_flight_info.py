import requests
from datetime import datetime
import logging

# TODO Valuable Information

# Set up logging
logging.basicConfig(level=logging.INFO)

# Get current date
NOW = datetime.now()

# Additional Variables
DATE = NOW.strftime("%d/%m/%Y")
END_DATE = NOW.strftime("25/10/%Y")
SHEET_EP = "https://api.sheety.co/9aad2a16529f732d9919e82247b52109/flightLocations/prices"
API_EP = "https://api.tequila.kiwi.com/v2/search?"
API_KEY = "asQZPK_0HTtlRyTaUFWiDrZctWAXm4RL"
BITLY_ACCESS_TOKEN = 'de95b203a777f2bf02735c7055ce72c04393245d'

# Flight request information
HEADER = {
    "accept": "application/json",
    "apikey": API_KEY
}

JSON_TEMPLATE = {
    "fly_from": "JNB",
    "fly_to": "",  # Placeholder for the IATA code
    "date_from": DATE,
    "date_to": END_DATE,
    "nights_in_dst_from": 7,
    "nights_in_dst_to": 14,
    "flight_type": "round",
    "ret_from_diff_city": False,
    "ret_to_diff_city": False,
    "selected_cabins": "C",
    "mix_with_cabins": "W",
    "only_working_days": False,
    "only_weekends": True,
    "partner_market": "za",
    "curr": "ZAR",
    "max_stopovers": 2,
    "max_sector_stopovers": 2,
    "limit": 10
}


def import_location_data():
    with requests.get(url=SHEET_EP) as response:
        if response.status_code == 200:
            json_data = response.json()
            # Do something with the object
            city_list = json_data['prices']  # 9 Cities
            city_code = {item['city']: item['iataCode'] for item in city_list}
            city_price = {item['city']: item['lowestPrice'] for item in city_list}
            return city_code, city_price

        else:
            logging.error(f"Failed to fetch spreadsheet data. Error: {response.text}")


# TODO Create Class
class FlightInfo:
    def __init__(self):
        self.city_code, self.city_price = import_location_data()
        self.flight_data_dict = self.format_flight_data()
        self.city_data_dict = self.compare_prices()

    # Format and prepare flight data
    def format_flight_data(self):
        flight_data_dict = {}
        for city, iata_code in self.city_code.items():
            json_data = JSON_TEMPLATE.copy()
            json_data["fly_to"] = iata_code

            with requests.get(url=API_EP, headers=HEADER, params=json_data) as response:
                if response.status_code == 200:
                    flight_data = response.json()
                    # Store the flight data for the current city in the dictionary
                    flight_data_dict[city] = flight_data

                else:
                    logging.error(f"Error fetching flight data for {city}. Error: {response.text}")
        return flight_data_dict

    # Shorten "deep link" in flight information
    def shorten_url(self, url, access_token):
        api_url = 'https://api-ssl.bitly.com/v4/shorten'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        data = {
            'long_url': url
        }
        response = requests.post(api_url, headers=headers, json=data)
        if response.status_code == 200:
            response_data = response.json()
            return response_data['link']  # Retrieve the shortened URL instead of 'id'
        else:
            logging.error(f"Failed to shorten URL. Error: {response.text}")
            return None

    # Compare flight data and return city information as results
    def compare_prices(self):
        result = {}

        for city, flight_data_dict in self.flight_data_dict.items():
            data_list = flight_data_dict.get("data", [])
            result[city] = []  # Initialize an empty list for each city

            for data_dict in data_list[:10]:
                # original_url = data_dict.get('deep_link', '')
                # short_url = self.shorten_url(original_url, BITLY_ACCESS_TOKEN)
                price = data_dict.get("price", float('inf'))
                low_price = self.city_price.get(city, float('inf'))
                local_departure = data_dict.get("local_departure")
                local_arrival = data_dict.get("local_arrival")
                result[city].append({
                    # 'short_url': short_url,
                    'price': price,
                    'low_price': low_price,
                    'local_departure': local_departure,
                    'local_arrival': local_arrival
                })
        return result

    def get_city_data_dict(self):
        print(self.city_data_dict)
        return self.city_data_dict
