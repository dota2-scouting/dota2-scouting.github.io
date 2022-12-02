# src/network.py

import json

"""
import requests
import time

class cached_requests(dict):
    def request(self, url):
        if url not in self:
            print('GET', url)
            self[url] = requests.get(url).json()
            time.sleep(2)
        print('CACHE', url)
        return self[url]

def file_io(path):
    return path
"""

from js import XMLHttpRequest
from pyodide.http import open_url
from io import StringIO
#import asyncio
# TODO add WAIT FOR OPENDOTA


#async
def xrequest(url):
    req = XMLHttpRequest.new()
    req.open("GET", url, False)
    req.send(None)
    #output = str(req.response)
    #output = json.loads(output)
    output = json.loads(req.response)
    #await asyncio.sleep(2)
    return output

class cached_requests(dict):
    def request(self, url):
        if url not in self:
            self[url] = xrequest(url)
        return self[url]

def file_io(url):
    return StringIO(open_url(url).getvalue())
