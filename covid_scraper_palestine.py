#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  COVID_scraper_ps.py
#  
#  Copyright 2020 Camilo Ulloa <camilo.ulloa.o[at]gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import \
    NoSuchElementException, TimeoutException, InvalidArgumentException, WebDriverException
from googletrans import Translator, constants
from datetime import datetime
import schedule
import time

def get_data():
    ## get_data returns a dataframe df with the data shown
    # in the main table of 'https://www.corona.ps/details'.
    # It also translates the text in the table from arabic to english.
    # Besides returning df it also generates a file named
    # 'COVID_ps_%timestamp.csv' in the same folder containting this file.,
    # The timestamp correspond to the actual date.
    
    
    
    #Website with data
    URL_or = 'https://www.corona.ps/details'
    
    #Magic
    page = requests.get(URL_or)
    soup = BeautifulSoup(page.content, 'html.parser')
    #Find tables in webpage
    tables = soup.find_all("table")
    # init the Google API translator
    translator = Translator()
    #tables[4] has the necessary data
    table = tables[4]
    tab_data = [[cell.text for cell in row.find_all(["th","td"])]
                        for row in table.find_all("tr")]
    #generate dataframe
    df = pd.DataFrame(tab_data)
    #translate the first row with titles
    for i in range(0, df.shape[1]):
        translation =  translator.translate(df[i][0], dest="en")
        df[i][0] = translation.text
    #now translate the 0th column (with governorates)
    for i in range(1, df.shape[0]):
        translation =  translator.translate(df[0][i], dest="en")
        df[0][i] = translation.text

    #Header 
    df = df.rename(columns=df.iloc[0]).drop(df.index[0])
    
    # Returns a datetime object containing the local date and time
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.date().strftime("%d-%b-%Y")
    name_df = 'COVID_ps_'+ timestampStr + '.csv'
    print('Dataframe generated\nSaved in '+ name_df)
    
    df.to_csv(name_df)
    
    return df

def main(args):
    schedule.every(24).hours.do(get_data)
    while True:
        schedule.run_pending()
        time.sleep(1)
    #get_data()
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
