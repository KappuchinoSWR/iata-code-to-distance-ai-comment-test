# Note: This is an unofficial Fork for the code to tesk AI code commenting capabilites. Since this public code, the file(s) that are AI commented are public as well. 
# Caution: The code has not been checked for any changes, corrections, omissions, etc. etc. 


Calculate flight distance (using Vincenty's formulae) and classify flight in short/middle/long (according to [this classification](https://soep-online.de/wp-content/uploads/2022/05/VO-EG-Nr.-2612004.pdf)).

# Install

1. Clone or download repo
2. Cd into repo
3. `pip install .`
4. try it: `flight-distance classify FRA ABC`

# Use

## General

```
Usage: flight-distance [OPTIONS] COMMAND [ARGS]...

Options:
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.
  --help                Show this message and exit.

Commands:
  classify        Classify a single flight
  classify-batch  Classify a batch of flights
  schemas         Show json schema(s)
```

## `classify`

E.g. `flight-distance classify FRA ABC`

```
Usage: flight-distance classify [OPTIONS] DEPARTURE_IATA ARRIVAL_IATA [WRITE_TO]

  Classify a single flight

Arguments:
  DEPARTURE_IATA  [required]
  ARRIVAL_IATA    [required]
  [WRITE_TO]      Write output to PATH

Options:
  --help  Show this message and exit.
```

## `classify-batch`

E.g.: `flight-distance classify-batch in.json out.json`

```
Usage: flight-distance classify-batch [OPTIONS] READ_FROM [WRITE_TO]

  Classify a batch of flights

  Duplicate flights in `read_from` are ignored.

Arguments:
  READ_FROM   [required]
  [WRITE_TO]  Write output to PATH

Options:
  --help  Show this message and exit.
```

# Examples & schemas

Cf. `flight-distance schemas`

## Input (`classify-batch`)

### Example

```json
[
    {
        "arrival": {
            "iata": "STR"
        }
    },
    {
        "depature": {
            "iata": "CHQ"
        }
    }
]
```

### Schema

```json
{
    "title": "ReadFlights",
    "type": "array",
    "items": {
        "$ref": "#/definitions/ReadFlight"
    },
    "definitions": {
        "ReadAirport": {
            "title": "ReadAirport",
            "type": "object",
            "properties": {
                "iata": {
                    "title": "Iata",
                    "minLength": 3,
                    "maxLength": 3,
                    "pattern": "^[a-zA-Z-0-9]+$",
                    "type": "string"
                }
            },
            "required": ["iata"]
        },
        "ReadFlight": {
            "title": "ReadFlight",
            "type": "object",
            "properties": {
                "departure": {
                    "$ref": "#/definitions/ReadAirport"
                },
                "arrival": {
                    "$ref": "#/definitions/ReadAirport"
                }
            },
            "required": ["departure", "arrival"]
        }
    }
}
```

## Output (`classify`)

### Example

```json
{
    "departure": "FRA",
    "departure_country": "DE",
    "arrival": "ABC",
    "arrival_country": "ES",
    "distance": 1481,
    "type": "short"
}
```

### Schema

```json
{
    "title": "ClassifiedFlight",
    "type": "object",
    "properties": {
        "departure": {
            "title": "Departure",
            "minLength": 3,
            "maxLength": 3,
            "pattern": "^[a-zA-Z-0-9]+$",
            "type": "string"
        },
        "departure_country": {
            "title": "Departure Country",
            "minLength": 2,
            "maxLength": 2,
            "pattern": "^[a-zA-Z]+$",
            "type": "string"
        },
        "arrival": {
            "title": "Arrival",
            "minLength": 3,
            "maxLength": 3,
            "pattern": "^[a-zA-Z-0-9]+$",
            "type": "string"
        },
        "arrival_country": {
            "title": "Arrival Country",
            "minLength": 2,
            "maxLength": 2,
            "pattern": "^[a-zA-Z]+$",
            "type": "string"
        },
        "distance": {
            "title": "Distance",
            "exclusiveMinimum": 0,
            "type": "integer"
        },
        "type": {
            "$ref": "#/definitions/FlightType"
        }
    },
    "required": [
        "departure",
        "departure_country",
        "arrival",
        "arrival_country",
        "distance"
    ],
    "definitions": {
        "FlightType": {
            "title": "FlightType",
            "description": "An enumeration.",
            "enum": ["short", "middle", "long"],
            "type": "string"
        }
    }
}
```

## Output (`classify-batch`)

### Example

```json
[
    {
        "departure": "STR",
        "departure_country": "DE",
        "arrival": "CHQ",
        "arrival_country": "GR",
        "distance": 1906,
        "type": "middle"
    }
]
```

### Schema

```json
{
    "title": "ClassifiedFlights",
    "type": "array",
    "items": {
        "$ref": "#/definitions/ClassifiedFlight"
    },
    "definitions": {
        "FlightType": {
            "title": "FlightType",
            "description": "An enumeration.",
            "enum": ["short", "middle", "long"],
            "type": "string"
        },
        "ClassifiedFlight": {
            "title": "ClassifiedFlight",
            "type": "object",
            "properties": {
                "departure": {
                    "title": "Departure",
                    "minLength": 3,
                    "maxLength": 3,
                    "pattern": "^[a-zA-Z-0-9]+$",
                    "type": "string"
                },
                "departure_country": {
                    "title": "Departure Country",
                    "minLength": 2,
                    "maxLength": 2,
                    "pattern": "^[a-zA-Z]+$",
                    "type": "string"
                },
                "arrival": {
                    "title": "Arrival",
                    "minLength": 3,
                    "maxLength": 3,
                    "pattern": "^[a-zA-Z-0-9]+$",
                    "type": "string"
                },
                "arrival_country": {
                    "title": "Arrival Country",
                    "minLength": 2,
                    "maxLength": 2,
                    "pattern": "^[a-zA-Z]+$",
                    "type": "string"
                },
                "distance": {
                    "title": "Distance",
                    "exclusiveMinimum": 0,
                    "type": "integer"
                },
                "type": {
                    "$ref": "#/definitions/FlightType"
                }
            },
            "required": [
                "departure",
                "departure_country",
                "arrival",
                "arrival_country",
                "distance"
            ]
        }
    }
}
```

# data/airports.json

The data in `airports.json` is public domain. Nearly all airports came from [here](https://github.com/davidmegginson/ourairports-data).
This dataset doesn't cover all airports with IATA codes. According to IATA there are about 11k airports with IATA codes. _airports.json_ has about 9.5k of them.
