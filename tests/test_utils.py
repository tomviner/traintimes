import datetime

import pytest
from freezegun import freeze_time
from utils import date_in_range


@pytest.fixture(params=range(0, 366, 10))
def frozen_date_over_year(request):
    dt = datetime.date.today() + datetime.timedelta(days=request.param)
    with freeze_time(dt):
        yield dt


def test_date_in_range(frozen_date_over_year):
    delta = date_in_range() - frozen_date_over_year
    assert datetime.timedelta(days=-7) < delta < datetime.timedelta(days=90)
