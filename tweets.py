import requests
import csv
import pandas as pd
import logging
from sentry_sdk import capture_exception
import utils


logging.getLogger().setLevel(logging.INFO)

DATA_URL = 'https://www.istheweatherweird.com/istheweatherweird-data-hourly'
STATIONS_URL = '{}/csv/stations.csv'.format(DATA_URL)
MIN_COVERAGE= pd.Timedelta(4, 'h')
DAY = pd.Timedelta(1, 'D')
WEEK = pd.Timedelta(7, 'D')


def get_tweets(place):
    # UTC values for 6pm local time yesterday - 6pm local time today
    end_time = pd.Timestamp.today(
        tz=place['TZ']
    ).replace(
        hour=18
    ).floor(
        freq='h'
    ).tz_convert(
        tz='UTC'
    )

    tweets = []
    tweet = write_tweet(place, end_time, DAY)

    if tweet:
        tweets += [tweet]

    # If it's Sunday, tweet a weekly recap
    if end_time.tz_convert(tz=place['TZ']).day_name() == 'Sunday':
        tweet = write_tweet(place, end_time, WEEK)
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
    nws_request_url = 'https://api.weather.gov/stations/{}/observations'.format(
        place['ICAO']
    )
    params = {
        'start': start_time.isoformat(),
        'end': end_time.isoformat(),
    }
    response_json = requests.get(nws_request_url, params=params).json()

    try:
        timestamps = [obs['properties']['timestamp']
                      for obs in response_json['features']]
        temps = [obs['properties']['temperature']['value']
                 for obs in response_json['features']]
        observations = pd.Series(temps, index=pd.DatetimeIndex(timestamps))
    except KeyError:
        observations = pd.Series()
    
    return observations


def get_observed_temp(place, start_time, end_time):
    observations = get_observations(place, start_time, end_time)

    coverage = utils.get_timeseries_coverage(observations, start_time, end_time)
    if coverage > MIN_COVERAGE:
        raise ValueError("Insufficient observational coverage: %s" % coverage)

    average = utils.average_interp_timeseries(observations, start_time, end_time)
    average_fahrenheit = average * 1.8 + 32

    return average_fahrenheit


def get_historical_temps(place, start_time, end_time):
    place_id = place['USAF'] + '-' + place['WBAN']

    start_year = int(place['BEGIN'][:4])
    intervals = get_intervals(end_time, pd.Timedelta(1, 'D'), start_year)
    interval_index = pd.IntervalIndex(list(intervals))

    # first get full days of temps
    month_days = get_unique_month_days(interval_index)
    df = get_month_days_temps(place_id, month_days)
    df['interval'] = pd.cut(df.timestamp, interval_index)

    # if a timestamp didn't lie in an interval then 'interval' is now null
    # so dropna() filters as desired
    df.dropna(inplace=True)
    return df


def write_tweet(place, end_time, timespan):
    start_time = end_time - timespan

    try:
        observed_temp = get_observed_temp(place, start_time, end_time)
    except ValueError as e:
        capture_exception(e)
        return

    historical_temps = get_historical_temps(place, start_time, end_time).set_index('timestamp')

    def average_interp_named_timeseries(timeseries):
        t0 = timeseries.name.left
        t1 = timeseries.name.right
        return utils.average_interp_timeseries(timeseries, t0, t1)

    averages = historical_temps.groupby('interval', observed=True).temp.agg(average_interp_named_timeseries)
    logging.info('Average temperatures: %s' % averages)
    year_warmer = observed_temp > averages
    percent_warmer = year_warmer.mean() * 100

    warm_bool = percent_warmer >= 50

    if warm_bool:
        percent_relative = int(round(percent_warmer))
    else:
        percent_relative = int(round(100 - percent_warmer))

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

    emoji_list = ['❄️', '🔥']

    weirdness = weirdness_levels[weirdness_level]
    comparison = comparisons[warm_bool][(weirdness_level == 3)]

    if weirdness_level:
        emoji = emoji_list[warm_bool] * weirdness_level + ' '
        if record:
            emoji = '🚨' + emoji
    else:
        emoji = ''

    sentence_dict = {
        'emoji': emoji,
        'record': record,
        'city': place['place'],
        'weirdness': weirdness,
        'observed_temp': int(round(observed_temp)),
        'comparison': comparison,
        'percent_relative': percent_relative,
        'month': end_time.tz_convert(tz=place['TZ']).month_name(),
        'day': end_time.tz_convert(tz=place['TZ']).day,
    }

    return write_sentences(sentence_dict, timespan)


def write_sentences(sentence_dict, timespan):
    if timespan == DAY:
        sentence1 = '{emoji}The weather in {city} was {weirdness} today. '.format(
            **sentence_dict
        )

        if not sentence_dict['record']:
            sentence2 = 'It was {observed_temp}ºF on average, {comparison} than {percent_relative}% of {month} {day} temperatures on record.'.format( # noqa
                **sentence_dict
            )
        else:
            sentence2 = 'It was {observed_temp}ºF on average, the {comparison} {month} {day} temperature on record.'.format( # noqa
                **sentence_dict
            )

    if timespan == WEEK:
        sentence1 = ' 🗓 The weather in {city} was {weirdness} this week. \n\n'.format(
            **sentence_dict
        )

        if not sentence_dict['record']:
            sentence2 = '{emoji}It was {observed_temp}ºF on average, {comparison} than {percent_relative}% of weeks ending {month} {day} on record.'.format( # noqa
                **sentence_dict
            )
        else:
            sentence2 = '{emoji}It was {observed_temp}ºF on average, the {comparison} week ending {month} {day} on record.'.format( # noqa
                **sentence_dict
            )

    return '{sentence1}{sentence2}'.format(
        sentence1=sentence1,
        sentence2=sentence2,
    )


def get_month_days_temps(place_id, month_days):
    """
    Concatenate observations for a range of month-days
    Args:
        place_id: USAF-WBAN string
        start: a dataframe with columns month and day as returned by get_month_days
    Returns: a dataframe with temp and current_date columns
    """
    return pd.concat((
        get_month_day_temps(place_id, row.month, row.day)
        for i, row in month_days.iterrows()))


def get_month_day_temps(place_id, month, day):
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
    df = pd.read_csv(url)
    df['timestamp'] = df.apply(lambda x: pd.Timestamp(
        year=x.year, month=month, day=day, hour=x.hour, tz='UTC'), axis=1)

    # istheweatherweird-data-hourly stores temps in celsius without a decimal
    df['temp'] = df.temp * .18 + 32
    return df


def get_intervals(end_time, timedelta, start_year):
    """
    Generator for comparison time intervals
    Args:
        end_time: the time at which the current interval ends
        timedelta: the length of the interval
        start_year: the first year to make the interval
    Returns:
        a sequence of pandas Intervals that we will compare the current interval with

    e.g. get_intervals(pd.Timestamp('2020-02-28 18:00Z'), pd.Timedelta(1, 'D'), 2017))
    generates
       Interval('2017-02-27 18:00:00', '2010-02-28 18:00:00', closed='left'),
       Interval('2018-02-27 18:00:00', '2011-02-28 18:00:00', closed='left'),
       Interval('2019-02-27 18:00:00', '2012-02-28 18:00:00', closed='left')
    """
    for year in range(start_year, end_time.year):
        # For Feb 29, replacing with a non-leap year will raise an error, just ignore those years
        try:
            end = end_time.replace(year=year)
        except ValueError:
            continue
        start = end - timedelta
        yield pd.Interval(start, end, closed='left')


def get_unique_month_days(interval_index):
    """
    For an interval index get a list of unique month-days
    Returns: a DataFrame with columns month and day
    """
    dates = pd.concat(
        [pd.Series(pd.date_range(i.left, i.right)) for i in interval_index]
    )
    month_days = pd.DataFrame(
        {
            'month': dates.dt.month,
            'day': dates.dt.day
        }
    ).drop_duplicates()
    return month_days
