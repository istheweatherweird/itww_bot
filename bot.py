import tweepy
from pandas import Timestamp
from sentry_sdk import init as sentry_init

from tweets import get_tweets, get_place

sentry_init("https://0e01f195b76649daa6ee7286f7307d2d@sentry.io/4081958")

cities = [
    'Chicago',
    'New York City',
    'Los Angeles',
    'Houston'
]

LOCAL_DEVELOPMENT = False

for city in cities:
    place = get_place(city)
    icao = place['ICAO']
    current_time = Timestamp.now(tz=place['TZ'])

    if LOCAL_DEVELOPMENT:
        # uncomment the following if you'd like to tweet from local dev
        # from secrets import *
        #
        # CONSUMER_KEY = globals()['{}_CONSUMER_KEY'.format(icao)]
        # CONSUMER_SECRET = globals()['{}_CONSUMER_SECRET'.format(icao)]
        # ACCESS_KEY = globals()['{}_ACCESS_KEY'.format(icao)]
        # ACCESS_SECRET = globals()['{}_ACCESS_SECRET'.format(icao)]

        # UTC value for the current hour
        end_time = Timestamp.now(tz='UTC').floor(freq='h')

        print(get_tweets(place, end_time))

    else:
        from os import environ

        try:
            CONSUMER_KEY = environ['{}_CONSUMER_KEY'.format(icao)]
            CONSUMER_SECRET = environ['{}_CONSUMER_SECRET'.format(icao)]
            ACCESS_KEY = environ['{}_ACCESS_KEY'.format(icao)]
            ACCESS_SECRET = environ['{}_ACCESS_SECRET'.format(icao)]
        except KeyError:
            print(
                "Key assignment error for {}! One of your keys is "
                "not defined properly. If you're trying to run this locally, "
                "make sure LOCAL_DEVELOPMENT=True.".format(icao)
            )

        # UTC value for 6pm today
        end_time = Timestamp.today(
            tz=place['TZ']
        ).replace(
            hour=18
        ).floor(
            freq='h'
        ).tz_convert(
            tz='UTC'
        )

    if current_time.hour == 18:
        # check if 6pm <= current local time < 7pm
        # this is intended to run every hour
        try:
            auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
            api = tweepy.API(auth)

            tweets = get_tweets(place, end_time)
            for tweet in tweets:
                if tweet:
                    api.update_status(tweet)
        except (tweepy.error.TweepError, NameError) as e:
            print('\nNot posted to Twitter!\n\nError: {}\n'.format(e))
