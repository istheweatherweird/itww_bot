import time
import sys
import tweepy
from pprint import pprint
from pandas import Timestamp

from tweets import get_tweets, get_place

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
        #
        # from secrets import *
        #
        # CONSUMER_KEY = globals()['{}_CONSUMER_KEY'.format(icao)]
        # CONSUMER_SECRET = globals()['{}_CONSUMER_SECRET'.format(icao)]
        # ACCESS_KEY = globals()['{}_ACCESS_KEY'.format(icao)]
        # ACCESS_SECRET = globals()['{}_ACCESS_SECRET'.format(icao)]

        print(get_tweets(place))

    elif not LOCAL_DEVELOPMENT and current_time.hour == 18:
        # check if 6pm <= current local time < 7pm
        # this is intended to run every hour through the Heroku scheduler
        from os import environ

        try:
            CONSUMER_KEY = environ['{}_CONSUMER_KEY'.format(icao)]
            CONSUMER_SECRET = environ['{}_CONSUMER_SECRET'.format(icao)]
            ACCESS_KEY = environ['{}_ACCESS_KEY'.format(icao)]
            ACCESS_SECRET = environ['{}_ACCESS_SECRET'.format(icao)]
        except KeyError:
            print("Key assignment error! One of your keys is not defined properly.")

    try:
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
        api = tweepy.API(auth)

        tweets = get_tweets(place)
        for tweet in tweets:
            api.update_status(tweet)
    except (tweepy.error.TweepError, NameError) as e:
        print('\nNot posted to Twitter!\n\nError: {}\n'.format(e))
