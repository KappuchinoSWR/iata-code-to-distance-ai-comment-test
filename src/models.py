import enum
import re
from typing import Tuple, Optional, List

from pydantic import BaseModel, validator, ConstrainedList, ConstrainedStr, PositiveInt

from .consts import MAX_MIDDLE_FLIGHT, MAX_SHORT_FLIGHT


# Validators


def to_upper(cls, value) -> str:
    if isinstance(value, str):
        return value.upper()
    return value


# Flight type


class FlightType(str, enum.Enum):
    SHORT = "short"
    MIDDLE = "middle"
    LONG = "long"


# Airport models


class IsoCountry(ConstrainedStr):
    min_length = 2
    max_length = 2
    regex = re.compile(r"^[a-zA-Z]+$")

    @classmethod
    def __get_validators__(cls):
        yield from super().__get_validators__()
        yield to_upper


class Coordinate(BaseModel):
    lat: float
    lon: float

    @validator("lon")
    def lon_is_max_180(cls, v):
        if abs(v) > 180:
            raise ValueError("invalid longitude")
        return v

    @validator("lat")
    def lat_is_max_90(cls, v):
        if abs(v) > 90:
            raise ValueError("invalid latitude")
        return v

    def as_tuple(self) -> Tuple[float, float]:
        return self.lat, self.lon


class IataCode(ConstrainedStr):
    min_length = 3
    max_length = 3
    regex = re.compile(r"^[a-zA-Z-0-9]+$")
    strict = True

    @classmethod
    def __get_validators__(cls):
        yield from super().__get_validators__()
        yield to_upper


class Airport(BaseModel):
    name: str
    code: IataCode
    country: IsoCountry
    position: Coordinate


class Flight(ConstrainedList):
    item_type = Airport
    min_items = 2
    max_items = 2


# Output model


class ClassifiedFlight(BaseModel):
    departure: IataCode
    departure_country: IsoCountry
    arrival: IataCode
    arrival_country: IsoCountry
    distance: PositiveInt  # in kilometres
    type: Optional[FlightType] = None

    @validator("type", pre=True, always=True)
    def set_type(cls, v, *, values, **kwargs):
        attr_distance = values["distance"]
        if attr_distance <= MAX_SHORT_FLIGHT:
            return FlightType.SHORT
        if attr_distance <= MAX_MIDDLE_FLIGHT:
            return FlightType.MIDDLE
        return FlightType.LONG

    @classmethod
    def from_flight(cls, flight: Flight, distance: PositiveInt) -> "ClassifiedFlight":
        departure = flight[0]
        arrival = flight[1]

        return cls(
            departure=departure.code,
            arrival=arrival.code,
            departure_country=departure.country,
            arrival_country=arrival.country,
            distance=distance,
        )


# Batch input/output models


class ReadAirport(BaseModel):
    iata: IataCode

    class Config:
        frozen = True


class ReadFlight(BaseModel):
    departure: ReadAirport
    arrival: ReadAirport

    class Config:
        frozen = True


class ReadFlights(BaseModel):
    __root__: List[ReadFlight]


class ClassifiedFlights(BaseModel):
    __root__: List[ClassifiedFlight]
