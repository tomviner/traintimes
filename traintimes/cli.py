"""Command line interface for the traintimes SDK."""

from __future__ import annotations

import datetime as _dt
import sys
from importlib import metadata
from typing import Callable

from pydantic import BaseModel, ConfigDict, Field
from pydantic_cli import Cmd, to_runner

from .sdk import Location, Service


try:
    _CLI_VERSION = metadata.version("traintimes")
except metadata.PackageNotFoundError:  # pragma: no cover - fallback when not installed
    _CLI_VERSION = None


def _render_model(model: BaseModel) -> None:
    """Pretty-print a pydantic model as JSON."""

    print(model.model_dump_json(by_alias=True, indent=2))


class _BaseCommand(Cmd):
    """Common configuration for CLI commands."""

    model_config = ConfigDict(extra="forbid")


class LocationCommand(_BaseCommand):
    """Fetch the line-up for a station."""

    station: str = Field(json_schema_extra={"cli": ("--station", "-s")})
    to_station: str | None = Field(
        default=None, json_schema_extra={"cli": ("--to-station",)}
    )
    when: _dt.date | _dt.datetime | None = Field(
        default=None, json_schema_extra={"cli": ("--when",)}
    )
    arrivals: bool = Field(default=False, json_schema_extra={"cli": ("--arrivals",)})

    def run(self) -> None:
        response = Location(
            station=self.station,
            to_station=self.to_station,
            when=self.when,
            arrivals=self.arrivals,
        ).get()
        _render_model(response)


class ServiceCommand(_BaseCommand):
    """Fetch details for a service on a given date."""

    service_uid: str = Field(json_schema_extra={"cli": ("--service-uid", "-u")})
    date: _dt.date | _dt.datetime = Field(json_schema_extra={"cli": ("--date", "-d")})

    def run(self) -> None:
        response = Service(self.service_uid, self.date).get()
        _render_model(response)


_COMMANDS: dict[str, type[Cmd]] = {
    "location": LocationCommand,
    "service": ServiceCommand,
}


def build_runner() -> Callable[[list[str]], int]:
    """Construct the CLI runner."""

    return to_runner(
        _COMMANDS,
        description="Command line interface for RealTimeTrains.",
        version=_CLI_VERSION,
    )


def main(argv: list[str] | None = None) -> int:
    """Execute the CLI with the provided arguments."""

    args = sys.argv[1:] if argv is None else argv
    runner = build_runner()
    return runner(args)


def run() -> None:
    """Entry point for the ``traintimes`` console script."""

    sys.exit(main())


__all__ = [
    "LocationCommand",
    "ServiceCommand",
    "build_runner",
    "main",
    "run",
]
