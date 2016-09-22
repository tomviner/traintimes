from datetime import datetime
# from pprint import pprint
from collections import Counter

from traintimes.sdk import Location, Service


# https://api.rtt.io/api/v1/json/search/HIB/to/CHX/2015/10/14/0800

# jq '.services | .[] | .locationDetail | "\(.gbttBookedDeparture),\(
# .destination[0].publicTime),\(.realtimeDeparture),\(.realtimeArrival),\(
# .destination[0].tiploc)"' | sed s/'"'//g | sed s/^/"'"/ | grep CH
START = 'CHX'
DEST = 'HIB'
# START, DEST = DEST, START

chx_services = []

# w1 - 1-7 sept
# w1 - 8-14 sept
for hour in range(19, 20):
    date = datetime(2016, 9, 13, hour, 0)
    print date
    data = Location(START, DEST, date).get()
    if not data['services']:
        continue
    #     import ipdb; ipdb.set_trace()
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
    print_detail = 1
    output = []
    # if print_detail:
    #     # print
    #     output.append('')
    for loc in locations:
        displays.append(loc['displayAs'])
        d = ''
        if loc['displayAs'] not in ('CALL', 'ORIGIN'):
            d = loc['displayAs']
            # print d
        if loc['crs'] == START:
            parts.append(get_parts(loc) + d)
        if loc['crs'] == DEST:
            match = True
            parts.append(get_parts(loc) + d)
        if print_detail:
            # print loc['crs'], get_parts(loc)
            output.append(loc['crs'] + ' ' + get_parts(loc))
            # if loc['crs'] == DEST:
        # if loc['displayAs'] not in ('CALL', 'ORIGIN'):
        output[-1] += '\t' + loc['displayAs']
        if match:
            break
    # if not match:
    #     continue
    print service_uid
    # if len(parts) == 2:
    #     # print "'" + ' - '.join(parts)
    #     output.append("'" + ' - '.join(parts))
    if output:
        print '\t' + '\n\t'.join(output)
        print
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
