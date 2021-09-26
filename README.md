# SBB Time Map
> Creates a map of SBB train/bus stations colorcoded by travel time from a given city.

[![python version][python-image]][python-url]
<!-- ([![Build Status][travis-image]][travis-url]) 
[![Downloads Stats][npm-downloads]][npm-url]-->

This app plots public transport locations color coded by the time it takes to travel to them from some origin station.
It can plot the travel time for public transport (train, bus, cable car, etc.), travel time for driving by car, and can
show the difference between the two. 

The map is LIVE at sbb-time-map.herokuapp.com

Currently, the list of origin cities is static: the SBB's API and the [OSRM](https://github.com/Project-OSRM/osrm-backend)
together take too long to query and process - on the order of 5 to 15 minutes to gather the full dataset for a new
location. There are ways to speed this up, such as loading partial results that include the key destinations, but I am
turning my focus to cleaning the code and making it something I can share and be proud of (rather than the ugly yet 
functional form it is currently in).

I have enjoyed this project quite a bit, as it has forced me to learn how to do a few things:
- MongoDB (a NoSQL database)
- Python's multiprocessing library
- Asynchronous IO API queries (asyncio)
- Plotly and Dash (a stripped down version of Flask)

To make a proper project out of it, I now need to incorporate:
- Automatic unit testing
- Proper documentation and commenting
- Type hinting
- Docstrings
- Proper separation of concerns and class architecture

<!-- Markdown link & img dfn's -->
[python-image]: https://img.shields.io/badge/python-3.6-blue.svg
[python-url]: https://www.python.org/downloads/release/python-360/
[npm-downloads]: https://img.shields.io/npm/dm/datadog-metrics.svg?style=flat-square
[travis-image]: https://img.shields.io/travis/dbader/node-datadog-metrics/master.svg?style=flat-square
[travis-url]: https://travis-ci.org/dbader/node-datadog-metrics
[wiki]: https://github.com/yourname/yourproject/wiki
