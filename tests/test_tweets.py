from pandas import Timestamp
from tweets import get_place, get_tweets
from bot import cities


def test_get_tweets():
    for city in cities:
        place = get_place(city)
        end_time = Timestamp.now(tz='UTC').floor(freq='h')
        tweets = get_tweets(place, end_time)
        assert len(tweets) > 0
