"""Command line interface for the traintimes SDK."""

from __future__ import annotations

import datetime as dt
import json
from typing import Any

import typer

from .sdk import Location, ResponseError, Service


app = typer.Typer(help="Interact with the RealTimeTrains API via the SDK.")


def _dump_model(model: Any, pretty: bool) -> str:
    """Return a JSON representation of a Pydantic model."""

    if hasattr(model, "model_dump_json"):
        indent = 2 if pretty else None
        return model.model_dump_json(indent=indent, by_alias=True)
    return json.dumps(model, indent=2 if pretty else None)


def _parse_date(value: str | None) -> dt.date | None:
    """Parse a YYYY-MM-DD date string."""

    if value is None:
        return None
    try:
        return dt.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:  # pragma: no cover - exercised via CLI tests
        raise typer.BadParameter(
            "Dates must be provided in YYYY-MM-DD format", param_hint="--date"
        ) from exc


def _parse_time(value: str | None) -> dt.time | None:
    """Parse a HH:MM time string."""

    if value is None:
        return None
    try:
        parsed = dt.datetime.strptime(value, "%H:%M")
        return parsed.time().replace(second=0, microsecond=0)
    except ValueError as exc:  # pragma: no cover - exercised via CLI tests
        raise typer.BadParameter(
            "Times must be provided in HH:MM format", param_hint="--time"
        ) from exc


def _combine_datetime(
    date: dt.date | None, time: dt.time | None
) -> dt.date | dt.datetime | None:
    """Combine date and time options into a datetime-like object."""

    if time and not date:
        raise typer.BadParameter(
            "--time requires --date to be provided", param_hint="--time"
        )
    if date and time:
        return dt.datetime.combine(date, time)
    return date


@app.command()
def location(
    station: str = typer.Argument(..., help="CRS or TIPLOC of the station to query."),
    to: str | None = typer.Option(
        None,
        "--to",
        help="Filter services to those heading towards the supplied CRS or TIPLOC.",
    ),
    date: str | None = typer.Option(
        None,
        "--date",
        help="Limit results to a specific date (YYYY-MM-DD).",
    ),
    time: str | None = typer.Option(
        None,
        "--time",
        help="Limit results to services at/after the supplied time (HH:MM).",
    ),
    arrivals: bool = typer.Option(
        False,
        "--arrivals/--departures",
        help="Show arrivals instead of departures.",
    ),
    pretty: bool = typer.Option(
        False,
        "--pretty",
        help="Pretty print the JSON response.",
    ),
) -> None:
    """Query the location line-up endpoint."""

    parsed_date = _parse_date(date)
    parsed_time = _parse_time(time)
    when = _combine_datetime(parsed_date, parsed_time)

    try:
        response = Location(
            station=station,
            to_station=to,
            when=when,
            arrivals=arrivals,
        ).get()
    except ResponseError as exc:
        typer.secho(str(exc), err=True, fg=typer.colors.RED)
        raise typer.Exit(1) from exc

    typer.echo(_dump_model(response, pretty))


@app.command()
def service(
    service_uid: str = typer.Argument(
        ..., help="Service UID returned from a location query."
    ),
    date: str = typer.Argument(..., help="Run date of the service (YYYY-MM-DD)."),
    pretty: bool = typer.Option(
        False,
        "--pretty",
        help="Pretty print the JSON response.",
    ),
) -> None:
    """Query the service information endpoint."""

    parsed_date = _parse_date(date)
    assert parsed_date is not None  # for type checkers

    try:
        response = Service(service=service_uid, date=parsed_date).get()
    except ResponseError as exc:
        typer.secho(str(exc), err=True, fg=typer.colors.RED)
        raise typer.Exit(1) from exc

    typer.echo(_dump_model(response, pretty))


def main() -> None:
    """Entry point used by ``python -m traintimes.cli``."""

    app()


if __name__ == "__main__":  # pragma: no cover - script entry point
    main()
