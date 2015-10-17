import datetime

import pytest
from freezegun import freeze_time

from sdk import Location, Service


@pytest.yield_fixture
def dt():
    with freeze_time("2015-10-16 21:52:00"):
        yield


class TestLocation(object):
    """
    /(json|xml)/search/<station>/<year>/<month>/<day>/<time>/arrivals
    """
    expected_base = 'https://api.rtt.io/api/v1/json/search/'

    def test_repr(self):
        assert Location('HIB').url == repr(Location('HIB'))

    def test_station(self):
        assert Location('HIB').url == self.expected_base + 'HIB'

    def test_to_station(self):
        assert Location('HIB', 'CHX').url == self.expected_base + 'HIB/to/CHX'

    def test_date(self, dt):
        assert Location('HIB', 'CHX', datetime.date.today()).url == \
            self.expected_base + 'HIB/to/CHX/2015/10/16'

    def test_time(self, dt):
        assert Location('HIB', 'CHX', datetime.datetime.now()).url == \
            self.expected_base + 'HIB/to/CHX/2015/10/16/2152'

    def test_arrivals(self, dt):
        assert Location('HIB', 'CHX', datetime.datetime.now(), True).url == \
            self.expected_base + 'HIB/to/CHX/2015/10/16/2152/arrivals'


class TestService(object):
    """
    /(json|xml)/service/<serviceUid>/<year>/<month>/<day>
    """
    expected_base = 'https://api.rtt.io/api/v1/json/service/'

    def test_service_date(self, dt):
        assert Service('W12345', datetime.date.today()).url == \
            self.expected_base + 'W12345/2015/10/16'

    def test_service_datetime(self, dt):
        assert Service('W12345', datetime.datetime.now()).url == \
            self.expected_base + 'W12345/2015/10/16'
