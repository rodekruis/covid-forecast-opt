# covid-forecast-palestine
COVID-19 emergency support to Palestine Red Cross to forecast new COVID cases and new ICU incidence one week ahead.

# covid_process.py
This script includes 2 main functions:

**1. To get the latest data**

&nbsp;1.1 To scrape the covid data in the main table of the website https://www.corona.ps/.

&nbsp;&nbsp;The table consists on covid data:

&nbsp;&nbsp;Governorate|Number of cases|Cases Today|Active cases|recovery cases|Deaths|

&nbsp;&nbsp;The function returns a dataframe with the above-mentioned structure. Besides returning a dataframe it also generates a file named 'COVID_ps_%timestamp.csv' which is saved in the same folder containting this file. The %timestamp correspond to the actual date.
    
&nbsp;1.2 Download the latest forecast data by Centre for Global Infectious Disease Analysis, Imperial College London

**2. To project the COVID incidence**


**Outputs**

The outputs of this forecast is saved as png and csv, including:
- figures of new COVID cases per governorate
- figures of new ICU incidence of the state
- csv files for new COVID cases and new ICU incidence
