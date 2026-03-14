import datetime as dt
import json

from traintimes import cli
from traintimes.models import (
    LocationEvent,
    LocationResponse,
    ServiceResponse,
    ServiceType,
    StationSummary,
)


def _make_location_response() -> LocationResponse:
    return LocationResponse(
        location=StationSummary(name="Highbury & Islington", crs="HIB"),
        services=[],
    )


def _make_service_response() -> ServiceResponse:
    return ServiceResponse(
        service_uid="A12345",
        run_date=dt.date(2024, 1, 1),
        service_type=ServiceType.TRAIN,
        is_passenger=True,
        atoc_code="ZZ",
        atoc_name="Zed Rail",
        performance_monitored=True,
        origin=[],
        destination=[],
        locations=[LocationEvent(tiploc="DEST")],
    )


def test_location_command_outputs_json(monkeypatch, capsys):
    captured: dict[str, object] = {}
    sample = _make_location_response()

    class DummyLocation:
        def __init__(
            self,
            station: str,
            to_station: str | None = None,
            when: dt.date | dt.datetime | None = None,
            arrivals: bool = False,
            **_: object,
        ) -> None:
            captured["station"] = station
            captured["to_station"] = to_station
            captured["when"] = when
            captured["arrivals"] = arrivals

        def get(self) -> LocationResponse:
            return sample

    monkeypatch.setattr(cli, "Location", DummyLocation)

    exit_code = cli.main(["location", "--station", "HIB"])

    assert exit_code == 0
    assert captured == {
        "station": "HIB",
        "to_station": None,
        "when": None,
        "arrivals": False,
    }

    out = capsys.readouterr()
    assert out.err == ""
    assert json.loads(out.out) == sample.model_dump(mode="json", by_alias=True)


def test_location_command_parses_datetime(monkeypatch):
    captured: dict[str, object] = {}
    sample = _make_location_response()

    class DummyLocation:
        def __init__(
            self,
            station: str,
            to_station: str | None = None,
            when: dt.date | dt.datetime | None = None,
            arrivals: bool = False,
            **_: object,
        ) -> None:
            captured["station"] = station
            captured["to_station"] = to_station
            captured["when"] = when
            captured["arrivals"] = arrivals

        def get(self) -> LocationResponse:
            return sample

    monkeypatch.setattr(cli, "Location", DummyLocation)

    exit_code = cli.main(
        [
            "location",
            "--station",
            "HIB",
            "--to-station",
            "KGX",
            "--when",
            "2024-04-01T12:45",
            "--arrivals",
            "true",
        ]
    )

    assert exit_code == 0
    assert captured["station"] == "HIB"
    assert captured["to_station"] == "KGX"
    assert isinstance(captured["when"], dt.datetime)
    assert captured["when"] == dt.datetime(2024, 4, 1, 12, 45)
    assert captured["arrivals"] is True


def test_service_command_outputs_json(monkeypatch, capsys):
    captured: dict[str, object] = {}
    sample = _make_service_response()

    class DummyService:
        def __init__(
            self, service: str, date: dt.date | dt.datetime, **_: object
        ) -> None:
            captured["service"] = service
            captured["date"] = date

        def get(self) -> ServiceResponse:
            return sample

    monkeypatch.setattr(cli, "Service", DummyService)

    exit_code = cli.main(["service", "--service-uid", "A12345", "--date", "2024-01-01"])

    assert exit_code == 0
    assert captured["service"] == "A12345"
    assert isinstance(captured["date"], dt.date)
    assert captured["date"] == dt.date(2024, 1, 1)

    out = capsys.readouterr()
    assert out.err == ""
    assert json.loads(out.out) == sample.model_dump(mode="json", by_alias=True)


def test_run_invokes_sys_exit(monkeypatch, capsys):
    captured: dict[str, object] = {}
    sample = _make_location_response()

    class DummyLocation:
        def __init__(
            self,
            station: str,
            to_station: str | None = None,
            when: dt.date | dt.datetime | None = None,
            arrivals: bool = False,
            **_: object,
        ) -> None:
            captured["station"] = station
            captured["to_station"] = to_station
            captured["when"] = when
            captured["arrivals"] = arrivals

        def get(self) -> LocationResponse:
            return sample

    monkeypatch.setattr(cli, "Location", DummyLocation)
    monkeypatch.setattr(cli.sys, "argv", ["traintimes", "location", "--station", "HIB"])
    exit_codes: list[int] = []
    monkeypatch.setattr(cli.sys, "exit", exit_codes.append)

    cli.run()

    assert exit_codes == [0]
    assert captured == {
        "station": "HIB",
        "to_station": None,
        "when": None,
        "arrivals": False,
    }

    out = capsys.readouterr()
    assert out.err == ""
    assert json.loads(out.out) == sample.model_dump(mode="json", by_alias=True)
