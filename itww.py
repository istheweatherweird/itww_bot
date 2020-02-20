import requests
import csv
from pandas import Timestamp, Timedelta
from utils import list_average

DATA_URL = 'https://www.istheweatherweird.com/istheweatherweird-data-hourly'
STATIONS_URL = '{}/csv/stations.csv'.format(DATA_URL)

CITY = 'Chicago'
START_TIME = Timestamp.utcnow().replace(microsecond=0) - Timedelta(days=1)
END_TIME = Timestamp.utcnow().replace(microsecond=0)


def get_tweet():
    place = get_place(CITY)

    daily_temp = get_daily_temp(place)
    historical_temps = get_historical_temps(place)

    tweet = write_tweet(daily_temp, historical_temps)

    return tweet


def get_place(city):
    response = requests.get(STATIONS_URL)
    reader = csv.DictReader(
        line.decode('utf-8') for line in response.iter_lines()
    )

    for place_dict in reader:
        if place_dict['place'] == city:
            return place_dict


def get_observations(place):
    nws_request_url ='https://api.weather.gov/stations/{}/observations'.format(
        place['ICAO']
    )
    params = {
        'start': START_TIME.isoformat(),
        'end': END_TIME.isoformat(),
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
def get_daily_temp(place):
    observations = get_observations(place)

    temps = [temp for (timestamp, temp) in observations]
    average = list_average(temps)
    average_fahrenheit = average * 1.8 + 32

    return average_fahrenheit

# This currently calculates the average temperature for the current day
def get_historical_temps(place):
    historical_data_url = "{data_url}/csv/{id}/{month}{day}.csv".format(
        data_url=DATA_URL,
        id=place['USAF'] + "-" + place['WBAN'],
        month='{:02}'.format(END_TIME.month),
        day='{:02}'.format(END_TIME.day)
    )
    response = requests.get(historical_data_url)
    lines = (line.decode('utf-8') for line in response.iter_lines())
    reader = csv.reader(lines)
    next(reader, None)  # skip the headers

    temps_by_year = {}
    for line in reader:
        [year, hour, temp] = list(line)
        try:
            temps_by_year[year] = temps_by_year[year] + [int(temp)]
        except KeyError:
            temps_by_year[year] = [int(temp)]

    average_temps = {year: (list_average(temps) * 0.18 + 32) for year, temps in temps_by_year.items()}

    return average_temps


def write_tweet(daily_temp, historical_temps):
    return "The average temperature in Chicago for the last day was {}ºF.".format(round(daily_temp))

print(get_tweet())
