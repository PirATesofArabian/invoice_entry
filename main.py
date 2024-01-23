import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from pyzbar.pyzbar import decode
import streamlit as st
import time
import cv2

def scan_barcode():
    cap = cv2.VideoCapture(0)
    barcode_scanner = cv2.QRCodeDetector()
    used_codes = []

    while True:
        success, frame = cap.read()
        for code in decode(frame):
            if code.data.decode('utf-8') not in used_codes:
                st.success('Approved. You can enter!')
                data = code.data.decode('utf-8')
                barcode_data = {'Barcode': data}
                st.write(barcode_data)
                used_codes.append(code.data.decode('utf-8'))
                time.sleep(5)
            elif code.data.decode('utf-8') in used_codes:
                st.warning('Sorry, this code has already been used')
                time.sleep(5)

        cv2.imshow('Testing-code-scan', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def get_existing_data_from_sheets():
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    credentials = Credentials.from_service_account_file('creds.json',
                                                        scopes=scopes
                                                        )

    gc = gspread.authorize(credentials)
    existing_data = gc.open("batterydata").sheet1.get_all_values()
    df = pd.DataFrame(existing_data)
    return df

def is_barcode_exists(barcode, dataframe):
    return barcode in dataframe[1].values

def add_data_to_sheets(data):
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    credentials = Credentials.from_service_account_file('creds.json',
                                                        scopes=scopes
                                                        )

    gc = gspread.authorize(credentials)
    sheet = gc.open("batterydata").sheet1

    new_row = [pd.Timestamp.now().strftime("%d-%m-%Y %H:%M:%S"), data['Barcode']]
    sheet.append_row(new_row)

def process_data(data, dataframe):
    if is_barcode_exists(data['Barcode'], dataframe):
        st.warning("Barcode already exists.")
    else:
        dataframe = dataframe.append(data, ignore_index=True)
        add_data_to_sheets(data)
        st.success("Data added to Google Sheets and DataFrame.")

def main():
    st.title("Barcode Scanner App")
    st.write("Click the button below to scan a barcode.")
    if st.button("Scan Barcode"):
        existing_data = get_existing_data_from_sheets()
        barcode_data = scan_barcode()
        process_data(barcode_data, existing_data)

if __name__ == '__main__':
    main()
