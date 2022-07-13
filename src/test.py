from .classify import load_airports, find_airport, get_flight_distance, classify_flight
from .models import FlightType, IataCode


def test():
    airports = load_airports()


    SFO = find_airport(airports, "sfo")  # San Francisco Intl.
    SYD = find_airport(airports, "syd")  # Sydney Kingsford Smith
    assert get_flight_distance(SFO, SYD) == 11936
    assert (
        classify_flight(airports, IataCode("SFO"), IataCode("syD")).type
        == FlightType.LONG
    )

    FKB = find_airport(airports, "fkb")  # Baden-Baden
    ABC = find_airport(airports, "abc")  # Albacete
    assert get_flight_distance(FKB, ABC) == 1351
    assert (
        classify_flight(airports, IataCode("FKB"), IataCode("ABC")).type
        == FlightType.SHORT
    )
