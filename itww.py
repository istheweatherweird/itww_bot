import requests
import csv
from pandas import Timestamp, Timedelta

DATA_URL = 'https://www.istheweatherweird.com/istheweatherweird-data-hourly'
STATIONS_URL = DATA_URL + '/csv/stations.csv'

CITY = 'Chicago'
START_TIME = (Timestamp.utcnow().replace(microsecond=0) - Timedelta(days=1)).isoformat()
END_TIME = Timestamp.utcnow().replace(microsecond=0).isoformat()

def get_tweet():
    place = get_place(CITY)
    observations = get_observations(place)
    average_temp = round(get_average_temp(observations))
    tweet = "The average temperature in Chicago for the last day was {}ºF.".format(average_temp)

    return tweet


def get_place(city):
    place_csv = requests.get(STATIONS_URL)
    reader = csv.DictReader(
        line.decode('utf-8') for line in place_csv.iter_lines()
    )

    for place_dict in reader:
        if place_dict['place'] == city:
            return place_dict


def get_observations(place):
    nws_request_url ='https://api.weather.gov/stations/{}/observations'.format(
        place['ICAO']
    )
    params = {
        'start': START_TIME,
        'end': END_TIME,
    }
    response_json = requests.get(nws_request_url, params=params).json()

    try:
        observations = [
            (observation['properties']['timestamp'],
            observation['properties']['temperature']['value'])
            for observation in response_json['features']
        ]
    except KeyError:
        observations = []

    return observations

# for now this is a simple average.
# however, the observations aren't necessarily spaced equally throughout
# the day. do something more sophisticated later!
def get_average_temp(observations):
    temps = [temp for (timestamp, temp) in observations]
    average = sum(temps) / len(temps)
    average_fahrenheit = average * 1.8 + 32

    return average_fahrenheit
