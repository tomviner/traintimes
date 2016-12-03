import datetime
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
    delta = (
        datetime.datetime.strptime(real, '%H%M') -
        datetime.datetime.strptime(book, '%H%M')
    )
    return int(delta.seconds / 60.0)

def lateness_as_str(loc):
    book = loc.get('gbttBookedDeparture', '?')
    real = loc.get('realtimeDeparture', '?')
    if '?' in (book, real):
        return '{} {}'.format(book, real)
    diff_mins = calc_lateness(book, real)
    return '{} {:+3.0f} {}'.format(book, diff_mins, real if diff_mins else '\t')

def lateness_as_mins(loc):
    book = loc.get('gbttBookedDeparture', '?')
    real = loc.get('realtimeDeparture', '?')
    if '?' in (book, real):
        return None
    return calc_lateness(book, real)


services = []
import sys

one_day = datetime.timedelta(days=1)
args = sys.argv[1:]
today = datetime.date.today()

date = today
if args:
    day = args[0]
    day = int(day)
    for i in range(31 * 2):
        date = today - (i * one_day)
        if date.day == day:
            break
    else:
        raise ValueError(day)
    day = today.day
print date
# sys.exit()
good_dest = [
    'HASTING', 'TUNWELL',
]
bad_dest = [
    'HAYS', 'SVNOAKS', 'OREE', 'SLADEGN', 'ORPNGTN', 'FLKSTNC',
    'GRVSEND', 'RAMSGTE-RAMSGTE', 'TONBDG', 'RAMSGTE', 'SIDCUP', 'DARTFD',
    'DOVERP', 'BRNHRST', 'GLNGHMK', 'ASHFKY', 'DOVERP-CNTBW', 'CRFD',
    'RCHT', 'ASHFKY-RAMSGTE', 'NBCKNHM', 'HTHRGRN',
]
ds = []
for hour in range(17, 22):
    dt = datetime.datetime.combine(date, datetime.time(hour))
    print dt
    try:
        data = Location(START, DEST, dt).get()
    except ResponseError as e:
        print(e)
        continue
    if not data['services']:
        continue
    print len(data['services']), 'trains'
    for s in data['services']:

        das = '-'.join(d['tiploc'] for d in s['locationDetail']['destination'])
        if das in bad_dest:
            continue
        ds.append(das)
        import json
        print json.dumps(s, indent=4)
        # if '1722' in str(s):
        #     sys.exit()
        extra = {
            'displayAs': s['locationDetail']['displayAs'],
            'lateness': lateness_as_mins(s['locationDetail']),
        }
        services.append((s['serviceUid'], extra))
print map(str, Counter(ds).keys())
# sys.exit()
displays = []
for service_uid, extra in services:
    data = Service(service_uid, date).get()
    locations = data['locations']

    locs = [loc['crs'] for loc in locations]
    das = [loc['displayAs'] for loc in locations]
    cancelled = 'CANCELLED_CALL' in das or 'TERMINATES' in das
    # if not cancelled:
    #     if DEST not in locs:
    #         continue
    #     if not extra['lateness']:
    #         continue

    started = False
    match = False
    output = []
    for loc in locations:
        displays.append(loc['displayAs'])
        started = started or loc['crs'] in (START, DEST)
        if not started:
            continue
        if loc['crs'] == DEST:
            output.append(' '*30 + 'x' * (lateness_as_mins(loc) or 0))
            match = True
        output.append(loc['crs'] + ' ' + lateness_as_str(loc))
        output[-1] += '\t' + loc['displayAs']
        # output[-1] += '\t' + loc['gbttBookedDeparture']
        if match:
            break
    print service_uid
    if output:
        print '\t' + '\n\t'.join(output)
        print extra
        print

print Counter(displays)