import datetime
import os
import logging

import requests
import requests_cache

from purl import Template


logging.basicConfig(level=logging.DEBUG)
requests_cache.install_cache()


class RTTBase(object):
    base_tpl = 'https://api.rtt.io/api/{version}/{accept}'
    auth = tuple(os.environ['RTT_AUTH'].split(':'))

    def __init__(self):
        self.context = {'version': 'v1', 'accept': 'json'}

    @property
    def url(self):
        tpl = Template(self.base_tpl + self.tpl)
        return tpl.expand(self.context).as_string()

    def push(self, key, value):
        self.context[key] = value

    def __repr__(self):
        return self.url

    def get(self):
        return requests.get(self.url, auth=self.auth)


class Location(RTTBase):
    """Location List API

    http://www.realtimetrains.co.uk/api/pull/locationlist
    /(json|xml)/search/<station>/<year>/<month>/<day>/<time>/arrivals
    """
    tpl = '/search/{station}{+tostation}{+date}{+time}{/arrivals}'

    def __init__(self, station, to_station=None, when=None, arrivals=False):
        super(Location, self).__init__()

        self.push('station', station)
        if to_station:
            self.push('tostation', '/to/{}'.format(to_station))
        if isinstance(when, datetime.date):
            self.push('date', '/{0:%Y}/{0:%m}/{0:%d}'.format(when))
        if isinstance(when, datetime.datetime):
            self.push('time', '/{0:%H}{0:%M}'.format(when))
        if arrivals:
            self.push('arrivals', 'arrivals')


class Service(RTTBase):
    """Service Information API

    http://www.realtimetrains.co.uk/api/pull/serviceinfo
    /(json|xml)/service/<serviceUid>/<year>/<month>/<day>
    """
    tpl = '/service{/service}{+date}'

    def __init__(self, service, date):
        super(Service, self).__init__()

        self.push('service', service)
        assert isinstance(date, datetime.date), \
            "Expected {} got {}".format(datetime.date, type(date))
        self.push('date', '/{0:%Y}/{0:%m}/{0:%d}'.format(date))
