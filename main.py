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

# JSON-Optionen für die Serialisierung festlegen
# pydantic_encoder wird als Default-Funktion verwendet, um Pydantic-Modelle zu serialisieren
# ensure_ascii=False erlaubt nicht-ASCII-Zeichen in der Ausgabe
JSON_OPTS = dict(default=pydantic_encoder, ensure_ascii=False)

# Logger konfigurieren
logger = logging.getLogger(name="main")
# Formatter definiert das Format der Log-Nachrichten
# Hier: Datum | Uhrzeit | Log-Level | Nachricht
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s", "%d.%m.%Y %H:%M:%S"
)
# Handler für das Schreiben der Logs in eine Datei
file_handler = logging.FileHandler("logs.log")
file_handler.setLevel(logging.DEBUG)  # Alle Log-Level ab DEBUG werden in die Datei geschrieben
file_handler.setFormatter(formatter)
# Handler für die Ausgabe kritischer Fehler auf der Konsole
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.CRITICAL)  # Nur kritische Fehler werden auf der Konsole ausgegeben

# Handler dem Logger hinzufügen
logger.addHandler(file_handler)
logger.addHandler(stdout_handler)

# Typer-App erstellen
# Typer ist eine Bibliothek zur Erstellung von CLI-Anwendungen
app = typer.Typer()


@app.command()
def schemas():
    """
    Zeigt die JSON-Schemas der verwendeten Modelle an
    """
    print("Output-Schema (für `classify`) \n\n", ClassifiedFlight.schema_json(indent=2))
    print(
        "\n\nOutput-Schema (für `classify-batch`) \n\n",
        ClassifiedFlights.schema_json(indent=2),
    )
    print("\n\nInput-Schema \n\n", ReadFlights.schema_json(indent=2))


@app.command()
def classify(
    departure_iata: str,  # IATA-Code des Abflugflughafens
    arrival_iata: str,    # IATA-Code des Ankunftsflughafens
    write_to: Optional[Path] = typer.Argument(None, help="Ausgabe in Datei schreiben"),
):
    """
    Klassifiziert einen einzelnen Flug
    """
    # Prüfen, ob Abflug- und Ankunftsflughafen identisch sind
    if departure_iata == arrival_iata:
        logger.log(
            msg="Flug von und zu demselben Flughafen kann nicht klassifiziert werden",
            level=logging.CRITICAL,
        )
        raise typer.Exit(code=1)

    # Flughäfen laden
    airports = load_airports()

    try:
        # IATA-Codes validieren und in IataCode-Objekte umwandeln
        departure_code = parse_obj_as(IataCode, departure_iata)
        arrival_code = parse_obj_as(IataCode, arrival_iata)
    except ValidationError as e:
        logger.log(
            msg="Mindestens ein Code ist kein gültiger IATA-Code (siehe Log)",
            level=logging.CRITICAL,
        )
        logger.exception(e)

        raise typer.Exit(code=1)

    try:
        # Flug klassifizieren
        flight = classify_flight(airports, departure_code, arrival_code)

        # Ergebnis in Datei schreiben, wenn gewünscht
        if write_to is not None:
            with open(write_to, "w") as f:
                json.dump(flight, f, **JSON_OPTS)
            raise typer.Exit()
        # Ansonsten Ergebnis auf der Konsole ausgeben
        print(flight.json())
    except AirportNotFoundError as e:
        logger.log(
            msg="Mindestens ein Flughafen nicht gefunden (siehe Log)", level=logging.CRITICAL
        )
        logger.exception(e)


@app.command()
def classify_batch(
    read_from: Path,  # Datei mit Eingabedaten
    write_to: Optional[Path] = typer.Argument(None, help="Ausgabe in Datei schreiben"),
):
    """
    Klassifiziert mehrere Flüge

    Doppelte Flüge in `read_from` werden ignoriert.
    """

    # Flughäfen laden
    airports = load_airports()

    # Eingabedaten aus Datei lesen
    with open(read_from, "r") as f:
        read_data = json.load(f)

    flights = list()

    try:
        # Eingabedaten validieren und in ReadFlight-Objekte umwandeln
        # Flüge von und zu demselben Flughafen werden ignoriert
        read_flights = {
            ReadFlight(**flight)
            for flight in read_data
            if flight["departure"]["iata"] != flight["arrival"]["iata"]
        }
    except (KeyError, ValidationError) as e:
        logger.log(
            msg="Fehlerhafte Eingabedaten (siehe Log)",
            level=logging.CRITICAL,
        )
        logger.exception(e)
        raise typer.Exit(code=1)

    # Jeden Flug klassifizieren
    for read_flight in read_flights:
        msg = f"Versuche {read_flight.departure.iata}-{read_flight.arrival.iata}"
        logger.log(msg=msg, level=logging.INFO)
        try:
            flight = classify_flight(
                airports, read_flight.departure.iata, read_flight.arrival.iata
            )
            flights.append(flight)
        except AirportNotFoundError as e:
            logger.log(
                msg="Flughafen nicht gefunden",
                level=logging.ERROR,
            )
            logger.exception(e)

    # Ergebnisse in Datei schreiben, wenn gewünscht
    if write_to is not None:
        with open(write_to, "w") as f:
            json.dump(flights, f, **JSON_OPTS)
        raise typer.Exit()
    # Ansonsten Ergebnisse auf der Konsole ausgeben
    print(json.dumps(flights, **JSON_OPTS))


if __name__ == "__main__":
    app()
