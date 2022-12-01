# src/ui.py

import asyncio
from js import document, XMLHttpRequest
#from pyodide import create_proxy
from pyodide.ffi import create_proxy

from scouting import scout

html = dict()
# input
html['role'] = document.getElementById("role-select")
html['account-ids'] = document.getElementById("account-ids-input")
html['flex'] = document.getElementById("flex-input")
html['date'] = document.getElementById("date-input")
html['ranked-only'] = document.getElementById("ranked-only-input")
# output
html['avatar'] = document.getElementById("avatar-label")
html['account-id'] = document.getElementById("account-id-label")
html['country'] = document.getElementById("country-label")
html['medal'] = document.getElementById("medal-label")
html['scouting'] = document.getElementById("scouting-listbox")

async def _scout(*args, **kwargs):

    def add_item(text):
        option = document.createElement('option')
        v = text
        option.value = v
        option.text = v
        listbox.appendChild(option)

    listbox.innerHTML = ''
    add_item('scouting...')

    account_ids = [int(a) for a in html['account-ids'].value.split(',')]
    flex = float(html['flex'].value)
    date = int(html['date'].value)
    ranked = html['ranked-only'].value
    add_item(str(type(ranked)) + ' ' + str(ranked)) # temp
    role = html['role'].value
    add_item(str(type(role)) + ' ' + str(role)) # temp

    params = {'date': date}
    if ranked:
        params['lobby_type'] = 7
    
    #listbox.innerHTML = report.to_html(classes="table")
    #add_item(report.columns.values.tolist())
    #for k, row in report.iterrows():
    #    add_item(row.values.tolist())

async def _export(*args, **kwargs):
    pass

scout_proxy = create_proxy(_scout)
document.getElementById("scout").addEventListener("click", scout_proxy)

export_proxy = create_proxy(_export)
document.getElementById("export").addEventListener("click", export_proxy)

"""
# global params
params = {'lobby_type': 7, 'date': 365}
flex = 0.25

# player params
account_ids = [99374795]
role = 1 # drop_down_menus['role'].get()

profile, scouting = scout(account_ids, role, flex, **params)
print(profile)
print(scouting)
"""
