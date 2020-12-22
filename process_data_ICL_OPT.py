# import necessary libraries
from __future__ import print_function
from datetime import datetime, timedelta
today = datetime.today()
next_week = today + timedelta(days=7)
import urllib.request
import pandas as pd
from apiclient import discovery
from google.oauth2 import service_account
from time import sleep
import traceback

import os
# os.chdir("c:/Users/BOttow/Documents/covid-forecast-lebanon/")

def multiply_round(df, new_col, col, factor):
    df[new_col] = df[col] * factor
    df[new_col] = df[new_col].astype(int)

# initialize google sheets API
scopes = ['https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/spreadsheets']
credentials = service_account.Credentials.from_service_account_file('service_account_key.json', scopes=scopes)
service = discovery.build('sheets', 'v4', credentials=credentials)

# get latest forecast data
urllib.request.urlretrieve("https://raw.githubusercontent.com/mrc-ide/global-lmic-reports/master/PSE/projections.csv", \
                           "data/forecast_latest.csv")
# https://github.com/mrc-ide/global-lmic-reports/blob/master/PSE/projections.csv
df = pd.read_csv('data/forecast_latest.csv')
df['date'] = pd.to_datetime(df['date'])

# calculate future cases (in the next 7 days)
df_new_cases = df[(df['scenario'] == 'Surged Maintain Status Quo') & (df['compartment'] == 'infections')]
df_new_cases = df_new_cases[['date', 'y_25', 'y_median', 'y_75']]
df_new_cases = df_new_cases[(df_new_cases['date'] > today) & (df_new_cases['date'] <= next_week)].sum()

# calculate future hospitalizations (in the next 7 days)
# df_new_hosp = df[(df['scenario'] == 'Surged Maintain Status Quo') & (df['compartment'] == 'hospital_incidence')]
# df_new_hosp = df_new_hosp[['date', 'y_25', 'y_median', 'y_75']]
# df_new_hosp = df_new_hosp[(df_new_hosp['date'] > today) & (df_new_hosp['date'] <= next_week)].sum()

# get latest data on cases and hospitalizations
# spreadsheetId = '1HZm2kQTodAC2Bz7l2Uw77RTGjtEOc5ywtrpzOF_oxtM'
# rangeName = 'Districts!A:K'
# result = service.spreadsheets().values().get(
#     spreadsheetId=spreadsheetId, range=rangeName).execute()
# values = result.get('values', [])
# df = pd.DataFrame.from_records(values)[1:] # convert to pandas dataframe
dateTimeObj = datetime.now()
timestampStr = dateTimeObj.date().strftime("%d-%b-%Y")
name_df = 'COVID_ps_'+ timestampStr + '.csv'
df = pd.read_csv('data/' + name_df)
# calculate proportion of new cases (in the last 7 days) per district
df.iloc[:,3] = df.iloc[:,3].astype(str).apply(lambda x: x.replace(',','')).astype(int) # 3th column contains new cases in the last 7 days, per district
total_new_cases = df.iloc[:,3].sum()
df['proportion_new_cases'] = df.iloc[:,3] / total_new_cases

# calculate future cases and hosp. per district based on the proportion of new cases per district
# multiply_round(df, 'new_hosp_min', 'proportion_new_cases', df_new_hosp['y_25'])
# multiply_round(df, 'new_hosp_mean', 'proportion_new_cases', df_new_hosp['y_median'])
# multiply_round(df, 'new_hosp_max', 'proportion_new_cases', df_new_hosp['y_75'])
multiply_round(df, 'new_cases_min', 'proportion_new_cases', df_new_cases['y_25'])
multiply_round(df, 'new_cases_mean', 'proportion_new_cases', df_new_cases['y_median'])
multiply_round(df, 'new_cases_max', 'proportion_new_cases', df_new_cases['y_75'])

# reformat data and push to google sheets
data_to_upload = [['New Cases (min)', 'New Cases (mean)', 'New Cases (max)']] +\
                 df[['new_cases_min', 'new_cases_mean', 'new_cases_max']].values.tolist()
TargetSpreadsheetId = '17E5dC_v186JcthIFLFZCNWG_jlKhD73_tOF9R2_TlM4'
TargetRangeName = 'Forecast!B:D'
body = {
  "range": TargetRangeName,
  "values": data_to_upload
}
value_input_option = 'USER_ENTERED'
result = service.spreadsheets().values().update(
    spreadsheetId=TargetSpreadsheetId, range=TargetRangeName, valueInputOption=value_input_option, body=body).execute()



