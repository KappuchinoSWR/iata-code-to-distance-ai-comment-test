Calculate flight distance (using Vincenty's formulae) and classify flight in short/middle/long (according to [this classification](https://soep-online.de/wp-content/uploads/2022/05/VO-EG-Nr.-2612004.pdf).

# Install

1. Clone or download repo
2. Cd into repo
3. `pip install .`
4. try it `flight-distance --help"


# Use

Usage: flight-distance COMMAND [ARGS]...

Commands:
  classify
  classify-batch
  test
  
E.g.: `flight-distance classify-batch in.json out.json`

This expects *in.json* having at least this structure and these properties:

```
  [
    "departure": {
      "iata": "FRA"
      },
    "arrival": {
      "iata": "ABC"
  ]
```


*Out.json* will look like:

```
 [
    {
      "departure": "str",
      "arrival": "chq",
      "distance": 1906,
      "type": "middle" 
    },...
 ]
```

# data/airports.json

The data in `airports.json` is public domain. Nearly all airports came from [here](https://github.com/davidmegginson/ourairports-data).
This dataset doesn't cover all airports with IATA codes. According to IATA there are about 11k airports with IATA codes. *airports.json* has about 9.5k of them.
