# EU membership across time

**Short decription**: Using Python to transform a list of current/former EU member states with their accession (and exit) dates into time series.

## Purpose

This script takes a list of all EU countries with their accession dates and converts it to a time series where it's possible to see for each day, month and year whether a specific country was a member state or not. This information can then be used for e.g. calculating aggregates for the GDP, population, etc. of the EU as a whole that are based on historically accurate information.

## Input data and method

* The input is a dataset based on [this website]() and sligthly adjusted by adding an exit date for the United Kingdom.
* A daily dataset is created that covers the period between the EU's foundation back in the 1950's and the end of the current calendar year
* For each member state, we mark the calendar days on which it has been a part of the EU
* We calculate aggregate metrics at the monthly and annual level, showing the number of days and the % of the month/year that the country has been an EU member for

## Output data

Three output datasets are created with the following aggregation level: daily, monthly and annual. All of these are exported to the current working directory and are stored in the `parquet` format.
