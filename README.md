# covid-forecast-palestine
COVID-19 emergency support to Palestine Red Cross

# covid_scraper_palestine.py
This script includes the function get_data() that scrapes the covid data in the main table of the website https://www.corona.ps/details .
The table consists on covid data:
Governorate|Number of cases|Cases Today|Active cases|recovery cases|Deaths|
The function get_data() returns a dataframe with the above-mentioned structure. 
Besides returning a dataframe it also generates a file named 'COVID_ps_%timestamp.csv'  which is 
saved in the same folder containting this file. The %timestamp correspond to the actual date.
    

