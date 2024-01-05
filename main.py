import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from streamlit_dynamic_filters import DynamicFilters

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
        vendor_name = st.selectbox("Select the vendor",options=VENDORS)
       # products = st.multiselect("Products Offered", options=PRODUCTS)
        #Amount = st.slider("Years in Business", 0, 50, 5)
        invoice_date = st.date_input(label="invoice_date")
        Amount = st.number_input('Enter the Amount')
        # AmountPaid=st.text_input("")
        AmountPaid= st.number_input("Enter amount paid")
        additional_info = st.text_area(label="Additional Notes")

        st.markdown("**required*")
        submit_button = st.form_submit_button(label="Submit Vendor Details")

        if submit_button:
            if not invoice_number or not vendor_name:
                st.warning("Ensure all mandatory fields are filled.")
            elif existing_data["VendorName"].str.contains(vendor_name).any() and existing_data["InvoiceNumber"].astype(str).str.contains(invoice_number).any():
                st.warning("A vendor with this invoice number already exists.")
            else:
                vendor_data = pd.DataFrame(
                    [
                        {
                            "VendorName": vendor_name,
                            "InvoiceNumber": invoice_number,
                           # "Products": ", ".join(products),
                            "Amount": Amount,
                            "InvoiceDate": invoice_date.strftime("%Y-%m-%d"),
                            "AmountPaid": AmountPaid,
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
        vendor_name = st.selectbox("Select the vendor",options=VENDORS)
        Amount= st.number_input("Enter the Amount",int(vendor_data["Amount"]))
        invoice_date = st.date_input(
            label="Invoice Date", value=pd.to_datetime(vendor_data["InvoiceDate"])
            
        )
        AmountPaid= st.number_input("Enter amount paid")
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
                            "AmountPaid": AmountPaid,
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
    df=pd.DataFrame(existing_data)
    filters=["InvoiceNumber","VendorName","Amount","InvoiceDate","AmountPaid"]
    dynamic_filters = DynamicFilters(df,filters=["InvoiceNumber","VendorName","Amount","InvoiceDate","AmountPaid"])
    vendor_name = st.selectbox(
        "Select a Vendor to filter", options=set(existing_data["VendorName"].tolist())
    )
    vendor_data = existing_data[existing_data["VendorName"] == vendor_name].iloc[
        0
    ]
    invoice_date = st.date_input(
            label="Invoice Date", value=pd.to_datetime(vendor_data["InvoiceDate"]))
    checkbox=st.checkbox(label="Tick if you want to search by both vendor name and date")

    # vendor_name = st.selectbox("Select the vendor",options=VENDORS)
    # dynamic_filters.display_df()
    
    full_data=st.checkbox(label="Tick if you want to see data for all vendors")
    if full_data:
        Total_Amount=df["Amount"].sum()
        Total_paid=df["AmountPaid"].sum()
        Balance_Amount=round(Total_Amount-Total_paid)
        st.write(df)
    else:
        if not checkbox:
            filter_df=df[(df['VendorName']==f"{vendor_name}")]
            Total_Amount=filter_df["Amount"].sum()
            Total_paid=filter_df["AmountPaid"].sum()
            Balance_Amount=Total_Amount-Total_paid
        if checkbox:
            filter_df=df[(df['VendorName']==f"{vendor_name}") & df['InvoiceDate']==invoice_date]
            print(type(df['InvoiceDate']))
            print(type(invoice_date))
            print(vendor_name)
            print(filter_df)
            Total_Amount=filter_df["Amount"].sum()
            Total_paid=filter_df["AmountPaid"].sum()
            Balance_Amount=round(Total_Amount-Total_paid)
        st.write(filter_df)
    if Balance_Amount<0:
        st.write(f"Total Amount is: {Total_Amount} RS")
        st.write(f"Total Amount Paid: {Total_paid} RS")
        st.write("Balance_Amount: 0 RS")
    else:
        st.write(f"Total Amount is: {Total_Amount} RS")
        st.write(f"Total Amount Paid: {Total_paid} RS")
        st.write(f"Balance Amount: {Balance_Amount} RS")
    # st.button(st.experimental_rerun())
    # st.dataframe(existing_data)

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