import requests
import csv
import numpy as np
import pandas as pd

UNIX_TIME_START = pd.Timestamp(0, tz='UTC')

def list_average(list):
    return sum(list) / len(list)

def average_interp(y, x, x0, x1):
    """
    Linearly interpolated average
    Args:
        y: y values of the function
        x: x values of the function
        x0: left end of interval to take average over
        x1: right end of interval to take average over

    This works in three steps:
        1. Interpolate the observations (x,y) to the end points x0, x1 using 
           np.interp(). This gives a linear interpolation inside the range of
           x and a flat interpolation outside
        2. Use np.trapz() to calculate the area under the curve between x0 and x1
        3. Divide by (x1 - x0) to get an interpolated average
    """
    if len(y) != len(x):
        raise ValueErrror("y and x should have same length")
    if x1 <= x0:
        raise ValueError("x1 should be greater than x0")
    if len(x) != len(np.unique(x)):
        raise ValueError("x should not contain duplicates")

    y0, y1 = np.interp([x0, x1], x, y)

    df = pd.DataFrame(dict(y=y + [y0, y1], 
                           x=x + [x0, x1]))
    df = df[df.x.between(x0, x1)].sort_values('x')
   
    return np.trapz(df.y, df.x) / (x1 - x0)

def average_interp_timeseries(temps, t0, t1):
    """
    Linearly interpolated average in time
    Converts x values to UNIX timestamps and calls average_interp()
    We use UNIX timestamps because they are standard 
        but the result is independent of this choice

    Args:
        temps: pandas Series of temperatures with DatetimeIndex
        t0: Timestamp, left end of interval to average over
        t1: Timestamp, right end of interval to average over
    Returns:
        average (float)
    """
    x = temps.index.map(to_unix_timestamp).tolist()
    x0 = to_unix_timestamp(t0)
    x1 = to_unix_timestamp(t1)
    return average_interp(temps.tolist(), x, x0, x1)

def to_unix_timestamp(t):
    return (t - UNIX_TIME_START) / pd.Timedelta(1, 's')
    
def get_reader(url):
    response = requests.get(url)
    lines = (line.decode('utf-8') for line in response.iter_lines())
    reader = csv.reader(lines)
    next(reader, None)  # skip the headers

    return reader
