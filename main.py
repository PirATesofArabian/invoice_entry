import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from streamlit_dynamic_filters import DynamicFilters

# Display Title and Description
st.title("Pragathi Motors Vendor Invoice Portal")

# Constants
VENDORS = [
    "JHADE AUTO SPARES",
    "DIAMOND AUTO PARTS",
    "VIKAS TRADE LINKS PVT LTD",
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
    "AUTOVERSE MOBILITY PUTO LIMITED",
    "OM SHREE ENTERPRISES",
    "ADVAITH SPARES AND ACCESSORIES",
    "RK AUTOMOBILES",
    "SWETADRI ASSOCIATES"
]
PRODUCTS = [
    "Electronics",
    "Apparel",
    "Groceries",
    "Software",
    "Other",
]

# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch existing vendors data
existing_data = conn.read(worksheet="Sheet1", usecols=list(range(6)), ttl=5)
existing_data = existing_data.dropna(how="all")

action = st.selectbox(
    "Choose an Action",
    [
        "Enter invoice Entry",
        "Update Existing Vendor",
        "View Vendor Data",
        "Delete Vendor Invoice",
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
        Amount = st.number_input('Enter the Amount',min_value=0.0)
        # AmountPaid=st.text_input("")
        AmountPaid= st.number_input("Enter amount paid",min_value=0.0)
        # additional_info = st.text_area(label="Additional Notes")
        UpdatePaymentDate= st.text_input("Enter the date of payment")

        # st.markdown("**required*")
        submit_button = st.form_submit_button(label="Submit Vendor Details")

        if submit_button:
            if not invoice_number or not vendor_name:
                st.warning("Ensure all mandatory fields are filled.")
            elif existing_data["VendorName"].str.contains(vendor_name).any() and existing_data["InvoiceNumber"].astype(str).str.contains(invoice_number).any():
                st.warning("Invoice number for this vendor already exists.")
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
                            "UpdatePaymentDate":UpdatePaymentDate
                            # "AdditionalInfo": additional_info,
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
        vendor_name = st.text_input("Vendor is",value=vendor_data["VendorName"])
        option=st.checkbox("want to update vendor name?")
        # if option:
        vendor_update=st.selectbox("Select the vendor to update",options=VENDORS)
        Amount= st.number_input("Enter the Amount",int(vendor_data["Amount"]))
        invoice_date = st.date_input(
            label="Invoice Date", value=pd.to_datetime(vendor_data["InvoiceDate"])
            
        )
        AmountPaid= st.number_input("Enter amount paid",int(vendor_data["AmountPaid"]))
        UpdatePaymentDate= st.text_input("Enter the date of payment",value=vendor_data["UpdatePaymentDate"])
        # additional_info = st.text_area(
        #     label="Additional Notes", value=vendor_data["AdditionalInfo"]
        # )

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
                if option:
                    updated_vendor_data = pd.DataFrame(
                    [
                        {
                            "InvoiceNumber": invoice_number,
                            "VendorName": vendor_update,
                           # "Products": ", ".join(products),
                            "Amount": Amount,
                            "InvoiceDate": invoice_date.strftime("%Y-%m-%d"),
                            "AmountPaid": AmountPaid,
                            "UpdatePaymentDate": UpdatePaymentDate,
                            # "AdditionalInfo": additional_info,
                        }
                    ]
                )
                else:
                    updated_vendor_data = pd.DataFrame(
                        [
                            {
                                "InvoiceNumber": invoice_number,
                                "VendorName": vendor_name,
                            # "Products": ", ".join(products),
                                "Amount": Amount,
                                "InvoiceDate": invoice_date.strftime("%Y-%m-%d"),
                                "AmountPaid": AmountPaid,
                                "UpdatePaymentDate": UpdatePaymentDate,
                                # "AdditionalInfo": additional_info,
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
elif action == "View Vendor Data":
    existing_data["InvoiceNumber"]=round(existing_data["InvoiceNumber"])
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
    date_checkbox=st.checkbox(label="Tick if want to search by date only")
    # vendor_name = st.selectbox("Select the vendor",options=VENDORS)
    # dynamic_filters.display_df()
    
    full_data=st.checkbox(label="Tick if you want to see data for all vendors")
    if full_data:
        Total_Amount=df["Amount"].sum()
        Total_paid=df["AmountPaid"].sum()
        Balance_Amount=round(Total_Amount-Total_paid)
        st.write("**:red[Showing Data for all Vendors]**")
        st.write(df)
    else:
        if not checkbox:
            if date_checkbox:
                print(df['InvoiceDate'].to_string()[5:])
                print("")
                filter_df=df[(df['InvoiceDate'].str.contains(invoice_date.strftime("%Y-%m-%d")))]
                Total_Amount=filter_df["Amount"].sum()
                Total_paid=filter_df["AmountPaid"].sum()
                Balance_Amount=round(Total_Amount-Total_paid)
                st.write("**:red[Showing Results based on Date filter]**")
                # pass
            else:
                filter_df=df[(df['VendorName']==f"{vendor_name}")]
                Total_Amount=filter_df["Amount"].sum()
                Total_paid=filter_df["AmountPaid"].sum()
                Balance_Amount=Total_Amount-Total_paid
                st.write("**:green[Showing results based on Vendor filter]**")
        elif checkbox:
            filter_df=df[(df['VendorName']==f"{vendor_name}") & (df['InvoiceDate'].str.contains(invoice_date.strftime("%Y-%m-%d")))]
            print()
            print(df['InvoiceDate'][0])
            print(invoice_date.strftime("%Y-%m-%d"))
            print(df['VendorName'])
            Total_Amount=filter_df["Amount"].sum()
            Total_paid=filter_df["AmountPaid"].sum()
            Balance_Amount=round(Total_Amount-Total_paid)
            st.write("**:orange[Showing Results based on vendor and Date filter]**")
        st.write(filter_df)
        # st.line_chart(df,x=df["InvoiceDate"].filter(),y=df["Amount"])
    st.write(f"Total Invoice Amount is: {Total_Amount} RS")
    st.write(f"Total Amount Paid: {Total_paid} RS")
    st.write(f"Balance Amount: {Balance_Amount} RS")
    # else:
    #     st.write(f"Total Invoice Amount is: {Total_Amount} RS")
    #     st.write(f"Total Amount Paid: {Total_paid} RS")
    #     st.write(f"Balance Amount: {Balance_Amount} RS")
    # st.button(st.experimental_rerun())
    # st.dataframe(existing_data)

# Delete Vendor
elif action == "Delete Vendor Invoice":
    vendor_to_delete = st.selectbox(
        "Select a Vendor Invoice to Delete", options=existing_data["InvoiceNumber"].tolist()
    )

    if st.button("Delete"):
        existing_data.drop(
            existing_data[existing_data["InvoiceNumber"] == vendor_to_delete].index,
            inplace=True,
        )
        conn.update(worksheet="Sheet1", data=existing_data)
        st.success("Vendor Invoice successfully deleted!")