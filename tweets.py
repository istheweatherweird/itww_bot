import requests
import csv
from pandas import Timestamp, Timedelta, read_csv, date_range, concat
from utils import list_average, get_reader

DATA_URL = 'https://www.istheweatherweird.com/istheweatherweird-data-hourly'
STATIONS_URL = '{}/csv/stations.csv'.format(DATA_URL)

def get_tweets(city):
    place = get_place(city)

    # UTC values for 6pm local time yesterday - 6pm local time today
    end_time = Timestamp.today(tz=place['TZ']).replace(hour=18).floor(freq='h').tz_convert(tz='UTC')
    start_time = end_time - Timedelta(days=1)

    tweets = []

    daily_temp = get_daily_temp(place, start_time, end_time)
    historical_temps = get_historical_temps(place, start_time, end_time)

    tweet = write_tweet(place, end_time, daily_temp, historical_temps)
    tweets += [tweet]

    return tweets


def get_place(city):
    response = requests.get(STATIONS_URL)
    reader = csv.DictReader(
        line.decode('utf-8') for line in response.iter_lines()
    )

    for place_dict in reader:
        if place_dict['place'] == city:
            return place_dict


def get_observations(place, start_time, end_time):
    nws_request_url ='https://api.weather.gov/stations/{}/observations'.format(
        place['ICAO']
    )
    params = {
        'start': start_time.isoformat(),
        'end': end_time.isoformat(),
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
def get_daily_temp(place, start_time, end_time):
    observations = get_observations(place, start_time, end_time)

    temps = [temp for (timestamp, temp) in observations if temp]
    average = list_average(temps)
    average_fahrenheit = average * 1.8 + 32

    return average_fahrenheit

def get_historical_temps(place, start_time, end_time):
    place_id = place['USAF'] + '-' + place['WBAN']
    # first get full days of temps
    df = _get_date_range_temps(place_id, 
            start.date(), end.date())
    # filter to necessary hours
    return df[df.current_date.between(start, end)]

def write_tweet(place, end_time, daily_temp, historical_temps):
    year_warmer = historical_temps.groupby('year').temp.mean() > daily_temp
    percent_warmer = year_warmer.mean() * 100

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
    month = end_time.tz_convert(tz=place['TZ']).month_name()
    day = end_time.tz_convert(tz=place['TZ']).day

    weirdness = weirdness_levels[weirdness_level]
    comparison = comparisons[warm_bool][(weirdness == 3)]

    if weirdness_level:
        emoji = emoji_list[warm_bool] * weirdness_level + ' '
    else:
        emoji = ''

    sentence1 = '{emoji}The weather in {city} is {weirdness} today.'.format(
        emoji=emoji,
        city=place['place'],
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

def _get_date_range_temps(place_id, start_time, end_time):
    """
    Concatenate observations for a range of month-days
    Args:
        place_id: USAF-WBAN string
        start: start date whose month-day will be used
        end: end date whose month-day will be used
    Returns: a dataframe with temp and current_date columns
    """
    dates = date_range(start, end, freq='D')
    print(dates)
    return concat((
        _get_month_day_temps(place_id, date.month, date.day, date.year)
        for date in dates))

def _get_month_day_temps(place_id, month, day, current_year):
    """
    Get historical temperatures for the given month-day.
    Adds a current_date column which is a timestamp with 
        the observation's month, day, and hour but the current year.
        This is used for filtering above.
    Args:
        place_id: the USAF-WBAN string to get temps for
        month: the month number
        day: the day number
        current_year: the current year
    Returns: a dataframe with temp and current_date columns
    """
    url = "{data_url}/csv/{id}/{month}{day}.csv".format(
            data_url=DATA_URL,
            id=place_id,
            month='{:02}'.format(month),
            day='{:02}'.format(day)
        )
    df = read_csv(url)
    df['current_date'] = df.apply(lambda x: Timestamp(
        year=current_year, month=month, day=day, hour=x.hour, tz='UTC'), axis=1)
    df['temp'] = df.temp * 1.8 + 32
    return df

# for testing in local development
print(get_tweets('Atlanta'))
