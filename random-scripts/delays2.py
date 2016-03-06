from datetime import datetime
# from pprint import pprint
from collections import Counter

from sdk import Location, Service


# https://api.rtt.io/api/v1/json/search/HIB/to/CHX/2015/10/14/0800

# jq '.services | .[] | .locationDetail | "\(.gbttBookedDeparture),\(
# .destination[0].publicTime),\(.realtimeDeparture),\(.realtimeArrival),\(
# .destination[0].tiploc)"' | sed s/'"'//g | sed s/^/"'"/ | grep CH
START = 'LBG'
DEST = 'HIB'

chx_services = []

for hour in range(16, 22):
    date = datetime(2016, 3, 3, hour, 0)
    data = Location(START, DEST, date).get()

    for s in data['services']:
        chx_services.append(s['serviceUid'])

def get_parts(loc):
    book = loc.get('gbttBookedDeparture', '?')
    real = loc.get('realtimeDeparture', '?')
    if '?' in (book, real):
        return '{} {}'.format(book, real)
    delta = datetime.strptime(real, '%H%M') - datetime.strptime(book, '%H%M')
    diff_mins = delta.seconds / 60.
    return '{} {:+3.0f}'.format(
        book, diff_mins)

displays = []
for service_uid in chx_services:
    data = Service(service_uid, date).get()

    locations = data['locations']
    match = False
    parts = []
    for loc in locations:
        displays.append(loc['displayAs'])
        if loc['crs'] == START:
            parts.append(get_parts(loc))
        if loc['crs'] == DEST:
            match = True
            parts.append(get_parts(loc))
    if not match:
        continue
    if len(parts) == 2:
        print "'" + ' - '.join(parts)
    # print
    # for loc in locations[:-1]:
    #     if loc['crs'] == DEST:
    #         if loc['displayAs'] in ('CALL', 'ORIGIN', 'STARTS'):
    #             parts.extend([
    #                 loc.get('gbttBookedDeparture', '?'),
    #                 loc.get('realtimeDeparture', '?')])
    #         else:
    #             parts.extend([loc.get('gbttBookedDeparture', '?'), '-'])
    # loc = locations[-1]
    # if loc['displayAs'] == 'DESTINATION':
    #     parts.extend([
    #         loc.get('realtimeArrival', '?'),
    #         loc.get('gbttBookedArrival', '?')])
    # if len(parts) == 4:
    #     print "'" + ','.join(parts)

print Counter(displays)
