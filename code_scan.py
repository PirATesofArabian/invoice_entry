import cv2
from pyzbar.pyzbar import decode
import time
import pandas as pd
# import streamlit as st


cap = cv2.VideoCapture (0)
cap.set (3, 640) #3 Width
cap. set (4, 480) #4 Height
used_codes = []
df=pd.DataFrame(columns=['Barcode','IN/OUT'])
print(df)
camera = True
# button=st.button(label="Click to enter the data")
while camera == True:
    success, frame = cap.read()
    for code in decode (frame):
        if code.data.decode('utf-8') not in used_codes:
            print('Approved. You can enter!')
            print (code.data.decode ('utf-8'))
            used_codes.append (code.data.decode ('utf-8'))
            time.sleep (5)
        elif code.data.decode('utf-8') in used_codes:
            print ('Sorry, this code has been already used!')
            time.sleep (5)
        else:
            pass
    df["Barcode"]=used_codes
    print(df)
    cv2.imshow ('Testing-code-scan', frame)
    cv2.waitKey (1)
    cv2.destroyAllWindows()