from datetime import datetime
from pprint import pprint
from collections import Counter

from sdk import Location, Service


# https://api.rtt.io/api/v1/json/search/HIB/to/CHX/2015/10/14/0800

# jq '.services | .[] | .locationDetail | "\(.gbttBookedDeparture),\(.destination[0].publicTime),\(.realtimeDeparture),\(.realtimeArrival),\(.destination[0].tiploc)"' | sed s/'"'//g | sed s/^/"'"/ | grep CH

chx_services = []

for hour in range(18, 21):
    date = datetime(2015, 10, 16, hour, 0)
    data = Location('CHX', 'HIB', date).get()

    for s in data['services']:
        chx_services.append(s['serviceUid'])
#         if s['serviceUid'] in chx_services:
#             continue
#         ld = s['locationDetail']
#         print s['serviceUid'], ld['gbttBookedDeparture']
#         dests = ld['destination']
#         assert len(dests) == 1, dests
#         dest = dests[0]
#         if dest['tiploc'] != "CHRX":
#             continue
#         assert ld['crs'] == "HIB", ld['crs']
#         chx_services.append(s['serviceUid'])

displays = []
for service_uid in chx_services:
    data = Service(service_uid, date).get()

    locations = data['locations']
    match = False
    parts = []
    for loc in locations:
        displays.append(loc['displayAs'])
        if loc['crs'] == 'CHX':
            parts.extend([loc.get('gbttBookedDeparture', '?'), loc.get('realtimeDeparture', '?')])
        if loc['crs'] == 'HIB':
            match = True
            parts.extend([loc.get('gbttBookedDeparture', '?'), loc.get('realtimeDeparture', '?')])
    if not match:
        continue
    if len(parts) == 4:
        print "'" + ','.join(parts)
#     for loc in locations[:-1]:
#         if loc['crs'] == 'HIB':
#             if loc['displayAs'] in ('CALL', 'ORIGIN', 'STARTS'):
#                 parts.extend([loc.get('gbttBookedDeparture', '?'), loc.get('realtimeDeparture', '?')])
#             else:
#                 parts.extend([loc.get('gbttBookedDeparture', '?'), '-'])
#     loc = locations[-1]
#     if loc['displayAs'] == 'DESTINATION':
#         parts.extend([loc.get('realtimeArrival', '?'), loc.get('gbttBookedArrival', '?')])

print Counter(displays)
