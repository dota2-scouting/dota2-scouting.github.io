# src/scouting.py

import pandas as pd
import json
from io import StringIO

import asyncio

from js import document, XMLHttpRequest
from pyodide import create_proxy
from pyodide.http import open_url

from tools import * # get_player_data, get_player_heroes

scouting_csv_url = "https://raw.githubusercontent.com/jeromehage/dota2-scouting/master/hero_stats2.csv"
stats = pd.read_csv(StringIO(open_url(scouting_csv_url).getvalue()), sep = ';', index_col = 0)




flex = 0.25
meta = True
params = {'lobby_type': 7, 'date': 365}

def weights_flex(flex = 0.25):
    # team flexibility [0, 1]
    # 0.0 will only play their roles + heroes for the role
    # 1.0 will swap roles + use heroes off-role
    # try negative values (refuse to play flexible heroes :p)

    # weights are columns
    # rows are roles
    # ex: pos 1 hero score (first row) will use:
    #  85% of pos 1 heroes, 10% of pos 2 heroes, 5% of pos 3 heroes
    wf000 = np.identity(5)
    wf025 = np.array([[0.85, 0.10, 0.05, 0.00, 0.00],
                      [0.20, 0.60, 0.20, 0.00, 0.00],
                      [0.10, 0.10, 0.70, 0.10, 0.00],
                      [0.00, 0.10, 0.00, 0.50, 0.40],
                      [0.00, 0.00, 0.00, 0.40, 0.60]])
    wf100 = np.ones((5,5)) * 0.20

    x = [0, 0.25, 1]
    y = [wf000, wf025, wf100]
    # interp
    i = max(np.searchsorted(x, f), 1)
    xi = (f - x[i - 1]) / (x[i] - x[i - 1])
    return y[i] * xi + y[i - 1] * (1 - xi)

# idk why I chose this format
weightsf = {k + 1: {x + 1: y for x, y in enumerate(v)}
            for k, v in enumerate(weights_flex(flex))}

outputs = []
team = {k: [v] for k, v in zip(range(1, 6), player_ids.value.split(','))}

def get_player_medal(account_id):
    return get_player_data(account_id)['medal']

def get_player_heroes(account_id, **parameters):
    params = ''
    if parameters:
        params = '?' + '&'.join('{}={}'.format(k, v) for k, v in parameters.items())
    url = 'https://api.opendota.com/api/players/{}/heroes{}'
    data = reqwest(url.format(account_id, params))
    return data



medal = {}
for k, accs in team.items():
    m = []
    for a in accs:
        m += [get_player_medal(a)]
        # delay for opendota APIs
        await asyncio.sleep(2)
    medal[k] = max(m)

for role, account_ids in team.items():
    if account_ids:
        d = []
        for a in account_ids:
            d += [get_player_heroes(a, **params)]
            # delay for opendota APIs
            await asyncio.sleep(2)

        # combine accounts
        d = [pd.DataFrame(a) for a in d]
        g1 = pd.concat(d).groupby('hero_id')['last_played'].apply(max)
        g2 = pd.concat(d).groupby('hero_id')[d[0].columns[2:]].apply(sum)
        df = pd.merge(g1, g2, on = 'hero_id').sort_values('games', ascending = False).reset_index()

        # add stats columns
        df['hero_id'] = df['hero_id'].astype('int64')
        m = pd.merge(df, stats, how = 'left', left_on = ['hero_id'], right_on = ['id'])

        # value: give points for heroes played on this role (considering flexibility)
        for k in range(1, 6):
            m['pts_{}'.format(k)] = weightsf[role][k] * m['pos{}_pick'.format(k)] * m['pos{}_win'.format(k)]
        m['value'] = m[['pts_{}'.format(k) for k in range(1, 6)]].sum(axis = 1)

        # adjust value for winrate on the player's medal and meta
        m['value'] = 2 * m['value'] * m['{}_win'.format(medal[role])] / m['{}_pick'.format(medal[role])]
        if meta:
            m['value'] = m['value'] * (m['pro_pick'] + m['pro_ban'])
        else:
            m['value'] = m['value'] * 1000

        # points: player games and winrate
        m['pts'] = m['value'] * m['win'] * m['win'] / m['games']
        m.sort_values('pts', ascending = False, inplace = True)

        # drop less important heroes
        m = m.reset_index().fillna(0)
        top = m['pts'].cumsum() < m['pts'].sum() * 0.95 # keep top 95%
        m = m[top | (m.index < 20)] # keep at least 20 heroes
        m['points'] = (1000 * m['pts'] / sum(m['pts']))

        # formating
        #m['last_played_days'] = ((time.time() - m['last_played']) / (24 * 3600)).astype(int)
        m['value'] = m['value'].astype(int)
        m['points'] = m['points'].fillna(0).astype(int)

        # player scout sheets
        #output = m[['localized_name', 'games', 'win', 'last_played_days', 'value', 'points']].copy()
        output = m[['localized_name', 'games', 'win', 'value', 'points']].copy()
        output.rename(columns = {'localized_name': 'hero'}, inplace = True)
        #output.to_csv('pos{}.csv'.format(role), sep = ';')
        outputs += [output]

report = pd.DataFrame()
for i, o in enumerate(outputs):
    report['{}_heroes'.format(i + 1)] = o['hero']
    report['{}_points'.format(i + 1)] = o['points']

#listbox.innerHTML = report.to_html(classes="table")
add_item(report.columns.values.tolist())
for k, row in report.iterrows():
    add_item(row.values.tolist())


scout = create_proxy(_scout)
document.getElementById("scout").addEventListener("click", scout)
