import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from streamlit_dynamic_filters import DynamicFilters
from google.oauth2.service_account import Credentials
import pandas as pd
import gspread
import cv2
import time
from pyzbar.pyzbar import decode
from oauth2client.service_account import ServiceAccountCredentials


st.title("Pragathi Batteries Management")

def total_inward():
    scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
    ]

    credentials = Credentials.from_service_account_file('creds.json',
        scopes=scopes
    )

    gc = gspread.authorize(credentials)
    existing_data = gc.open("batterydata").sheet1.get_all_records()
    df = pd.DataFrame(existing_data)
    # print((df=='59').sum().sum())
    dynamic_filters = DynamicFilters(df, filters=['Timestamp', 'Barcode', 'Type'])
    with st.sidebar:
        dynamic_filters.display_filters()
    dynamic_filters.display_df()
    # return df

def total_outward():
    scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
    ]

    credentials = Credentials.from_service_account_file('creds.json',
        scopes=scopes
    )

    gc = gspread.authorize(credentials)
    existing_data = gc.open("batterydata").worksheet("outwards").get_all_records()
    # print(existing_data.worksheets())
    df = pd.DataFrame(existing_data)
    dynamic_filters = DynamicFilters(df, filters=['Date', 'barcode', 'Customer','Part No','quantity','Bill Value'])
    with st.sidebar:
        dynamic_filters.display_filters()
    dynamic_filters.display_df()


def current_stock():
    scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
    ]

    credentials = Credentials.from_service_account_file('creds.json',
        scopes=scopes
    )

    gc = gspread.authorize(credentials)
    existing_data = gc.open("batterydata").worksheet("Total Received")
    dataframe = pd.DataFrame(existing_data.get_all_records())
    new_out=pd.DataFrame(gc.open("batterydata").worksheet("outwards").get_all_records())
    new_out=new_out['barcode']
    for x in new_out:
        if str(x) in str(dataframe):
            dataframe.drop(dataframe[dataframe['Barcode']==x].index,inplace=True)
            print("data is removed from total inward",x)
        else:
            print("Data not in Inwards, please update it")
    worksheet=gc.open("batterydata").worksheet("current stock")
    worksheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())
    # print(dataframe)
    dynamic_filters = DynamicFilters(dataframe, filters=['Timestamp', 'Barcode', 'Type'])
    with st.sidebar:
        dynamic_filters.display_filters()
    dynamic_filters.display_df()



a=st.selectbox("What do you want to check?",("Total Inward","Total Outward","Current Stock"))
if a =="Total Inward":
    total_inward()
elif a=="Total Outward":
    total_outward()
else:
    current_stock()
