# KPI dashboard

This demo dashboard provides an example of a Key Performance Indicator (KPI) dashboard, designed to help users get started and extend further.
It uses fictional budget data to demonstrate the capabilities of Vizro using real world applications.

Special thanks to the [#RWFD Real World Fake Data initiative](https://opendatainitiative.io/), a community project that
provides high-quality fake data for creating realistic dashboard examples for real-world applications.

Note: The data has been additionally edited for the purpose of this example.

<img src="./assets/images/kpi_dashboard.gif" alt="Gif to KPI dashboard">

## How to run the example locally

1. If you have `hatch` set up, run the example with the command `hatch run example kpi`. Otherwise, run the `app.py` file with your environment activated where `vizro` is installed.
2. You should now be able to access the app locally via http://127.0.0.1:8050/.

## Possible future iterations

- Enable selection of year filter
- Enable current year vs. past year comparison
- Enable dynamic KPI Cards
- Bar - Enable drill-downs from Issue to Sub-issue and Product to Sub-product
- Bar - Reformat numbers with commas in bar chart
- Bar - Left-align y-axis labels
- Bar - Shorten labels
- Line - Customize function to always show selected year vs. past year
- Table-view - Check why date format does not work on `Date Received`
- Table-view - Add icons to `On time?` column
- Table-view - Improve speed by applying cache or overcome limitation that entire data set is loaded in
