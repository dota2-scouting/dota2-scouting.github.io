# src/tools.py

import json
from js import XMLHttpRequest

def xrequest(url):
    req = XMLHttpRequest.new()
    req.open("GET", url, False)
    req.send(None)
    #output = str(req.response)
    #output = json.loads(output)
    #return output
    return json.loads(req.response)

class cache(dict):
    def request(self, url):
        if url not in self:
            self[url] = xrequest(url)
        return self[url]
    def 

"""
class cache(dict):
    def request(self, url):
        if url not in self:
            print('GET', url)
            self[url] = requests.get(url).json()
        return self[url]
"""

## opendota API calls
c = cache()

def get_player_data(account_id):
    # fill the following
    profile = {'name': '',
               'avatar': '',
               'country': '',
               'medal': ''}
    url = 'https://api.opendota.com/api/players/{}'
    data = c.request(url.format(account_id))
    profile['name'] = data['personaname']
    profile['avatar'] = data['avatarmedium']
    profile['country'] = data['loccountrycode']
    profile['medal'] = data['rank_tier'] // 10
    return profile

def get_player_heroes(account_id, **parameters):
    params = ''
    if parameters:
        params = '?' + '&'.join('{}={}'.format(k, v) for k, v in parameters.items())
    url = 'https://api.opendota.com/api/players/{}/heroes{}'
    data = c.request(url.format(account_id, params))
    return data
