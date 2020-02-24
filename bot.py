import time
import sys
import tweepy
from pprint import pprint
from pandas import Timestamp

from tweets import get_tweets, get_place

LOCAL_DEVELOPMENT = False

if LOCAL_DEVELOPMENT:
    from secrets import *

else:
    from os import environ

    CONSUMER_KEY = environ['CONSUMER_KEY']
    CONSUMER_SECRET = environ['CONSUMER_SECRET']
    ACCESS_KEY = environ['ACCESS_KEY']
    ACCESS_SECRET = environ['ACCESS_SECRET']
    CITY = environ['CITY']

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

place = get_place(CITY)
current_time = Timestamp.now(tz=place['TZ'])

# check if 6pm <= current local time < 7pm
# this is intended to run every hour through the Heroku scheduler
if current_time.hour == 18:
    tweets = get_tweets(CITY)
    for tweet in tweets:
        api.update_status(tweet)
