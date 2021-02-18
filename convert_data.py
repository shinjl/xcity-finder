# Data preparation utility for runtime
# Split large world city file into small chunks to save runtime memory
# ==============================================================================

import time
import os
import csv

countries = {}
cities = {}


def read_country_code():
    print('loading country code')
    with open('countries/country_code.csv', newline='') as csvfile:
        datareader = csv.reader(csvfile, delimiter=',')
        for one in datareader:
            countries[one[0]] = one[1]


def read_city_list():
    start = time.time()
    print('loading city list')
    errors = set()
    for i in ['1', '2']:
        with open('cities/worldcitiespop' + i + '.csv', newline='') as csvfile:
            datareader = csv.reader(csvfile, delimiter=',')
            next(datareader)  # skip the header row
            for one in datareader:
                city_name_key = one[1].strip()[0:2]
                prev = cities.get(city_name_key)
                if (prev is None):
                    prev = []
                country_name = countries.get(one[0].upper())
                if (country_name is None):
                    errors.add(one[0].upper())
                else:
                    prev.append([one[1].lower(), one[2] + '(' + country_name + ')',
                                 float(one[5]), float(one[6])])
                    cities[city_name_key] = prev

    end = time.time()
    print("loaded city list with: ", (end - start), "sec")
    if (len(errors) > 0):
        print("the following country code was not found:")
        print(errors)


def convert_city_data():
    read_country_code()
    read_city_list()

    start = time.time()
    print('converting city list')
    output_dir = 'data/'
    os.makedirs(output_dir, exist_ok=True)
    for city_name_key in cities:
        with open(output_dir + city_name_key + '.csv', 'w', newline='') as csvfile:
            datawriter = csv.writer(csvfile, delimiter=',')
            values = cities.get(city_name_key)
            sorted_values = sorted(values, key=lambda item: item[0])
            for one in sorted_values:
                datawriter.writerow(one)

    end = time.time()
    print("converted city list with: ", (end - start), "sec")


convert_city_data()
