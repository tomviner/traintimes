import datetime

import pytest
from freezegun import freeze_time

from sdk import Location, Service
from utils import date_in_range


@pytest.yield_fixture
def frozen_date():
    """ Test against a known, rarely changing date, within range.

    API covers -7 to +90 days from current date.
    Requests using the free API are currently limited to 50 per day.
    So choose one datetime "per season", and use requests_cache to avoid repeat
    requests.
    """
    date = date_in_range()
    dt = datetime.datetime.combine(date, datetime.time(12, 0, 0))
    with freeze_time(dt):
        yield dt


class TestLocation(object):
    """
    /(json|xml)/search/<station>/<year>/<month>/<day>/<time>/arrivals
    """
    expected_base = 'https://api.rtt.io/api/v1/json/search/'

    def test_station(self):
        assert Location('HIB').get()

    def test_to_station(self):
        assert Location('HIB', 'CHX').get()

    def test_date(self, frozen_date):
        assert Location('HIB', 'CHX', datetime.date.today()).get()

    def test_time(self, frozen_date):
        assert Location('HIB', 'CHX', datetime.datetime.now()).get()

    def test_arrivals(self, frozen_date):
        assert Location('HIB', 'CHX', datetime.datetime.now(), True).get()


class TestService(object):
    """
    /(json|xml)/service/<serviceUid>/<year>/<month>/<day>
    """
    expected_base = 'https://api.rtt.io/api/v1/json/service/'

    def test_service_date(self, frozen_date):
        assert Service('W27124', datetime.date.today()).get()

    def test_service_datetime(self, frozen_date):
        assert Service('W27124', datetime.datetime.now()).get()
