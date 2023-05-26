"""
=========================
EU membership across time
=========================

This script takes a list of all EU countries with their
accession dates and converts it to a time series where
it's possible to see for each month and year whether a
specific country was a member state or not. This information
can then be used for e.g. calculating aggregates for
the GDP, population, etc. of the EU as a whole that are
based on historically accurate information.
"""

# %% Setting up

# Importing relevant packages
import pandas as pd
import numpy as np
import datetime as dt
import os

# Custom function to convert text to date that also
# allows for having NANs in the input data
def convert_text_to_date(text, format):
    try:
        converted_date = dt.datetime.strptime(text, format)
    except:
        converted_date = np.nan
    return converted_date


# %% Importing data

# Data originally from link below, with minor modifications by the author
# https://www.countries-ofthe-world.com/european-union-countries.html
InputData = pd.read_excel("EU_countries_with_accession_dates.xlsx", skiprows = 3)


# %% Creating daily historical data

# Converting string dates to actual dates
for col in ["EU accession date", "EU exit date"]:
    InputData[col] = InputData[col].apply(lambda x: convert_text_to_date(x, "%B %d, %Y"))

# Getting the earliest and latest date possible for being part of the EU
# Note: we limit the series until the end of the current year
EarliestDateForEU = np.min(InputData["EU accession date"])
EndOfYear = dt.date.today().year
LatestDateForEU = pd.to_datetime(str(EndOfYear) + "-12-31")

# For each country, we create accurate historical data
# where we have an entry for each day of the country's membership
OutputData = pd.DataFrame()
for country in InputData["Country"].unique():
    CountryData = InputData[InputData["Country"] == country].copy()
    AccessionDate = CountryData["EU accession date"].iloc[0]
    if CountryData["EU exit date"].isna().sum() > 0:
        ExitDate = LatestDateForEU
    else:
        ExitDate = CountryData["EU exit date"].iloc[0]
    DateRange = pd.date_range(start = EarliestDateForEU, end = LatestDateForEU, freq = "D").strftime("%Y-%m-%d")
    CountryData = pd.DataFrame({"Country":country, "Date":DateRange})
    CountryData["AccessionDate"] = AccessionDate
    CountryData["LatestDate"] = ExitDate
    CountryData["EU_Member"] = ((CountryData["Date"] >= CountryData["AccessionDate"]) & (CountryData["Date"] <= CountryData["LatestDate"]))
    CountryData.drop(columns = ["AccessionDate", "LatestDate"], inplace = True)
    OutputData = pd.concat([OutputData, CountryData])


# %% Creating monthly aggregate data

# Specifying columns of interest
VarsToAggBy = ["YearMonth", "Country"]
VarsToKeep = ["Country", "YearMonth", "DaysInMonth", \
              "MembershipInMonth_Days", "MembershipInMonth_Pct"]

# Denoting N of days and % of the month the country's been an EU member for
OutputData_Monthly = OutputData.copy()
OutputData_Monthly["Date"] = pd.to_datetime(OutputData_Monthly["Date"])
OutputData_Monthly["Month"] = OutputData_Monthly["Date"].dt.month.astype(str)
OutputData_Monthly["Month"] = np.where(OutputData_Monthly["Month"].str.len() == 1,
                                       "0" + OutputData_Monthly["Month"],
                                       OutputData_Monthly["Month"])
OutputData_Monthly["YearMonth"] = OutputData_Monthly["Date"].dt.year.astype(str) + "-" + OutputData_Monthly["Month"]
OutputData_Monthly["DaysInMonth"] = OutputData_Monthly.groupby("YearMonth")["Date"].transform("nunique")
OutputData_Monthly["MembershipInMonth_Days"] = OutputData_Monthly.groupby(VarsToAggBy)["EU_Member"].transform("sum")
OutputData_Monthly["MembershipInMonth_Pct"] = OutputData_Monthly["MembershipInMonth_Days"]/OutputData_Monthly["DaysInMonth"]
OutputData_Monthly.drop_duplicates(subset = VarsToAggBy, inplace = True)
OutputData_Monthly.reset_index(inplace = True, drop = True)
OutputData_Monthly = OutputData_Monthly[VarsToKeep].copy()


# %% Creating annual aggregate data

# Specifying columns of interest
VarsToAggBy = ["Year", "Country"]
VarsToKeep = ["Country", "Year", "DaysInYear", \
              "MembershipInYear_Days", "MembershipInYear_Pct"]

# Denoting N of days and % of the month the country's been an EU member for
OutputData_Annual = OutputData.copy()
OutputData_Annual["Date"] = pd.to_datetime(OutputData_Annual["Date"])
OutputData_Annual["Year"] = OutputData_Annual["Date"].dt.year.astype(str)
OutputData_Annual["DaysInYear"] = OutputData_Annual.groupby("Year")["Date"].transform("nunique")
OutputData_Annual["MembershipInYear_Days"] = OutputData_Annual.groupby(VarsToAggBy)["EU_Member"].transform("sum")
OutputData_Annual["MembershipInYear_Pct"] = OutputData_Annual["MembershipInYear_Days"]/OutputData_Annual["DaysInYear"]
OutputData_Annual.drop_duplicates(subset = VarsToAggBy, inplace = True)
OutputData_Annual.reset_index(inplace = True, drop = True)
OutputData_Annual = OutputData_Annual[VarsToKeep].copy()

# Exporting data
OutputData.to_parquet(os.getcwd() + "\EU_countries_series_daily.parquet")
OutputData_Monthly.to_parquet(os.getcwd() + "\EU_countries_series_monthly.parquet")
OutputData_Annual.to_parquet(os.getcwd() + "\EU_countries_series_annual.parquet")
