import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Display Title and Description
st.title("Vendor Management Portal")

# Constants
VENDORS = [
    "JHADE AUTO SPARES",
    "DIAMOND AUTO PARTS",
    "VIKAS TRADE LINKS",
    "RK AUTO MOBILES",
    "MUBIES",
    "COOLAID",
    "KARUNA MOTORS",
    "WURTH",
    "HINDUSTAN PANTS",
    "AUTO SHEILD",
    "KHT TATA MOTORS",
    "SN BATTERY",
    "GEORGE OAKES LTD",
    "MARUTI POPULAR",
    "TOYOTA MOTOR WORLD",
    "KHT AGENCIES PVT LTD",
    "BOSCH BATTERY",
    "SUNDARAM MOTORS",
    "S&S VENTURE(FORD)",
    "INFINITY AUTO PARTS",
    "SRI BANDU",
    "RR AUTOMOBILES",
    "AUTOVERSE MOBILITY PUTO LIMITED"
]
PRODUCTS = [
    "Electronics",
    "Apparel",
    "Groceries",
    "Software",
    "Other",
]

# Establishing a Google Sheets connection
conn = st.experimental_connection("gsheets", type=GSheetsConnection)

# Fetch existing vendors data
existing_data = conn.read(worksheet="Sheet1", usecols=list(range(6)), ttl=5)
existing_data = existing_data.dropna(how="all")

action = st.selectbox(
    "Choose an Action",
    [
        "Enter invoice Entry",
        "Update Existing Vendor",
        "View All Vendors",
        "Delete Vendor",
    ],
)

if action == "Enter invoice Entry":
    st.markdown("Enter the details of the new vendor below.")
    with st.form(key="vendor_form"):
        invoice_number = st.text_input(label="InvoiceNumber")
        vendor_name = st.multiselect("Select the vendor",options=VENDORS)
       # products = st.multiselect("Products Offered", options=PRODUCTS)
        #Amount = st.slider("Years in Business", 0, 50, 5)
        invoice_date = st.date_input(label="invoice_date")
        Amount = st.number_input('Enter the Amount')
        additional_info = st.text_area(label="Additional Notes")

        st.markdown("**required*")
        submit_button = st.form_submit_button(label="Submit Vendor Details")

        if submit_button:
            if not invoice_number or not vendor_name:
                st.warning("Ensure all mandatory fields are filled.")
            elif existing_data["InvoiceNumber"].str.contains(invoice_number).any():
                st.warning("A vendor with this company name already exists.")
            else:
                vendor_data = pd.DataFrame(
                    [
                        {
                            "VendorName": vendor_name,
                            "InvoiceNumber": invoice_number,
                           # "Products": ", ".join(products),
                            "Amount": Amount,
                            "InvoiceDate": invoice_date.strftime("%Y-%m-%d"),
                            "AdditionalInfo": additional_info,
                        }
                    ]
                )
                updated_df = pd.concat([existing_data, vendor_data], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_df)
                st.success("Vendor details successfully submitted!")

elif action == "Update Existing Vendor":
    st.markdown("Select a vendor and update their details.")

    vendor_to_update = st.selectbox(
        "Select a Vendor to Update", options=existing_data["InvoiceNumber"].tolist()
    )
    vendor_data = existing_data[existing_data["InvoiceNumber"] == vendor_to_update].iloc[
        0
    ]

    with st.form(key="update_form"):
        invoice_number = st.text_input(
            label="Invoice Number*", value=vendor_data["InvoiceNumber"]
        )
        vendor_name = st.multiselect("Select the vendor",options=VENDORS)
        Amount= st.number_input("Enter the Amount",int(vendor_data["Amount"]))
        invoice_date = st.date_input(
            label="Invoice Date", value=pd.to_datetime(vendor_data["InvoiceDate"])
        )
        additional_info = st.text_area(
            label="Additional Notes", value=vendor_data["AdditionalInfo"]
        )

        st.markdown("**required*")
        update_button = st.form_submit_button(label="Update Vendor Details")

        if update_button:
            if not invoice_number or not vendor_name:
                st.warning("Ensure all mandatory fields are filled.")
            else:
                # Removing old entry
                existing_data.drop(
                    existing_data[
                        existing_data["InvoiceNumber"] == vendor_to_update
                    ].index,
                    inplace=True,
                )
                # Creating updated data entry
                updated_vendor_data = pd.DataFrame(
                    [
                        {
                            "InvoiceNumber": invoice_number,
                            "VendorName": vendor_name,
                           # "Products": ", ".join(products),
                            "Amount": Amount,
                            "InvoiceDate": invoice_date.strftime("%Y-%m-%d"),
                            "AdditionalInfo": additional_info,
                        }
                    ]
                )
                # Adding updated data to the dataframe
                updated_df = pd.concat(
                    [existing_data, updated_vendor_data], ignore_index=True
                )
                conn.update(worksheet="Sheet1", data=updated_df)
                st.success("Vendor details successfully updated!")

# View All Vendors
elif action == "View All Vendors":
    st.dataframe(existing_data)

# Delete Vendor
elif action == "Delete Vendor":
    vendor_to_delete = st.selectbox(
        "Select a Vendor to Delete", options=existing_data["InvoiceNumber"].tolist()
    )

    if st.button("Delete"):
        existing_data.drop(
            existing_data[existing_data["InvoiceNumber"] == vendor_to_delete].index,
            inplace=True,
        )
        conn.update(worksheet="Sheet1", data=existing_data)
        st.success("Vendor successfully deleted!")