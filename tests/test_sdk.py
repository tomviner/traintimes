import datetime

import pytest
from freezegun import freeze_time

from traintimes.sdk import Location, Service


@pytest.fixture
def dt():
    with freeze_time("2025-10-16 21:52:00"):
        yield


class TestLocation:
    """
    /(json|xml)/search/<station>/<year>/<month>/<day>/<time>/arrivals
    """
    expected_base = 'https://api.rtt.io/api/v1/json/search/'

    def test_repr(self):
        assert Location('HIB').uri == repr(Location('HIB'))

    def test_station(self):
        assert Location('HIB').uri == self.expected_base + 'HIB'

    def test_to_station(self):
        assert Location('HIB', 'CHX').uri == self.expected_base + 'HIB/to/CHX'

    def test_date(self, dt):
        assert Location('HIB', 'CHX', datetime.date.today()).uri == \
            self.expected_base + 'HIB/to/CHX/2025/10/16'

    def test_time(self, dt):
        assert Location('HIB', 'CHX', datetime.datetime.now()).uri == \
            self.expected_base + 'HIB/to/CHX/2025/10/16/2152'

    def test_arrivals(self, dt):
        assert Location('HIB', 'CHX', datetime.datetime.now(), True).uri == \
            self.expected_base + 'HIB/to/CHX/2025/10/16/2152/arrivals'


class TestService:
    """
    /(json|xml)/service/<serviceUid>/<year>/<month>/<day>
    """
    expected_base = 'https://api.rtt.io/api/v1/json/service/'

    def test_service_date(self, dt):
        assert Service('W12345', datetime.date.today()).uri == \
            self.expected_base + 'W12345/2025/10/16'

    def test_service_datetime(self, dt):
        assert Service('W12345', datetime.datetime.now()).uri == \
            self.expected_base + 'W12345/2025/10/16'
