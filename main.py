import logging
from typing import Optional
from pathlib import Path
import json
import sys

from pydantic.json import pydantic_encoder
from pydantic import ValidationError, parse_obj_as
import typer

from src.classify import classify_flight, load_airports
from src.errors import AirportNotFoundError
from src.models import (
    IataCode,
    ClassifiedFlight,
    ClassifiedFlights,
    ReadFlight,
    ReadFlights,
)

JSON_OPTS = dict(default=pydantic_encoder, ensure_ascii=False)

# setup logger
logger = logging.getLogger(name="main")
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s", "%d.%m.%Y %H:%M:%S"
)
file_handler = logging.FileHandler("logs.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.CRITICAL)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)

app = typer.Typer()


@app.command()
def schemas():
    """
    Show json schema(s)
    """
    print("Output schema (for `classify`) \n\n", ClassifiedFlight.schema_json(indent=2))
    print(
        "\n\nOutput schema (for `classify-batch`) \n\n",
        ClassifiedFlights.schema_json(indent=2),
    )
    print("\n\nInput schema \n\n", ReadFlights.schema_json(indent=2))


@app.command()
def classify(
    departure_iata: str,
    arrival_iata: str,
    write_to: Optional[Path] = typer.Argument(None, help="Write output to PATH"),
):
    """
    Classify a single flight
    """
    if departure_iata == arrival_iata:
        logger.log(
            msg="Can't classify a flight from one airport to itself",
            level=logging.CRITICAL,
        )
        raise typer.Exit(code=1)

    airports = load_airports()

    try:
        departure_code = parse_obj_as(IataCode, departure_iata)
        arrival_code = parse_obj_as(IataCode, arrival_iata)
    except ValidationError as e:
        logger.log(
            msg="At least one code is not a valid iata code (cf. log)",
            level=logging.CRITICAL,
        )
        logger.exception(e)

        raise typer.Exit(code=1)

    try:
        flight = classify_flight(airports, departure_code, arrival_code)

        if write_to is not None:
            with open(write_to, "w") as f:
                json.dump(flight, f, **JSON_OPTS)
            raise typer.Exit()
        print(flight.json())
    except AirportNotFoundError as e:
        logger.log(
            msg="At least one airport not found (cf. log)", level=logging.CRITICAL
        )
        logger.exception(e)


@app.command()
def classify_batch(
    read_from: Path,
    write_to: Optional[Path] = typer.Argument(None, help="Write output to PATH"),
):
    """
    Classify a batch of flights

    Duplicate flights in `read_from` are ignored.
    """

    airports = load_airports()

    with open(read_from, "r") as f:
        read_data = json.load(f)

    flights = list()

    try:
        read_flights = {
            ReadFlight(**flight)
            for flight in read_data
            if flight["departure"]["iata"] != flight["arrival"]["iata"]
        }
    except (KeyError, ValidationError) as e:
        logger.log(
            msg="Malformatted input (cf. log)",
            level=logging.CRITICAL,
        )
        logger.exception(e)
        raise typer.Exit(code=1)

    for read_flight in read_flights:
        msg = f"trying {read_flight.departure.iata}-{read_flight.arrival.iata}"
        logger.log(msg=msg, level=logging.INFO)
        try:
            flight = classify_flight(
                airports, read_flight.departure.iata, read_flight.arrival.iata
            )
            flights.append(flight)
        except AirportNotFoundError as e:
            logger.log(
                msg="Airport not found",
                level=logging.ERROR,
            )
            logger.exception(e)

    if write_to is not None:
        with open(write_to, "w") as f:
            json.dump(flights, f, **JSON_OPTS)
        raise typer.Exit()
    print(json.dumps(flights, **JSON_OPTS))


if __name__ == "__main__":
    app()
