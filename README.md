# SBB Journey Length Map
> Creates a map of SBB train/bus stations colorcoded by the time it takes to get there from a given origin.

[![python version][python-image]][python-url]
<!-- ([![Build Status][travis-image]][travis-url]) 
[![Downloads Stats][npm-downloads]][npm-url]-->

This program queries the SBB's API to gather information on journey times from a starting origin to the rest of the
country. Given an origin and starting time, a map is built showing how long it takes to get to each other station.

Click anywhere on the image to view the interactive map.
[![alt text](example_results/zurich_summer_saturday_0700.png)](https://jwpatt.github.io/SBB/)


SBB gives each user 1000 free API requests per day, but there are ~30,000 destinations in the network. 
By gathering info on the intermediate stations along a path, we devise an algorithm to determine which destinations are
end nodes on the network. Thus, we can gather information for most destinations with only 1000 queries.
Currently, this is but a python script to be run locally and the API calls are the current bottleneck, 
taking ~0.2 to 10 seconds each. 10 seconds is a long time, even when running in parallel. This requires investigation. 

The goal is to turn this into a web application where the server does the querying each day to build a database of 
common origins/starting times, e.g. Zurich at 7 AM on a Saturday (common among dayhikers).


Next improvements to be made:
1. ensure error handling is robust
4. add ability to make map based on arrival time (rather than duration)


Future directions for the project:
1. create a database for various stating cities/times
2. run continuously on a server, adding to the DB each day (via free API gets)
3. have script email me progress reports
4. develop web application to connect to this

<!--
![](header.png)

## Installation

OS X & Linux:

```sh
npm install my-crazy-module --save
```

Windows:

```sh
edit autoexec.bat
```

## Usage example

A few motivating and useful examples of how your product can be used. Spice this up with code blocks and potentially more screenshots.

_For more examples and usage, please refer to the [Wiki][wiki]._

## Development setup

Describe how to install all development dependencies and how to run an automated test-suite of some kind. Potentially do this for multiple platforms.

```sh
make install
npm test
```

## Release History

* 0.2.1
    * CHANGE: Update docs (module code remains unchanged)
* 0.2.0
    * CHANGE: Remove `setDefaultXYZ()`
    * ADD: Add `init()`
* 0.1.1
    * FIX: Crash when calling `baz()` (Thanks @GenerousContributorName!)
* 0.1.0
    * The first proper release
    * CHANGE: Rename `foo()` to `bar()`
* 0.0.1
    * Work in progress

## Meta

Your Name – [@YourTwitter](https://twitter.com/dbader_org) – YourEmail@example.com

Distributed under the XYZ license. See ``LICENSE`` for more information.

[https://github.com/yourname/github-link](https://github.com/dbader/)

## Contributing

1. Fork it (<https://github.com/yourname/yourproject/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request
-->
<!-- Markdown link & img dfn's -->
[python-image]: https://img.shields.io/badge/python-3.6-blue.svg
[python-url]: https://www.python.org/downloads/release/python-360/
[npm-downloads]: https://img.shields.io/npm/dm/datadog-metrics.svg?style=flat-square
[travis-image]: https://img.shields.io/travis/dbader/node-datadog-metrics/master.svg?style=flat-square
[travis-url]: https://travis-ci.org/dbader/node-datadog-metrics
[wiki]: https://github.com/yourname/yourproject/wiki
