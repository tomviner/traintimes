import datetime

import pytest
from freezegun import freeze_time

from traintimes.sdk import Location, ResponseError, Service


@pytest.fixture
def dt():
    with freeze_time("2025-10-16 21:52:00"):
        yield


class TestLocation:
    """Test Location endpoint URI generation for all endpoint combinations"""

    expected_base = 'https://api.rtt.io/api/v1/json/search/'

    def test_repr(self):
        assert Location('HIB').uri == repr(Location('HIB'))

    def test_station_only(self):
        """Normal queries (live departures): /json/search/<station>"""
        assert Location('HIB').uri == self.expected_base + 'HIB'

    def test_station_with_to_station(self):
        """Normal queries filtered to a location: /json/search/<station>/to/<toStation>"""
        assert Location('HIB', 'CHX').uri == self.expected_base + 'HIB/to/CHX'

    def test_station_with_date(self, dt):
        """Queries for all services on a specific date: /json/search/<station>/<year>/<month>/<day>"""
        assert (
            Location('HIB', when=datetime.date.today()).uri
            == self.expected_base + 'HIB/2025/10/16'
        )

    def test_station_with_to_station_and_date(self, dt):
        """Filtered queries on a specific date"""
        assert (
            Location('HIB', 'CHX', datetime.date.today()).uri
            == self.expected_base + 'HIB/to/CHX/2025/10/16'
        )

    def test_station_with_datetime(self, dt):
        """Queries for services on a specific date and time: /json/search/<station>/<year>/<month>/<day>/<time>"""
        assert (
            Location('HIB', when=datetime.datetime.now()).uri
            == self.expected_base + 'HIB/2025/10/16/2152'
        )

    def test_station_with_to_station_and_datetime(self, dt):
        """Filtered queries on a specific date and time"""
        assert (
            Location('HIB', 'CHX', datetime.datetime.now()).uri
            == self.expected_base + 'HIB/to/CHX/2025/10/16/2152'
        )

    def test_station_with_arrivals(self):
        """Station with /arrivals appended"""
        assert Location('HIB', arrivals=True).uri == self.expected_base + 'HIB/arrivals'

    def test_station_with_date_and_arrivals(self, dt):
        """Date query with /arrivals appended"""
        assert (
            Location('HIB', when=datetime.date.today(), arrivals=True).uri
            == self.expected_base + 'HIB/2025/10/16/arrivals'
        )

    def test_station_with_datetime_and_arrivals(self, dt):
        """Datetime query with /arrivals appended"""
        assert (
            Location('HIB', when=datetime.datetime.now(), arrivals=True).uri
            == self.expected_base + 'HIB/2025/10/16/2152/arrivals'
        )

    def test_station_with_to_station_datetime_and_arrivals(self, dt):
        """Full combination: filtered query with date/time and arrivals"""
        assert (
            Location('HIB', 'CHX', datetime.datetime.now(), True).uri
            == self.expected_base + 'HIB/to/CHX/2025/10/16/2152/arrivals'
        )


class TestService:
    """Test Service endpoint URI generation"""

    expected_base = 'https://api.rtt.io/api/v1/json/service/'

    def test_service_with_date(self, dt):
        """Service with date: /json/service/<serviceUid>/<year>/<month>/<day>"""
        assert (
            Service('W12345', datetime.date.today()).uri
            == self.expected_base + 'W12345/2025/10/16'
        )

    def test_service_with_datetime(self, dt):
        """Service with datetime (date part extracted): /json/service/<serviceUid>/<year>/<month>/<day>"""
        assert (
            Service('W12345', datetime.datetime.now()).uri
            == self.expected_base + 'W12345/2025/10/16'
        )


class TestErrorHandling:
    """Test error scenarios in the get() method"""

    def test_non_ok_response_with_json_error(self, requests_mock):
        """Test handling of non-OK response with JSON error payload"""
        subject = Location('HIB')
        requests_mock.get(
            subject.uri,
            json={'error': 'Service unavailable', 'errcode': '503'},
            status_code=503,
        )
        with pytest.raises(ResponseError) as exc:
            subject.get()
        assert exc.value.message == '503: Service unavailable'

    def test_non_ok_response_with_non_json(self, requests_mock):
        """Test handling of non-OK response with non-JSON body"""
        subject = Location('HIB')
        requests_mock.get(
            subject.uri, text='<html>Error</html>', status_code=404, reason='Not Found'
        )
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
            reason='Internal Server Error',
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

    def test_ok_response_with_json_error(self, requests_mock):
        """Test handling of OK response containing an error payload"""
        subject = Location('HIB')
        requests_mock.get(
            subject.uri,
            json={'error': 'Service unavailable', 'errcode': '503'},
            status_code=200,
        )
        with pytest.raises(ResponseError) as exc:
            subject.get()
        assert exc.value.message == '503: Service unavailable'

    def test_ok_response_returns_payload(self, requests_mock):
        """Test successful OK response returns JSON payload"""
        subject = Location('HIB')
        payload = {'services': []}
        requests_mock.get(subject.uri, json=payload, status_code=200)
        assert subject.get() == payload
