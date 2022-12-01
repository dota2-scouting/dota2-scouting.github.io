# src/ui.py

import asyncio
from js import document, XMLHttpRequest
from pyodide import create_proxy
#from pyodide.ffi import create_proxy

from scouting import scout

html = dict()
# input
html['role'] = document.getElementById("role-select")
html['account-ids'] = document.getElementById("account-ids-input")
html['flex'] = document.getElementById("flex-input")
html['date'] = document.getElementById("date-input")
html['ranked-only'] = document.getElementById("ranked-only-select")
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
        html['scouting'].appendChild(option)

    html['scouting'].innerHTML = ''
    add_item('scouting...')

    account_ids = [int(a) for a in html['account-ids'].value.split(',')]
    role = int(html['role'].value)
    flex = float(html['flex'].value)
    date = int(html['date'].value)
    ranked = bool(int(html['ranked-only'].value))

    params = {'date': date}
    if ranked:
        params['lobby_type'] = 7

    add_item(str([account_ids, role, flex, **params]))
    profile, report = scout(account_ids, role, flex, **params)
    add_item(str([account_ids, role, flex, **params]))
    html['avatar'].src = profile['avatar']
    html['account-id'].innerText = profile['name']
    html['country'].innerText = str(profile['country'])
    html['medal'].innerText = str(profile['medal'])
    
    #listbox.innerHTML = report.to_html(classes="table")
    add_item(report.columns.values.tolist())
    for k, row in report.iterrows():
        add_item(row.values.tolist())

async def _export(*args, **kwargs):
    # https://www.jhanley.com/blog/pyscript-files-and-file-systems-part-2/
    # https://stackoverflow.com/questions/72463208/how-to-save-figure-using-pyscript
    pass

scout_proxy = create_proxy(_scout)
document.getElementById("scout").addEventListener("click", scout_proxy)

export_proxy = create_proxy(_export)
document.getElementById("export").addEventListener("click", export_proxy)
