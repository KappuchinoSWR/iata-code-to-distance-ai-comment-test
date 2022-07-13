import logging
from typing import Optional
from pathlib import Path
import json

from pydantic.json import pydantic_encoder
import typer

import src.test
from src.classify import classify_flight, load_airports
from src.errors import AirportNotFoundError
from src.models import IataCode

app = typer.Typer()


JSON_OPTS = dict(default=pydantic_encoder, ensure_ascii=False)


@app.command()
def test():
    src.test.test()
    print("Everything seems to work")


@app.command()
def classify(departure_iata: str, arrival_iata: str, write_to: Optional[Path] = None):
    if departure_iata == arrival_iata:
        print("Can't classify a flight from one airport to itself")
        return
    airports = load_airports()
    departure_code = IataCode(departure_iata)
    arrival_code = IataCode(arrival_iata)
    try:
        flight = classify_flight(airports, departure_code, arrival_code)

        if write_to is not None:
            with open(write_to, "w") as f:
                json.dump(flight, f, **JSON_OPTS)
            return
        print(flight.json())
        return
    except AirportNotFoundError as e:
        print("At least one airport not found")
        logging.exception(e)


@app.command()
def classify_batch(read_from: Path, write_to: Path = typer.Argument(...)):
    airports = load_airports()

    with open(read_from, "r") as f:
        read_data = json.load(f)

    flights = list()

    arrival_depature_pairs = set()
    for flight in read_data:
        departure_code = flight["departure"]["iata"]
        arrival_code = flight["arrival"]["iata"]
        if departure_code != arrival_code:
            arrival_depature_pairs.add((departure_code, arrival_code))

    for departure_code, arrival_code in arrival_depature_pairs:
        msg = f"trying {departure_code}-{arrival_code}"
        logging.log(msg=msg, level=logging.DEBUG)
        try:
            flight = classify_flight(airports, departure_code, arrival_code)
            flights.append(flight)
        except AirportNotFoundError as e:
            SystemExit("At least one airport not found")
            logging.exception(e)

    if write_to is not Path():
        with open(write_to, "w") as f:
            json.dump(flights, f, **JSON_OPTS)
        return
    print(json.dumps(flights, **JSON_OPTS))


if __name__ == "__main__":
    app()
