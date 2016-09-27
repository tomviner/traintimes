from datetime import datetime
# from pprint import pprint
from collections import Counter

from traintimes.sdk import Location, Service, ResponseError


# https://api.rtt.io/api/v1/json/search/HIB/to/CHX/2015/10/14/0800

# jq '.services | .[] | .locationDetail | "\(.gbttBookedDeparture),\(
# .destination[0].publicTime),\(.realtimeDeparture),\(.realtimeArrival),\(
# .destination[0].tiploc)"' | sed s/'"'//g | sed s/^/"'"/ | grep CH
START = 'CHX'
DEST = 'HIB'
# START, DEST = DEST, START


def calc_lateness(book, real):
    delta = datetime.strptime(real, '%H%M') - datetime.strptime(book, '%H%M')
    return int(delta.seconds / 60.0)

def lateness_as_str(loc):
    book = loc.get('gbttBookedDeparture', '?')
    real = loc.get('realtimeDeparture', '?')
    if '?' in (book, real):
        return '{} {}'.format(book, real)
    diff_mins = calc_lateness(book, real)
    return '{} {:+3.0f}'.format(book, diff_mins)

def lateness_as_mins(loc):
    book = loc.get('gbttBookedDeparture', '?')
    real = loc.get('realtimeDeparture', '?')
    if '?' in (book, real):
        return None
    return calc_lateness(book, real)

services = []

for hour in range(12, 21):
    date = datetime(2016, 9, 27, hour, 0)
    print date
    try:
        data = Location(START, DEST, date).get()
    except ResponseError as e:
        print(e)
        continue
    if not data['services']:
        continue
    for s in data['services']:
        # import json
        # print json.dumps(s, indent=4)
        extra = {
            'displayAs': s['locationDetail']['displayAs'],
            'lateness': lateness_as_mins(s['locationDetail']),
        }
        services.append((s['serviceUid'], extra))
        break

displays = []
for service_uid, extra in services:
    data = Service(service_uid, date).get()
    locations = data['locations']

    match = False
    output = []
    for loc in locations:
        displays.append(loc['displayAs'])
        if loc['crs'] == DEST:
            match = True
        output.append(loc['crs'] + ' ' + lateness_as_str(loc))
        output[-1] += '\t' + loc['displayAs']
        if match:
            break
    print service_uid
    if output:
        print '\t' + '\n\t'.join(output)
        print extra
        print

print Counter(displays)
