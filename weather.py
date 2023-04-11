import json
import logging
import shelve
from datetime import datetime

import requests

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')


class Weather:
    """
    This is a class that receives a location either in words, or in longitude and latitude to be able to provide related
    weather information
    """

    def __init__(self, city: str = None, latitude: float = None, longitude: float = None):

        """
        Initialize the class with the required api keys, endpoints, and location
        """

        self.api_key = shelve.open('keys/api_keys')
        self.weather_api_key = self.api_key['weather_api']
        logging.debug(f'The api key in use is {self.weather_api_key}')
        self.endpoints = 'http://api.weatherapi.com/v1/forecast.json'

        if city:
            self.location = city
        elif latitude and longitude:
            self.location = f'{latitude},{longitude}'
        else:
            raise Exception('Either the City name or its longitude and latitude must be provided')
        logging.debug(f'The location used in the request is {self.location}')

    @staticmethod
    def _time():
        """Gets the specific hour of the day"""
        current_time = datetime.now().time()
        clean_time = f'%02d' % current_time.hour
        return clean_time

    def get_forecast(self):
        """Returns a 6 hourly weather forecast for any specific location"""
        params = {
            'key': self.weather_api_key,
            'q': self.location,
            'days': 1,
        }

        logging.debug(f'The parameters for the request are {params}')

        response = requests.get(self.endpoints, params=params)
        response.raise_for_status()

        logging.debug(f'The status code for the request is {response.status_code}')

        weather_forecast = response.json()["forecast"]["forecastday"][0]['hour']
        total_forecast = []
        for prediction in range(len(weather_forecast)):

            chosen_forecast = weather_forecast[prediction]
            hour = chosen_forecast["time"].split(' ')[1].split(':')[0]

            if int(self._time()) <= int(hour) < int(self._time()) + 6:
                temp_c = chosen_forecast["temp_c"]
                condition = chosen_forecast["condition"]["text"]
                wind_speed = chosen_forecast["wind_kph"]

                if chosen_forecast["will_it_rain"] == 0:
                    rain = 'No'
                else:
                    rain = 'Yes'
                clean_forecast = {'hour': f'{hour}:00', 'temp_c': temp_c, 'condition': condition,
                                  'wind_speed': wind_speed,
                                  'rain': rain}

                total_forecast.append(clean_forecast)

        return total_forecast


if __name__ == '__main__':
    test = Weather(longitude=-0.22, latitude=5.55)
    result = test.get_forecast()
    with open('forecast.json', mode='w') as json_file:
        json.dump(result, json_file, indent=4)
