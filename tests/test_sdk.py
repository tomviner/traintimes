import datetime

import pytest
import requests_mock
from freezegun import freeze_time

from traintimes.sdk import Location, ResponseError, Service


@pytest.fixture
def dt():
    with freeze_time("2015-10-16 21:52:00"):
        yield


class TestLocation(object):
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
            self.expected_base + 'HIB/to/CHX/2015/10/16'

    def test_time(self, dt):
        assert Location('HIB', 'CHX', datetime.datetime.now()).uri == \
            self.expected_base + 'HIB/to/CHX/2015/10/16/2152'

    def test_arrivals(self, dt):
        assert Location('HIB', 'CHX', datetime.datetime.now(), True).uri == \
            self.expected_base + 'HIB/to/CHX/2015/10/16/2152/arrivals'


class TestService(object):
    """
    /(json|xml)/service/<serviceUid>/<year>/<month>/<day>
    """
    expected_base = 'https://api.rtt.io/api/v1/json/service/'

    def test_service_date(self, dt):
        assert Service('W12345', datetime.date.today()).uri == \
            self.expected_base + 'W12345/2015/10/16'

    def test_service_datetime(self, dt):
        assert Service('W12345', datetime.datetime.now()).uri == \
            self.expected_base + 'W12345/2015/10/16'


def test_get_raises_response_error():
    subject = Location('HIB')
    with requests_mock.Mocker() as mocker:
        adapter = mocker.get(
            subject.uri,
            json={'error': 'failure message', 'errcode': 'E_TEST'},
        )

        with pytest.raises(ResponseError) as excinfo:
            subject.get()

        assert str(excinfo.value) == 'E_TEST: failure message'
        assert adapter.called
        assert mocker.last_request.url == subject.uri


def test_get_returns_json_payload():
    subject = Location('HIB')
    expected_payload = {'success': True}

    with requests_mock.Mocker() as mocker:
        mocker.get(subject.uri, json=expected_payload)

        assert subject.get() == expected_payload
