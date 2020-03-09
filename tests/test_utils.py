from utils import average_interp, average_interp_timeseries, get_timeseries_coverage
import pandas as pd


def test_average_interp():
    x = [0, 2, 4]
    y = [0, 4, 2]

    # averaging over the observed interval
    assert average_interp(y, x, 0, 4) == 10.0/4

    # averaging over a narrower interval than observed
    assert average_interp(y, x, 1, 3) == 6.5/2

    # averaging over a wider interval than observed
    assert average_interp(y, x, -1, 5) == 12/6


def test_average_interp_timeseries():
    now = pd.Timestamp.utcnow()
    temps = pd.Series({
        now: 0,
        now + pd.Timedelta(2, 'h'): 4,
        now + pd.Timedelta(4, 'h'): 2})
    t0 = now - pd.Timedelta(1, 'h')
    t1 = now + pd.Timedelta(5, 'h')
    assert average_interp_timeseries(temps, t0, t1) == 12/6


def test_get_timeseries_coverage():
    now = pd.Timestamp.utcnow()
    temps = pd.Series({
        now: 0,
        now + pd.Timedelta(2, 'h'): 4,
        now + pd.Timedelta(4, 'h'): 2})
    t0 = now - pd.Timedelta(1, 'h')
    t1 = now + pd.Timedelta(5, 'h')
    assert get_timeseries_coverage(temps, t0, t1) == pd.Timedelta(2, 'h')
