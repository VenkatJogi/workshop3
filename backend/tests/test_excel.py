from io import BytesIO
import pandas as pd
import pytest
from app.services.excel_service import ExcelValidationError, excel_service

def test_all_curated_workbooks_are_valid():
    for name in ("inventory", "orders", "suppliers"):
        rows, validation = excel_service.read_sample(name)
        assert rows and validation.status == "VALID"

def test_rejects_non_excel_extension():
    with pytest.raises(ExcelValidationError):
        excel_service.read(b"bad", "inventory.csv", "inventory")

def test_reports_missing_required_columns():
    stream = BytesIO()
    pd.DataFrame({"product_id": ["P1"]}).to_excel(stream, index=False)
    rows, validation = excel_service.read(stream.getvalue(), "inventory.xlsx", "inventory")
    assert rows == [] and validation.status == "INVALID"
    assert "Missing required columns" in validation.errors[0]
