import streamlit as st
import os
from google import genai
from google.genai import types
from src.models import ExtractionResult
import json


def perform_ocr(pdf_bytes: bytes) -> ExtractionResult | None:
    """
    Performs OCR on a PDF file using Google's Gemini API and returns structured data.
    """
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        st.warning(
            "GEMINI_API_KEY not found in Streamlit secrets. "
            "Using the provided key as a fallback. This is not secure for production."
        )
        api_key = "AIzaSyCV5VRH9TxTh95C36bEMMy7IqepIQklHX8"  # User-provided fallback

    os.environ["GEMINI_API_KEY"] = api_key

    try:
        # The client gets the API key from the environment variable `GEMINI_API_KEY`.
        client = genai.Client()
    except Exception as e:
        st.error(f"Failed to create Gemini client: {e}")
        return None

    model = "gemini-2.5-flash"

    prompt = """
    You are an expert AI data extraction assistant specializing in financial documents.
    Your task is to meticulously analyze the provided PDF document, which is an invoice or a claim-related document,
    and extract specific pieces of information.

    **Important Note:** The document you will be processing is written in the **Thai language**.
    You must be able to read and interpret Thai script and financial terms.

    **Instructions:**
    1.  Read the entire document carefully to identify the required fields.
    2.  The output MUST be a valid JSON object that strictly adheres to the provided `ExtractionResult` schema.
    3.  Do not add any fields that are not in the schema.
    4.  If a specific field cannot be found in the document, you MUST return an empty string ("") for that field. Do not guess or invent information.

    **Field Extraction Guide (with Thai Keywords):**
    -   **payee_account_name**: The name of the person or company to be paid. Look for English terms like 'Payee', 'Beneficiary', 'Account Name', or Thai terms like 'ชื่อผู้รับเงิน', 'ชื่อบัญชี'. Should be in the format "8699.40".
    -   **net_amount**: The subtotal amount before any taxes are applied. Look for English terms like 'Subtotal', 'Net Amount', or Thai terms like 'ยอดสุทธิก่อนภาษี', 'มูลค่าสินค้า', 'จำนวนเงิน'. Should be in the format "8699.40".
    -   **vat_amount**: The Value Added Tax (VAT) amount. Look for English terms like 'VAT', 'GST', or Thai terms like 'ภาษีมูลค่าเพิ่ม', 'VAT 7%'. Should be in the format "8699.40".
    -   **gross_amount**: The final, total amount to be paid. Look for English terms like 'Total', 'Gross Amount', 'Grand Total', or Thai terms like 'ยอดรวมทั้งสิ้น', 'รวมเป็นเงิน', 'ยอดสุทธิ'.
    -   **tax_invoice_number**: The unique identifier for the tax invoice. Look for English labels like 'Tax Invoice No.', 'TIN', or Thai terms like 'เลขที่ใบกำกับภาษี'. If not present, check for a general invoice number.
    -   **tax_invoice_date**: The date the tax invoice was issued. Look for English 'Tax Invoice Date' or Thai 'วันที่ใบกำกับภาษี', or a general 'Date' field associated with the invoice.
    -   **invoice_number**: The unique number for the invoice itself. Look for Thai 'เลขที่ใบแจ้งหนี้' or 'เลขที่'. If only one invoice number is on the document, use it for both this field and `tax_invoice_number`.
    -   **invoice_date**: The date the invoice was issued. Look for Thai 'วันที่'. If only one date is on the document, use it for both this field and `tax_invoice_date`. Should be in the format DD/MM/YYYY.

    Please process the document and provide the extracted data in the specified JSON format.
    """

    try:
        response = client.models.generate_content(
            model=model,
            contents=[
                types.Part.from_bytes(
                    data=pdf_bytes,
                    mime_type="application/pdf",
                ),
                prompt,
            ],
            config={
                "response_mime_type": "application/json",
                "response_schema": ExtractionResult,
            },
        )
        result_dict = json.loads(response.text)
        return ExtractionResult(**result_dict)
    except Exception as e:
        st.error(f"An error occurred during OCR processing: {e}")
        if "response" in locals() and hasattr(response, "prompt_feedback"):
            st.warning(f"Prompt Feedback: {response.prompt_feedback}")
        return None
