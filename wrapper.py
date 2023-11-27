"""
Game data from ncaa.com using R script from Luke Benz
https://github.com/lbenz730/NCAA_Hoops
"""
import random
import subprocess
from datetime import datetime
from datetime import timezone

import numpy as np
import pandas as pd

today = datetime.now(timezone.utc).strftime('%Y-%m-%d') + 'T00:00:00.000Z'
todayprint = datetime.now()
todayprint = todayprint.strftime('%m/%d/%Y %H:%M:%S')

subprocess.call('Rscript ./ncaa_hoops_scraper.R', shell=True)
sched = pd.read_csv('NCAA_Hoops_Results.csv')
sched = sched[(sched.teamscore.notna()) & (sched.oppscore.notna())]
sched = sched.reset_index(drop=True)
sched['datestring'] = ''
sched['t1'] = ''
sched['t2'] = ''
for i in range(len(sched)):
    m, d, y = sched.loc[i, ['month', 'day', 'year']]
    sched.loc[i, 'datestring'] = '%i-%i-%i' % (m, d, y)
    t1, t2 = sched.loc[i, ['team', 'opponent']]
    t1, t2 = sorted([t1, t2])
    sched.loc[i, 't1'] = t1
    sched.loc[i, 't2'] = t2
sched = sched.drop_duplicates(subset=['t1', 't2', 'datestring'], keep='first')
sched['date'] = pd.to_datetime(sched.datestring)
sched = sched.sort_values('date').reset_index(drop=True)

conf = pd.read_csv('conferences.csv')
p6 = np.array(
    ['SEC', 'Pac 12', 'Big 12', 'ACC', 'Big East', 'Big 10', 'AAC'],
    dtype=object,
)
df = pd.DataFrame()
df['school'] = conf.team.values
df['rating'] = 1000.0
df['id'] = conf.ncaa_id.values
df['conference'] = conf.conference.values
df['level'] = 'mid-major'
df['rd'] = 600.0
df['volatility'] = 0.06
df.loc[df.conference.isin(p6) | (df.school == 'Gonzaga'), 'rating'] = 1500
df.loc[df.conference.isin(p6) | (df.school == 'Gonzaga'), 'level'] = 'power'
df.to_csv('./teams.csv', index=False)

sched1 = sched.copy()
loopnum = 171
for i in range(loopnum - 1):
    sched = pd.concat([sched, sched1]).reset_index(drop=True)
sched.to_csv('./sched.csv', index=False)

subprocess.run('./cbb', shell=True)

df = pd.read_csv('./teams_2023_rankings.csv')
df = df[df.level != 'non-d1'].reset_index(drop=True)
df['wins'] = (df['wins'] / (loopnum)).astype(int)
df['losses'] = (df['losses'] / (loopnum)).astype(int)

ranks = (
    df.sort_values('rating', ascending=False)
    .reset_index(drop=True)[
        ['school', 'conference', 'rating', 'wins', 'losses', 'rd']
    ]
    .values
)

print(
    '| {:<5} | {:<20} | {:<20} | {:<8} | {:<6} | {:<9} |'.format(
        'Rank', 'Team', 'Conference', 'Record', 'Rating', 'Deviation'
    )
)
print(
    '| {:<5} | {:<20} | {:<20} | {:<8} | {:<6} | {:<9} |'.format(
        '---:', '---:', '---:', '---:', '---:', '---:'
    )
)
for i in range(1, 25 + 1):
    t, c, r, w, l, rd = ranks[i - 1]
    rec = str(int(w)) + '-' + str(int(l))
    print(
        '| {:<5} | {:<20} | {:<20} | {:<8} | {:<6} | {:<9} |'.format(
            i, t, c, rec, int(r), int(rd)
        )
    )

with open('./README.md', 'w') as f:
    print(
        '| {:<5} | {:<20} | {:<20} | {:<8} | {:<6} | {:<9} |'.format(
            'Rank', 'Team', 'Conference', 'Record', 'Rating', 'Deviation'
        ),
        file=f,
    )
    print(
        '| {:<5} | {:<20} | {:<20} | {:<8} | {:<6} | {:<9} |'.format(
            '---:', '---:', '---:', '---:', '---:', '---:'
        ),
        file=f,
    )
    for i in range(1, 25 + 1):
        t, c, r, w, l, rd = ranks[i - 1]
        rec = str(int(w)) + '-' + str(int(l))
        print(
            '| {:<5} | {:<20} | {:<20} | {:<8} | {:<6} | {:<9} |'.format(
                i, t, c, rec, int(r), int(rd)
            ),
            file=f,
        )

    print('', file=f)
    print(f'Updated {todayprint}', file=f)


df.to_csv('teams_2023_rankings.csv', index=False)

subprocess.run('rm -f sched.csv', shell=True)
