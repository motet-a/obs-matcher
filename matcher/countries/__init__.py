import json
import os
from pathlib import Path

import requests


data = []


def load_data(app):
    global data
    if data:
        return data
    DATA_FILE = Path(app.instance_path).joinpath('countries.json')
    UPDATE_URL = 'https://raw.githubusercontent.com/mledoze/countries/' \
                 'master/dist/countries.json'
    try:
        data += json.load(open(str(DATA_FILE), 'r'))
    except OSError:
        r = requests.get(UPDATE_URL)
        assert r.status_code == 200
        data += r.json()
        os.makedirs(str(DATA_FILE.parent), exist_ok=True)
        with open(str(DATA_FILE), 'w') as handle:
            json.dump(data, handle)
    return data


def lookup(name):
    for country in data:
        if name.lower() in [s.lower() for s in country['altSpellings']]:
            return country['cca2']

        for translation in list(country['translations'].values()) \
                + [country['name']]:
            for attr in ['official', 'common']:
                if translation.get(attr, '').lower() == name.lower():
                    return country['cca2']
    return None
