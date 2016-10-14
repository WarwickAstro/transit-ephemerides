Ephemeris2
----------

This is a slightly updated version of Neale Gibson's Ephemeris code

## Synopsis

This script works out the visible transits for a list of objects and observatories.

   1. Observatories are specified as per the observatories2 file
   1. Target's ephemrides are specified as per the targets/Planets file

There are several utility scripts also available in the ```utils/``` directory:

   1. whatsUpTonight.py - shows which objects are transiting tonight
   1. refineEphemeris.py - refines the period to match a given transit mid-point
   1. updateNGEphem.py - grabs updated planet parameters from ETD *needs updating*

## Code Example

To get the transit times for targets in ```NITES_2016.txt``` between 1st Dec 2016 and 31st Dec 2016 do:

```
python ephemeris2.py targets/NITES_2016.txt observatories2 2016-12-01 2016-12-31
```

where the observatory required is uncommented in the ```observatories2``` file. Target files are now stored in ```targets/``` directory as they can build up and clutter the parent folder.

## Motivation

To study planet transits you need to know when they are :)

## Installation

Clone this repo using:

```
git clone git@github.com:NITES-40cm/ephemeris2.git
```

## Contributors

Neale Gibson, James McCormac

## License

MIT License
