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

    historical_average_temps = {year: (list_average(temps) * 0.18 + 32) for year, temps in temps_by_year.items()}

    return historical_average_temps


def write_tweet(daily_temp, historical_temps):
    total_years = len(historical_temps)
    warmer_years = [temp for year, temp in historical_temps.items() if temp < daily_temp]
    percent_warmer = len(warmer_years) / len(historical_temps) * 100

    warm_bool = percent_warmer >= 50

    if warm_bool:
        percent_relative = round(percent_warmer)
    else:
        percent_relative = round(100 - percent_warmer)

    record = False

    if percent_relative >= 97.5:
        weirdness_level = 3
        record = True
    elif percent_relative >= 90:
        weirdness_level = 2
    elif percent_relative >= 80:
        weirdness_level = 1
    else:
        weirdness_level = 0

    weirdness_levels = [
        'typical',
        'a bit weird',
        'weird',
        'very weird',
    ]

    comparisons = [
        ['colder', 'coldest'],
        ['warmer', 'warmest']
    ]

    daily_temp = round(daily_temp)
    month = END_TIME.month_name()
    day = END_TIME.day

    weirdness = weirdness_levels[weirdness_level]
    comparison = comparisons[warm_bool][(weirdness == 3)]

    sentence1 = 'The weather in {city} is {weirdness} today.'.format(
        city=CITY,
        weirdness=weirdness
    )

    if not record:
        sentence2 = 'It\'s {daily_temp}ºF, {comparison} than {percent_relative}% of {month} {day} temperatures on record.'.format(
            daily_temp=daily_temp,
            comparison=comparison,
            percent_relative=percent_relative,
            month=month,
            day=day,
        )
    else:
        sentence2 = 'It\'s {daily_temp}ºF, the {comparison} {month} {day} temperature on record.'.format(
            daily_temp=daily_temp,
            comparison=comparison,
            percent_relative=percent_relative,
            month=month,
            day=day,
        )

    return '{sentence1} {sentence2}'.format(
        sentence1=sentence1,
        sentence2=sentence2,
    )

print(get_tweet())
