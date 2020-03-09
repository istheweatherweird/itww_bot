from bot import LOCAL_DEVELOPMENT
from tweets import get_place, get_tweets


def test_get_tweets():
    place = get_place('Chicago')
    tweets = get_tweets(place)
    assert len(tweets) > 0
