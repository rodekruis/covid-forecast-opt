# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 16:17:09 2021

@author: pphung
"""

from __future__ import print_function
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
# from google_trans_new import google_translator
from googletrans import Translator
import datetime
today = datetime.date.today()
last_week = today - datetime.timedelta(days=7)
next_week = today + datetime.timedelta(days=7)
import urllib.request
#from apiclient import discovery
#from google.oauth2 import service_account
import glob
from matplotlib import pyplot as plt


def multiply_round(df, new_col, col, factor):
    df[new_col] = df[col] * factor
    df[new_col] = df[new_col].astype(int)


## get_data returns a dataframe df with the data shown
# in the main table of 'https://www.corona.ps/details'.
# It also translates the text in the table from arabic to english.
# Besides returning df it also generates a file named
# 'COVID_ps_%timestamp.csv' in the same folder containting this file.,
# The timestamp correspond to the actual date.

#Website with data
# URL_or = 'https://www.corona.ps/details'
URL_or = 'https://www.corona.ps/'

#Magic
page = requests.get(URL_or)
soup = BeautifulSoup(page.content, 'html.parser')

#Find tables in webpage
tables = soup.find_all("table")

if not tables:
    # os.chdir("data")
    file_list = glob.glob("data/COVID_ps_*.csv")
    table = max(file_list, key=os.path.getctime)
    df_ps = pd.read_csv(table)
else:
    #tables[4] has the necessary data
    table = tables[4]
    tab_data = [[cell.text for cell in row.find_all(["th","td"])]
                    for row in table.find_all("tr")]
    #generate dataframe
    df = pd.DataFrame(tab_data)
    
    # init the Google API translator
    translator = Translator()
    # translator = google_translator()
    
    #translate the first row with titles
    for i in range(0, df.shape[1]):
        translation =  translator.translate(df[i][0], dest="en")
        df[i][0] = translation.text
    #now translate the 0th column (with governorates)
    for i in range(1, df.shape[0]):
        translation =  translator.translate(df[0][i], dest="en")
        df[0][i] = translation.text
    
    #Header 
    df.loc[0] = df.loc[0].str.strip()
    df_ps = df.rename(columns=df.iloc[0]).drop(df.index[0])
    
    # Returns a datetime object containing the local date and time
    # dateTimeObj = datetime.now()
    dateTimeObj = today
    timestampStr = dateTimeObj.strftime("%d-%b-%Y")
    name_df = 'COVID_ps_'+ timestampStr + '.csv'
    # print('Dataframe generated\nSaved in '+ name_df)
    
    df_ps.to_csv('data/' + name_df)



## initialize google sheets API
#scopes = ['https://www.googleapis.com/auth/drive',
#        'https://www.googleapis.com/auth/drive.file',
#        'https://www.googleapis.com/auth/spreadsheets']
#credentials = service_account.Credentials.from_service_account_file('service_account_key.json', scopes=scopes)
#service = discovery.build('sheets', 'v4', credentials=credentials)
#service_drive = discovery.build('drive', 'v3', credentials=credentials)

# get latest forecast data
urllib.request.urlretrieve("https://raw.githubusercontent.com/mrc-ide/global-lmic-reports/master/PSE/projections.csv", \
                        "data/forecast_latest.csv")
# https://github.com/mrc-ide/global-lmic-reports/blob/master/PSE/projections.csv
df = pd.read_csv('data/forecast_latest.csv')
df['date'] = pd.to_datetime(df['date'])

# calculate future cases (in the next 7 days)
df_new_cases = df[(df['scenario'] == 'Surged Maintain Status Quo') & (df['compartment'] == 'infections')]
df_new_cases = df_new_cases[['date', 'y_25', 'y_median', 'y_75']]
df_new_cases = df_new_cases[(df_new_cases['date'] > pd.to_datetime(last_week)) & (df_new_cases['date'] <= pd.to_datetime(next_week))].reset_index()

# calculate future ICU incidence (in the next 7 days)
df_icu_inci = df[(df['scenario'] == 'Surged Maintain Status Quo') & (df['compartment'] == 'ICU_incidence')]
df_icu_inci = df_icu_inci[['date', 'y_25', 'y_median', 'y_75']]
df_icu_inci = df_icu_inci[(df_icu_inci['date'] > pd.to_datetime(last_week)) & (df_icu_inci['date'] <= pd.to_datetime(next_week))]

# calculate proportion of new cases (in the last 7 days) per district
df_ps.iloc[:,2] = df_ps.iloc[:,2].astype(str).apply(lambda x: x.replace(',','')).astype(int) # 3th column contains new cases in the last 7 days, per district
df_ps.iloc[:,1] = df_ps.iloc[:,1].astype(str).apply(lambda x: x.replace(',','')).astype(int) # 2th column contains all time total cases, per district

# Gaza breakdown
total_new_cases = df_ps.iloc[:,2].sum()
df_gaza = pd.DataFrame(columns=df_ps.columns)
df_gaza.iloc[:,0] = ['Jabalia', 'Gaza City', 'Der Albalah', 'Khan Younis', 'Rafah']
gaza_cases = [9237, 21101, 5564, 8399, 4611]
gaza_ratios = [cases/48912 for cases in gaza_cases]          # figures from Jan 20, 2021

if total_new_cases != 0: 
    gaza_today = df_ps[df_ps['Governorate'].str.contains("Gaza")].iloc[0,2]
    df_gaza.iloc[:,2] = [gaza_today*i for i in gaza_ratios]  
    df_ps = df_ps.append(df_gaza)
    df_ps = df_ps[~df_ps['Governorate'].isin(["Gaza strip"])]
    df_ps['proportion_new_cases'] = df_ps.iloc[:,2] / total_new_cases
else:    
    gaza_today = df_ps[df_ps['Governorate'].str.contains("Gaza")].iloc[0,1]
    df_gaza.iloc[:,1] = [gaza_today*i for i in gaza_ratios]  
    df_ps = df_ps.append(df_gaza)
    df_ps = df_ps[~df_ps['Governorate'].isin(["Gaza strip"])]

    total_new_cases = df_ps.iloc[:,1].sum()
    df_ps['proportion_new_cases'] = df_ps.iloc[:,1] / total_new_cases

df_ps_week = pd.DataFrame()

for i in range(len(df_new_cases)):
    df_ps_date = df_ps
    # calculate future cases and hosp. per district based on the proportion of new cases per district
    # multiply_round(df, 'new_hosp_min', 'proportion_new_cases', df_new_hosp['y_25'])
    # multiply_round(df, 'new_hosp_mean', 'proportion_new_cases', df_new_hosp['y_median'])
    # multiply_round(df, 'new_hosp_max', 'proportion_new_cases', df_new_hosp['y_75'])
    multiply_round(df_ps_date, 'new_cases_min', 'proportion_new_cases', df_new_cases.loc[i,'y_25'])
    multiply_round(df_ps_date, 'new_cases_mean', 'proportion_new_cases', df_new_cases.loc[i,'y_median'])
    multiply_round(df_ps_date, 'new_cases_max', 'proportion_new_cases', df_new_cases.loc[i,'y_75'])
    df_ps_date["date"] = df_new_cases.loc[i,'date'] 
    
    df_ps_week = df_ps_week.append(df_ps_date)
    


fig1, ax1 = plt.subplots(figsize=(20, 10), dpi=300)
ax1.plot(df_icu_inci['date'], df_icu_inci['y_median'], color="crimson", label=i)
ax1.fill_between(df_icu_inci['date'],
        df_icu_inci['y_25'],
        df_icu_inci['y_75'], color="crimson", alpha=0.35)
ax1.axvline(today, linestyle='dashed', label="Today", color="k")
ax1.set(title="ICU incidence forecast", xlabel="Date", ylabel="New cases")
ax1.set_ylim(bottom=0)
ax1.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left')
ax1.grid()
# fig1.savefig('output/' + str(today)+'_ICU_forecast.png', format='png')

for i, m in df_ps_week.groupby('Governorate'):
    fig, ax = plt.subplots(figsize=(15, 7))
    ax.plot(m['date'], m['new_cases_mean'], label=i)
    ax.fill_between(m['date'],
            m['new_cases_min'],
            m['new_cases_max'], alpha=0.35)
    # print(i, m)
    # for j in range(len(m)):
    #     print(m.loc[j,'date'], m.loc[j,'new_cases_mean'])
    #     ax.text(m.loc[j,'date'], m.loc[j,'new_cases_mean']+0.1, "%d" %m.loc[j,'new_cases_mean'])
    ax.axvline(today, linestyle='dashed', label="Today", color="k")
    ax.set(title="COVID cases forecast "+ str(i), xlabel="Date", ylabel="New cases")
    ax.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left')
    # ax.set_yscale('log')
    ax.grid()
    # fig.savefig('output/' + str(today) + str(i) + '_covid_forecast.png', dpi=300, format='png')

# folder_metadata = {
#     'name': 'Palestine COVID forecast',
#     'mimeType': 'application/vnd.google-apps.folder'
# }
# folder = service_drive.files().create(body=folder_metadata,
#                                     fields='id').execute()
# permission1 = {
#         'type': 'user',
#         'role': 'writer',
#         'emailAddress': 'info@510.global',
# }
# folderId = folder.get('id')
# service_drive.permissions().create(fileId=folderId, body=permission1).execute()
# print(folderId)

# the_file_to_upload = str(i)+'covid_forecast.png'
# metadata = {'name': the_file_to_upload,
#             'parents': [folderId]}
# media = MediaFileUpload(the_file_to_upload,
#                         mimetype='image/png',
#                         resumable=True)
# request = service_drive.files().create(body=metadata, media_body=media, 
#                                        supportsAllDrives=True, fields='id').execute()
# fileId = request.get('id')


df_ps_week['date'] = df_ps_week['date'].dt.strftime('%Y%m%d')

df_to_export = df_ps_week[['Governorate', 'date', 'new_cases_min', 'new_cases_mean', 'new_cases_max']].reset_index(drop=True)
# df_to_export.to_csv('output/' + str(today) + '_covid_forecast.csv')
df_icu_inci = df_icu_inci.rename(columns={'y_25' : 'icu_indicent_min', 'y_median': 'icu_indicent_mean', 'y_75': 'icu_indicent_max'}).reset_index(drop=True)
# df_icu_inci.to_csv('output/' + str(today) + '_ICUincident_forecast.csv')

## reformat data and push to google sheets
#data_to_upload = [['Governorate', 'Date', 'New Cases (min)', 'New Cases (mean)', 'New Cases (max)']] +\
#                df_ps_week[['Governorate ', 'date', 'new_cases_min', 'new_cases_mean', 'new_cases_max']].values.tolist()
#TargetSpreadsheetId = '17E5dC_v186JcthIFLFZCNWG_jlKhD73_tOF9R2_TlM4'
#TargetRangeName = 'Forecast!A:E'
#body = {
#"range": TargetRangeName,
#"values": data_to_upload
#}
#value_input_option = 'USER_ENTERED'
#result = service.spreadsheets().values().update(
#    spreadsheetId=TargetSpreadsheetId, range=TargetRangeName, valueInputOption=value_input_option, body=body).execute() 

