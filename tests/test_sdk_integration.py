import datetime
import os

import pytest
from freezegun import freeze_time

from traintimes.sdk import Location, Service, ResponseError
from utils import date_in_range


_PLACEHOLDER_AUTH = "demo:demo"


pytestmark = pytest.mark.skipif(
    os.environ.get("RTT_AUTH") == _PLACEHOLDER_AUTH,
    reason="Integration tests require valid RTT_AUTH credentials",
)


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

@pytest.fixture
def past_dt(frozen_date):
    """ Test against a known past date """
    date = datetime.date.today() + datetime.timedelta(days=-150)
    return datetime.datetime.combine(date, datetime.time(12, 0, 0))

@pytest.fixture
def future_dt(frozen_date):
    """ Test against a known future date """
    date = datetime.date.today() + datetime.timedelta(days=150)
    return datetime.datetime.combine(date, datetime.time(12, 0, 0))

@pytest.fixture
def service_code(frozen_date):
    return Location('HIB', 'CHX', datetime.datetime.now()) \
        .get()['services'][0]['serviceUid']


class TestLocation(object):
    """
    /(json|xml)/search/<station>/<year>/<month>/<day>/<time>/arrivals
    """
    expected_base = 'https://api.rtt.io/api/v1/json/search/'

    def assert_valid_location(self, data):
        assert data.viewkeys() == {'location', 'filter', 'services'}

    def test_station(self):
        self.assert_valid_location(Location('HIB').get())

    def test_to_station(self):
        self.assert_valid_location(
            Location('HIB', 'CHX').get())

    def test_date(self, frozen_date):
        self.assert_valid_location(
            Location('HIB', 'CHX', datetime.date.today()).get())

    def test_time(self, frozen_date):
        self.assert_valid_location(
            Location('HIB', 'CHX', datetime.datetime.now()).get())

    def test_arrivals(self, frozen_date):
        self.assert_valid_location(
            Location('HIB', 'CHX', datetime.datetime.now(), True).get())

    def test_before_available_window(self, past_dt):
        with pytest.raises(ResponseError) as exc:
            assert Location('HIB', 'CHX', past_dt).get()
        assert exc.value.message == '501: searching outside available window'

    def test_after_available_window(self, future_dt):
        with pytest.raises(ResponseError) as exc:
            assert Location('HIB', 'CHX', future_dt).get()
        assert exc.value.message == '502: searching outside available window'


class TestService(object):
    """
    /(json|xml)/service/<serviceUid>/<year>/<month>/<day>
    """
    expected_base = 'https://api.rtt.io/api/v1/json/service/'

    def assert_valid_service(self, data):
        minimal_service_keys = {
            'atocCode',
            'atocName',
            'destination',
            'isPassenger',
            'locations',
            'origin',
            'performanceMonitored',
            'powerType',
            'runDate',
            'serviceType',
            'serviceUid',
            'trainClass',
            'trainIdentity'
        }
        # every key must be in the data
        assert minimal_service_keys.issubset(data.viewkeys())

    def test_service_date(self, frozen_date, service_code):
        self.assert_valid_service(
            Service(service_code, datetime.date.today()).get())

    def test_service_datetime(self, frozen_date, service_code):
        self.assert_valid_service(
            Service(service_code, datetime.datetime.now()).get())

    def test_no_schedule_found_for_far_future(self, future_dt, service_code):
        with pytest.raises(ResponseError) as exc:
            assert Service(service_code, future_dt).get()
        assert exc.value.message == '<no errcode>: No schedule found'

    def test_no_schedule_found_for_bad_service(self, frozen_date):
        with pytest.raises(ResponseError) as exc:
            assert Service('Q98765', datetime.datetime.now()).get()
        assert exc.value.message == '<no errcode>: No schedule found'
