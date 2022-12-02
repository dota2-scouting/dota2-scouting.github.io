# src/network.py

import json
#import time
# TODO WAIT FOR OPENDOTA


"""
import requests

class cached_requests(dict):
    def request(self, url):
        if url not in self:
            print('GET', url)
            self[url] = requests.get(url).json()
        print('CACHE', url)
        return self[url]

def file_io(path):
    return path
"""

from js import XMLHttpRequest
from pyodide.http import open_url
from io import StringIO
import asyncio

#async
async def xrequest(url):
    req = XMLHttpRequest.new()
    req.open("GET", url, False)
    req.send(None)
    #output = str(req.response)
    #output = json.loads(output)
    output = json.loads(req.response)
    #time.sleep(2)
    await asyncio.sleep(2)
    return output

async class cached_requests(dict):
    async def request(self, url):
        if url not in self:
            self[url] = xrequest(url)
        return self[url]

def file_io(url):
    return StringIO(open_url(url).getvalue())
