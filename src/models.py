from pydantic import BaseModel, Field


class ExtractionResult(BaseModel):
    payee_account_name: str = Field(description="The name of the payee's account.")
    net_amount: str = Field(description="The amount before tax.")
    vat_amount: str = Field(description="The value added tax amount.")
    gross_amount: str = Field(description="The total amount including tax.")
    tax_invoice_number: str = Field(description="The unique identifier for the tax invoice.")
    tax_invoice_date: str = Field(description="The date the tax invoice was issued.")
    invoice_number: str = Field(description="The unique identifier for the invoice.")
    invoice_date: str = Field(description="The date the invoice was issued.")
