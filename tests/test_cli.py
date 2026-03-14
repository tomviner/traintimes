import datetime as dt
import json
from unittest.mock import MagicMock

from typer.testing import CliRunner

from traintimes import cli
from traintimes.models import (
    LocationResponse,
    ServiceResponse,
    ServiceType,
    StationSummary,
)


runner = CliRunner()


class DummyLocation:
    last_kwargs: dict | None = None

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        DummyLocation.last_kwargs = kwargs

    def get(self):
        return LocationResponse(
            location=StationSummary(name="Test Station", crs="TST"),
            services=[],
        )


class DummyService:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs

    def get(self):
        return ServiceResponse(
            service_uid="A12345",
            run_date=dt.date(2024, 1, 1),
            service_type=ServiceType.TRAIN,
            is_passenger=True,
            train_identity=None,
            power_type=None,
            train_class=None,
            sleeper=None,
            atoc_code="ZZ",
            atoc_name="Test",
            performance_monitored=True,
            origin=[],
            destination=[],
            locations=[],
            realtime_activated=False,
            running_identity=None,
        )


def test_location_command_outputs_json(monkeypatch):
    monkeypatch.setattr(cli, "Location", DummyLocation)

    result = runner.invoke(cli.app, ["location", "TST"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["location"]["crs"] == "TST"


def test_location_command_requires_date_with_time():
    result = runner.invoke(cli.app, ["location", "TST", "--time", "12:30"])

    assert result.exit_code != 0
    assert "--time requires --date" in result.stderr


def test_location_command_handles_response_error(monkeypatch):
    class FailingLocation(DummyLocation):
        def get(self):  # pragma: no cover - error path
            raise cli.ResponseError("bad request")

    monkeypatch.setattr(cli, "Location", FailingLocation)

    result = runner.invoke(cli.app, ["location", "TST"])

    assert result.exit_code == 1
    assert "bad request" in result.stderr


def test_service_command_outputs_json(monkeypatch):
    monkeypatch.setattr(cli, "Service", DummyService)

    result = runner.invoke(cli.app, ["service", "A12345", "2024-01-01", "--pretty"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["serviceUid"] == "A12345"


def test_service_command_handles_response_error(monkeypatch):
    class FailingService(DummyService):
        def get(self):  # pragma: no cover - error path
            raise cli.ResponseError("oops")

    monkeypatch.setattr(cli, "Service", FailingService)

    result = runner.invoke(cli.app, ["service", "A12345", "2024-01-01"])

    assert result.exit_code == 1
    assert "oops" in result.stderr


def test_location_command_combines_date_and_time(monkeypatch):
    monkeypatch.setattr(cli, "Location", DummyLocation)

    result = runner.invoke(
        cli.app,
        ["location", "TST", "--date", "2024-01-02", "--time", "12:30"],
    )

    assert result.exit_code == 0
    when = DummyLocation.last_kwargs["when"]
    assert isinstance(when, dt.datetime)
    assert when.date() == dt.date(2024, 1, 2)
    assert when.time() == dt.time(12, 30)


def test_location_command_handles_plain_dict_response(monkeypatch):
    class DictLocation(DummyLocation):
        def get(self):
            return {"location": {"name": "Dict Station"}}

    monkeypatch.setattr(cli, "Location", DictLocation)

    result = runner.invoke(cli.app, ["location", "TST", "--pretty"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["location"]["name"] == "Dict Station"


def test_main_invokes_app(monkeypatch):
    fake_app = MagicMock()
    monkeypatch.setattr(cli, "app", fake_app)

    cli.main()

    fake_app.assert_called_once_with()
