import datetime
import os
import logging

import requests
import requests_cache

from purl import Template


logging.basicConfig(level=logging.DEBUG)
cache_dir = '.requests_cache'
try:
    os.mkdir(cache_dir)
except OSError:
    pass
requests_cache.install_cache(os.path.join(cache_dir, 'cache'))


class RTTBase(object):
    """ Base Class for RealTimeTrains API

    See http://www.realtimetrains.co.uk/api

    Apply for API access at https://api.rtt.io/
    Set environ variable:
        export RTT_AUTH=user:password
    """
    # URI template language as per RFC6570
    base_uri_template = 'https://api.rtt.io/api/{version}/{accept}'
    auth = tuple(os.environ['RTT_AUTH'].split(':'))

    def __init__(self, version='v1', accept='json'):
        self.context = {'version': version, 'accept': accept}

    def add_to_context(self, key, value):
        self.context[key] = value

    @property
    def uri(self):
        uri_template = Template(self.base_uri_template + self.uri_template)
        return uri_template.expand(self.context).as_string()

    def __repr__(self):
        return self.uri

    def get(self):
        return requests.get(self.uri, auth=self.auth).json()


class Location(RTTBase):
    """ Location List API

    http://www.realtimetrains.co.uk/api/pull/locationlist
    /(json|xml)/search/<station>/<year>/<month>/<day>/<time>/arrivals
    """

    uri_template = '/search/{station}{+tostation}{+date}{+time}{/arrivals}'

    def __init__(
            self, station, to_station=None, when=None, arrivals=False,
            **kwargs):
        super(Location, self).__init__(**kwargs)

        self.add_to_context('station', station)

        if to_station:
            self.add_to_context('tostation', '/to/{}'.format(to_station))

        if isinstance(when, datetime.date):
            self.add_to_context('date', '/{0:%Y}/{0:%m}/{0:%d}'.format(when))

        if isinstance(when, datetime.datetime):
            self.add_to_context('time', '/{0:%H}{0:%M}'.format(when))

        if arrivals:
            self.add_to_context('arrivals', 'arrivals')


class Service(RTTBase):
    """Service Information API

    http://www.realtimetrains.co.uk/api/pull/serviceinfo
    /(json|xml)/service/<serviceUid>/<year>/<month>/<day>
    """

    uri_template = '/service{/service}{+date}'

    def __init__(self, service, date, **kwargs):
        super(Service, self).__init__(**kwargs)

        self.add_to_context('service', service)

        assert isinstance(date, datetime.date), \
            "Expected {} got {}".format(datetime.date, type(date))
        self.add_to_context('date', '/{0:%Y}/{0:%m}/{0:%d}'.format(date))
