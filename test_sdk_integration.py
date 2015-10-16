import datetime

from sdk import Location, Service


class TestLocation(object):
    """
    /(json|xml)/search/<station>/<year>/<month>/<day>/<time>/arrivals
    """
    expected_base = 'https://api.rtt.io/api/v1/json/search/'

    def test_station(self):
        assert Location('HIB').get()

    def test_to_station(self):
        assert Location('HIB', 'CHX').get()

    def test_date(self):
        assert Location('HIB', 'CHX', datetime.date.today()).get()

    def test_time(self):
        assert Location('HIB', 'CHX', datetime.datetime.now()).get()

    def test_arrivals(self):
        assert Location('HIB', 'CHX', datetime.datetime.now(), True).get()


class TestService(object):
    """
    /(json|xml)/service/<serviceUid>/<year>/<month>/<day>
    """
    expected_base = 'https://api.rtt.io/api/v1/json/service/'

    def test_service_date(self):
        assert Service('W27124', datetime.date.today()).get()

    def test_service_datetime(self):
        assert Service('W27124', datetime.datetime.now()).get()
