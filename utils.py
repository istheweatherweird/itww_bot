import requests
import csv

def list_average(list):
    return sum(list) / len(list)


def get_reader(url):
    response = requests.get(url)
    lines = (line.decode('utf-8') for line in response.iter_lines())
    reader = csv.reader(lines)
    next(reader, None)  # skip the headers

    return reader
