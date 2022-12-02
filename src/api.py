# src/api.py

from network import cached_requests
cache = cached_requests()

import asyncio

## opendota API calls

async def get_player_data(account_id):
    # fill the following
    profile = {'name': '',
               'avatar': '',
               'country': '',
               'medal': ''}
    url = 'https://api.opendota.com/api/players/{}'
    data = cache.request(url.format(account_id))
    profile['name'] = data['profile']['personaname']
    profile['avatar'] = data['profile']['avatarmedium']
    profile['country'] = data['profile']['loccountrycode']
    profile['medal'] = data['rank_tier'] // 10
    return profile

async def get_player_heroes(account_id, **parameters):
    params = ''
    if parameters:
        params = '?' + '&'.join('{}={}'.format(k, v) for k, v in parameters.items())
    url = 'https://api.opendota.com/api/players/{}/heroes{}'
    data = cache.request(url.format(account_id, params))
    return data
