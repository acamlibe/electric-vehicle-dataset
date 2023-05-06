# Electric Vehicle Ownership in Washington State

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://acamlibe-electric-vehicle-dataset-app-91mkz8.streamlit.app/)

## Introduction
This Streamlit dashboard enables users to view and analyze electric vehicle ownership in the state of washington.

Electric vehicles can be split up into two broad categories:
- Battery Electric Vehicles (BEV) - e.g., Tesla Model X
- Plug-in Hybrid Electric Vehicle (PHEV) - e.g., Toyota Prius Prime

EV ownership has increased over the years as citizens of Washington are reluctant to pay for high gas prices. Washington state ranks 4th in the nation for highest gas prices.

Find national gas prices here: https://gasprices.aaa.com/state-gas-price-averages/

Along with high gas prices, the State of Washington passed, in 2019, a bill to determine eligibility for the **Clean Alternative Fuel Eligibility (CAFV)** status. This bill protects consumers and provides benefits for EV vehicles that are eligible. 

CAFV Bill Details: https://app.leg.wa.gov/rcw/default.aspx?cite=82.08.9999

## Data Sources
The data used in this app is found in three CSV files.
1. Electric Vehicle Population Dataset (https://data.wa.gov/Transportation/Electric-Vehicle-Population-Data/f6w7-q2d2)
2. Electric Vehicle Size History Dataset (https://data.wa.gov/Transportation/Electric-Vehicle-Population-Size-History/d886-d5q2/data)
3. Washington State All Grades Conventional Retail Gasoline Prices (https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=pet&s=emm_epm0u_pte_swa_dpg&f=m)

## Data Preparation
- Date conversions
- Converted from geocoded POINT variable to latitude and longitude columns
- NA values have been dropped for the Plotly.Express map display
- Electric ranges that have not been disclosed (0) were dropped for EV range analysis

## Use Case
It is important to note how, where, and why EV ownership is growing in the State of Washington. This can enable users such as government employees, dealerships, and EV manufacturers target specific cities/counties depending on EV ownership.

## App Features
- Analyze which cities and counties have the largest EV ownership, and which cities are lagging behind.
- View how range differs between various make and models of Battery Electric and Plug-In Hybrid vehicles.
- Analyze gas prices and EV ownership over time. View possible correlations between increasing gas prices and increasing EV ownership.
- Analyze which makes/models are eligible for the **CAFV** eligibility status.

## Future Work
This app can be extended to include additional states that show a similar pattern of EV ownership growth. As EVs grow more in popularity, we may see more citizens of different states make the switch from conventional ICE vehicles.

## Streamlit App
https://acamlibe-electric-vehicle-dataset-app-91mkz8.streamlit.app