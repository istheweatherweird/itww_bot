import requests
import csv
from pandas import Timestamp, Timedelta
from utils import list_average, get_reader

DATA_URL = 'https://www.istheweatherweird.com/istheweatherweird-data-hourly'
STATIONS_URL = '{}/csv/stations.csv'.format(DATA_URL)

CITY = 'Chicago'
START_TIME = Timestamp.utcnow().replace(microsecond=0) - Timedelta(days=1)
END_TIME = Timestamp.utcnow().replace(microsecond=0)


def get_tweets():
    place = get_place(CITY)
    local_time = END_TIME.tz_convert(place['TZ'])

    tweets = []

    # check if 6pm <= current local time < 7pm
    # this is intended to run every hour through the Heroku scheduler
    if local_time.floor(freq='h').hour == 18:
        daily_temp = get_daily_temp(place)
        historical_temps = get_historical_temps(place, local_time)

        tweet = write_tweet(place, local_time, daily_temp, historical_temps)
        tweets += [tweet]

        if local_time.day_name() == 'Sunday':
            print("Calculate weekly average here TK")

    return tweets


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

def get_historical_temps(place, local_time):
    place_id = place['USAF'] + "-" + place['WBAN']

    current_day_url = "{data_url}/csv/{id}/{month}{day}.csv".format(
        data_url=DATA_URL,
        id=place_id,
        month='{:02}'.format(END_TIME.month),
        day='{:02}'.format(END_TIME.day)
    )

    current_day = get_reader(current_day_url)

    # we want 24 hours of weather data starting ending at 6pm today local time
    tz_offset = int(local_time.utcoffset().total_seconds() / 3600)
    additional_hours_needed = -6 - tz_offset

    if additional_hours_needed < 0:
        # we need to grab the previous day's sheet as well and take the last
        # additional_hours_needed hours for each year
        previous_day = END_TIME - Timedelta(days=1)
        previous_day_url = "{data_url}/csv/{id}/{month}{day}.csv".format(
            data_url=DATA_URL,
            id=place_id,
            month='{:02}'.format(previous_day.month),
            day='{:02}'.format(previous_day.day)
        )

        previous_day_filtered = [
            row for row
            in get_reader(previous_day_url)
            if int(row[1]) >= (24 + additional_hours_needed)
        ]

        current_day_filtered = [
            row for row
            in get_reader(previous_day_url)
            if int(row[1]) < (24 + additional_hours_needed)
        ]

        adjusted_day = previous_day_filtered + current_day_filtered

    elif additional_hours_needed > 0:
        # we need to grab the next day's sheet as well and take the first
        # additional_hours_needed hours for each year
        next_day = END_TIME + Timedelta(days=1)
        next_day_url = "{data_url}/csv/{id}/{month}{day}.csv".format(
            data_url=DATA_URL,
            id=place_id,
            month='{:02}'.format(next_day.month),
            day='{:02}'.format(next_day.day)
        )

        next_day_filtered = [
            row for row
            in get_reader(next_day_url)
            if int(row[1]) <= additional_hours_needed
        ]

        current_day_filtered = [
            row for row
            in get_reader(next_day_url)
            if int(row[1]) > additional_hours_needed
        ]

        adjusted_day = next_day_filtered + current_day_filtered

    else:
        # use the current day's sheet
        adjusted_day = current_day

    temps_by_year = {}
    for row in adjusted_day:
        [year, hour, temp] = list(row)
        try:
            temps_by_year[year] = temps_by_year[year] + [int(temp)]
        except KeyError:
            temps_by_year[year] = [int(temp)]

    historical_average_temps = {
        year: (list_average(temps) * 0.18 + 32)
        for year, temps in temps_by_year.items()
    }

    return historical_average_temps


def write_tweet(place, local_time, daily_temp, historical_temps):
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
        'pretty typical',
        'a bit weird',
        'weird',
        'very weird',
    ]

    comparisons = [
        ['colder', 'coldest'],
        ['warmer', 'warmest']
    ]

    emoji_list = ['❄️','🔥']

    daily_temp = round(daily_temp)
    month = local_time.month_name()
    day = local_time.day

    weirdness = weirdness_levels[weirdness_level]
    comparison = comparisons[warm_bool][(weirdness == 3)]

    if weirdness_level:
        emoji = emoji_list[warm_bool] * weirdness_level + ' '
    else:
        emoji = ''

    sentence1 = '{emoji}The weather in {city} is {weirdness} today.'.format(
        emoji=emoji,
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

# for testing in local development
print(get_tweets())
