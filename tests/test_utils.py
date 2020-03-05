from utils import average_interp, average_interp_timestamp
import pandas as pd 

def test_average_interp():
    x = [0,2,4]
    y = [0,4,2]

    # averaging over the observed interval
    assert average_interp(y,x,0,4) == 10.0/4

    # averaging over a narrower interval than observed
    assert average_interp(y, x, 1, 3) == 6.5/2

    # averaging over a wider interval than observed
    assert average_interp(y, x, -1, 5) == 12/6

def test_average_interp_timestamp():
    now = pd.Timestamp.now()
    t = [now, 
         now + pd.Timedelta(2, 'h'), 
         now + pd.Timedelta(4, 'h')]
    t0 = now - pd.Timedelta(1, 'h')
    t1 = now + pd.Timedelta(5, 'h')
    y = [0, 4, 2]
    assert average_interp_timestamp(y, t, t0, t1) == 12/6
