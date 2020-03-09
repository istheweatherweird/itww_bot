from bot import LOCAL_DEVELOPMENT
from tweets import get_place, get_tweets


def test_get_tweets():
    place = get_place('Chicago')
    end_time = Timestamp.now(tz='UTC').floor(freq='h')
    tweets = get_tweets(place, end_time)
    assert len(tweets) > 0
