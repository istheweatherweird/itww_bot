import time
import sys
import tweepy
from pprint import pprint

from tweets import get_tweets

LOCAL_DEVELOPMENT = False

if LOCAL_DEVELOPMENT:
    from secrets import *

else:
    from os import environ

    CONSUMER_KEY = environ['CONSUMER_KEY']
    CONSUMER_SECRET = environ['CONSUMER_SECRET']
    ACCESS_KEY = environ['ACCESS_KEY']
    ACCESS_SECRET = environ['ACCESS_SECRET']

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

tweets = get_tweets()

if len(tweets) > 0:
    for tweet in tweets:
        api.update_status(tweet)
