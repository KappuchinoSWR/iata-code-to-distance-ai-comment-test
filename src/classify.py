from typing import Literal
import json

from typing import List

from pydantic import PositiveInt
from vincenty import vincenty

from .models import Airport, ClassifiedFlight, Flight, IataCode
from .errors import AirportNotFoundError


def load_airports() -> List[Airport]:
    """
    Load airports
    """
    with open("data/airports.json", "r") as f:
        airports = json.load(f)

    return [Airport(**airport) for airport in airports]


def find_airport(
    airports: List[Airport], value: str, key: Literal["code", "name"] = "code"
) -> Airport:
    """
    Returns the first matching airport.

    Raises `AirportNotFoundError` if no airport is found.
    """
    value = value.lower()

    def filter_by(airport: Airport, value=value) -> bool:
        if key == "name":
            return value in airport.name.lower()
        return airport.code.lower() == value

    airport = next(
        (airport for airport in airports if filter_by(airport)),
        None,
    )
    if airport is None:
        msg = f"Airport not found ({value}, {key})"
        raise AirportNotFoundError(msg)

    return airport


def get_flight_distance(departure: Airport, arrival: Airport) -> PositiveInt:
    """Get distance from departure airport to arrival airport in kilometres as measured by Vincenty's formulae"""
    _from = departure.position.as_tuple()
    _to = arrival.position.as_tuple()
    return int(vincenty(_from, _to, miles=False))


def classify_flight(
    airports: List[Airport], departure_code: IataCode, arrival_code: IataCode
) -> ClassifiedFlight:
    """Classify a flight from airport with `departure_code` to airport with `arrival_code`"""
    flight = Flight(
        [
            find_airport(airports, departure_code),
            find_airport(airports, arrival_code),
        ]
    )

    distance = get_flight_distance(*flight)

    return ClassifiedFlight(
        departure=flight[0].code, arrival=flight[1].code, distance=distance
    )
