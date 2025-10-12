import datetime

import pytest
from freezegun import freeze_time

from traintimes.sdk import Location, ResponseError, Service


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


class TestErrorHandling:
    """Test error scenarios in the get() method"""

    def test_non_ok_response_with_json_error(self, requests_mock):
        """Test handling of non-OK response with JSON error payload"""
        subject = Location('HIB')
        requests_mock.get(
            subject.uri,
            json={'error': 'Service unavailable', 'errcode': '503'},
            status_code=503
        )
        with pytest.raises(ResponseError) as exc:
            subject.get()
        assert exc.value.message == '503: Service unavailable'

    def test_non_ok_response_with_non_json(self, requests_mock):
        """Test handling of non-OK response with non-JSON body"""
        subject = Location('HIB')
        requests_mock.get(subject.uri, text='<html>Error</html>', status_code=404, reason='Not Found')
        with pytest.raises(ResponseError) as exc:
            subject.get()
        assert exc.value.message == 'Not Found'

    def test_non_ok_response_with_json_but_no_error_key(self, requests_mock):
        """Test handling of non-OK response with JSON but no error key"""
        subject = Location('HIB')
        requests_mock.get(
            subject.uri,
            json={'message': 'Something went wrong'},
            status_code=500,
            reason='Internal Server Error'
        )
        with pytest.raises(ResponseError) as exc:
            subject.get()
        assert exc.value.message == '500: Internal Server Error'

    def test_ok_response_with_invalid_json(self, requests_mock):
        """Test handling of OK response with invalid JSON"""
        subject = Location('HIB')
        requests_mock.get(subject.uri, text='<html>Not JSON</html>', status_code=200)
        with pytest.raises(ResponseError) as exc:
            subject.get()
        assert 'response.text=' in exc.value.message
