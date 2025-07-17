import streamlit as st
import pandas as pd
from src.ocr import perform_ocr


hide_github_icon = """
    <style>
        .css-1dp5vir.e1tzin5v3 {visibility: hidden;} /* GitHub link in top right */
        footer {visibility: hidden;}  /* Streamlit footer */
    </style>
"""
st.markdown(hide_github_icon, unsafe_allow_html=True)

st.title("Claims Processing")

uploaded_files = st.file_uploader(
    "Upload one or multiple PDF files",
    type="pdf",
    accept_multiple_files=True,
)

if uploaded_files:
    st.write(f"Number of files uploaded: {len(uploaded_files)}")

    payment_options = ["OD Repair Cost", "Windscreen Repair Cost", "TPPD Repair Cost"]

    with st.form("claims_form"):
        st.subheader("Set Payment Categories")
        # Create a selectbox for each uploaded file
        for i, uploaded_file in enumerate(uploaded_files):
            st.selectbox(
                f'Payment Category for "{uploaded_file.name}"',
                options=payment_options,
                key=f"category_{i}",
            )

        submitted = st.form_submit_button("Process Claims")

        if submitted:
            extracted_data = []
            with st.spinner("Performing OCR on uploaded files... Please wait."):
                for i, uploaded_file in enumerate(uploaded_files):
                    st.write(f"Processing {uploaded_file.name}...")
                    file_bytes = uploaded_file.getvalue()

                    # Get the selected category from session state
                    payment_category = st.session_state[f"category_{i}"]
                    ocr_result = perform_ocr(file_bytes)

                    if ocr_result:
                        data = {
                            "Filename": uploaded_file.name,
                            "Payment Category": payment_category,
                            "Payee: Account Name": ocr_result.payee_account_name,
                            "Net Amount": ocr_result.net_amount,
                            "VAT Amount": ocr_result.vat_amount,
                            "Gross Amount": ocr_result.gross_amount,
                            "Tax Invoice No": ocr_result.tax_invoice_number,
                            "Tax Invoice Date": ocr_result.tax_invoice_date,
                            "Invoice No": ocr_result.invoice_number,
                            "Invoice Date": ocr_result.invoice_date,
                        }
                        extracted_data.append(data)
                    else:
                        # Add a placeholder for a failed file
                        data = {
                            "Filename": uploaded_file.name,
                            "Payment Category": payment_category,
                            "Error": "Failed to extract data",
                        }
                        extracted_data.append(data)

            if extracted_data:
                df = pd.DataFrame(extracted_data)
                st.subheader("Extracted Information")
                st.dataframe(df)
