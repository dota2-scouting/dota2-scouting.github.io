# src/scouting.py

import pandas as pd
import numpy as np
import json
#import time
import asyncio

from api import * # get_player_data, get_player_heroes
from network import file_io

scouting_csv_url = "https://raw.githubusercontent.com/jeromehage/dota2-scouting/master/hero_stats2.csv"
stats = pd.read_csv(file_io(scouting_csv_url), sep = ';', index_col = 0)

## todo: split scout() into 3 functions:
# 1) get player info (first account info, medal = of the highest account)
# 2) feed into gen scout data
# 3) apply scout formula



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
    # matrix interp
    x = [0, 0.25, 1]
    y = [wf000, wf025, wf100]
    i = max(np.searchsorted(x, flex), 1)
    xi = (flex - x[i - 1]) / (x[i] - x[i - 1])
    return y[i] * xi + y[i - 1] * (1 - xi)

async def scout(account_ids, role, flex, **params):
    # hero viability for each role
    # (role, heroes)
    # (5, 123) matrix
    role_viability = np.array([(stats['pos{}_pick'.format(k)] * stats['pos{}_win'.format(k)]).values for k in [1, 2, 3, 4, 5]])
    #role_viability = role_viability / np.linalg.norm(role_viability, 'fro')

    # hero flexiblity for each role = team flexiblity * hero viability for each role
    # (role, weight for each role) * (role, heroes) = (role, heroes)
    # (5, 5) * (5, 123) = (5, 123) matrix
    role_flexibility = np.dot(weights_flex(flex), role_viability)

    ## global statistics
    meta = stats['pro_pick'] + stats['pro_ban']

    ## role related statistics
    viability = role_viability[role - 1]
    flexibility = role_flexibility[role - 1]

    ## skill related statistics
    profiles = [get_player_data(a) for a in account_ids]
    medal = max([p['medal'] for p in profiles]) # account with highest medal
    bracket = stats['{}_win'.format(medal)] / stats['{}_pick'.format(medal)] # hero winrate at bracket

    ## player history related statistics
    d = []
    for a in account_ids:
        d += [get_player_heroes(a, **params)]
        # delay for opendota APIs
        #await asyncio.sleep(2)

    # combine accounts
    d = [pd.DataFrame(a) for a in d]
    g1 = pd.concat(d).groupby('hero_id')['last_played'].apply(max)
    g2 = pd.concat(d).groupby('hero_id')[d[0].columns[2:]].apply(sum)
    df = pd.merge(g1, g2, on = 'hero_id').sort_values('games', ascending = False).reset_index()

    # history
    df['winrate'] = df['win'] / df['games']
    df['wins'] = df['win']
    df['losses'] = df['games'] - df['wins']
    #df['freshness'] = ((time.time() - df['last_played']) / (24 * 3600)).astype(int) # number of days since hero was played

    ## join data
    #df = df[['hero_id', 'games', 'wins', 'losses', 'winrate', 'freshness']].copy()
    df = df[['hero_id', 'games', 'wins', 'losses', 'winrate']].copy()
    df['hero_id'] = df['hero_id'].astype('int64')

    df2 = stats[['id', 'localized_name', 'pro_pick', 'pro_ban']].copy()
    df2.rename(columns = {'localized_name': 'hero'}, inplace = True)
    df2['viability'] = viability
    df2['flexibility'] = flexibility
    df2['meta'] = meta
    df2['bracket'] = bracket

    data = pd.merge(df, df2, how = 'left', left_on = ['hero_id'], right_on = ['id'])

    ## formula
    # 1 - give points for heroes played on this role (considering flexibility)
    # 2 - adjust value for winrate on the player's medal and meta

    # original formula = meta * 2 *bracket * flexibility * winrate * wins * 1000
    data['pts'] = data['meta'] * data['bracket'] * data['flexibility'] * data['winrate'] * data['wins']

    ## results

    # drop less important heroes
    data.sort_values('pts', ascending = False, inplace = True)
    data = data.reset_index().fillna(0)
    top = data['pts'].cumsum() < data['pts'].sum() * 0.95 # keep top 95%
    data = data[top | (data.index < 20)] # keep at least 20 heroes
    data['points'] = (1000 * data['pts'] / sum(data['pts'])) # normalize over 1000 points

    # formating
    data['points'] = data['points'].fillna(0).astype(int)
    output = data[['hero', 'games', 'wins', 'points']].copy()
    profiles[0]['medal'] = medal

    return profiles[0], output

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
