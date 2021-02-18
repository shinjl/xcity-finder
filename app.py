# World city finder service
# ==============================================================================

from flask import Flask, request, abort
from markupsafe import escape
import urllib.request
import urllib.parse
from os import path
import csv
from flask_cors import CORS
import psutil

MEMORY_THRESHOLD = 60  # release memory when memory usage reaches this point
MAX_RECORDS = 1000  # limit the maximum number of matching records


cities = dict()
hits = dict()
app = Flask(__name__)
CORS(app)


def refresh_hits(city_name_key):
    hit_counter = hits.get(city_name_key)
    if (hit_counter is None):
        hit_counter = 0
    hit_counter += 1
    hits[city_name_key] = hit_counter


def release_memory():
    # remove least frequently used item from cache
    # when the memory usage reaches the threshold value
    if (len(hits) < 1):
        return

    virtual_memory = psutil.virtual_memory()
    print('current memory usage', virtual_memory.percent)
    if (virtual_memory.percent > MEMORY_THRESHOLD):
        hits_sorted = sorted(hits.items(), key=lambda item: item[1])
        print('hits', hits_sorted)
        one = hits_sorted[0][0]
        print('remove', one, 'from cache')
        cities.pop(one)
        hits.pop(one)


def get_city_data(city_name):
    city_name_key = city_name[0:2]
    file_name = 'data/' + city_name_key + '.csv'
    if (not path.exists(file_name)):
        return []

    city_list = cities.get(city_name_key)
    if (city_list is not None):
        refresh_hits(city_name_key)
        return city_list

    release_memory()

    city_list = []

    with open(file_name, newline='') as csvfile:
        print('reading from: ', file_name)
        datareader = csv.reader(csvfile, delimiter=',')
        for one in datareader:
            city_list.append(
                {
                    'key': one[0],
                    'name': one[1],
                    'label': one[1],
                    'lat': float(one[2]),
                    'lon': float(one[3])
                }
            )
        cities[city_name_key] = city_list
    refresh_hits(city_name_key)
    return city_list


@app.route('/cities/<name>', methods=['GET'])
def get_cities(name):
    print('query:', name)
    city_name = urllib.parse.unquote(name)
    city_name = city_name.lower().strip()
    if (len(city_name) < 2):
        return {'cities': []}

    city_list = get_city_data(city_name)
    matching_cities = [x for x in city_list if x['key'].startswith(city_name)]
    print('total', len(city_list), 'records')
    print('matching', len(matching_cities), 'records')
    if (len(matching_cities) > MAX_RECORDS):
        matching_cities = matching_cities[:MAX_RECORDS]
    return {
        'cities': list(matching_cities)
    }


print('xcity-finder service started')
