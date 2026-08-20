from io import BytesIO
from pathlib import Path
from typing import BinaryIO
import pandas as pd
from fastapi import UploadFile
from app.models.agent_outputs import FileValidation

SCHEMAS = {
    "inventory": ["product_id","product_name","category","current_stock","reorder_level","maximum_stock","unit_cost","warehouse"],
    "orders": ["order_id","product_id","product_name","quantity","order_date","customer","priority","status"],
    "suppliers": ["supplier_id","supplier_name","product_id","product_name","unit_price","minimum_order_quantity","lead_time_days","reliability_score","supplier_type"],
}
NUMERIC = {
    "inventory": ["current_stock","reorder_level","maximum_stock","unit_cost"],
    "orders": ["quantity"],
    "suppliers": ["unit_price","minimum_order_quantity","lead_time_days","reliability_score"],
}

class ExcelValidationError(ValueError): pass

class ExcelService:
    sample_dir = Path(__file__).resolve().parents[3] / "data" / "sample_data"

    def read(self, source: bytes | BinaryIO | Path, file_name: str, dataset: str) -> tuple[list[dict], FileValidation]:
        if dataset not in SCHEMAS: raise ExcelValidationError(f"Unknown dataset: {dataset}")
        if not file_name.lower().endswith(".xlsx"): raise ExcelValidationError(f"{file_name}: only .xlsx files are accepted")
        try:
            frame = pd.read_excel(BytesIO(source) if isinstance(source, bytes) else source, engine="openpyxl")
        except Exception as exc: raise ExcelValidationError(f"{file_name}: invalid Excel workbook") from exc
        frame.columns = [str(column).strip().lower().replace(" ", "_") for column in frame.columns]
        missing_columns = sorted(set(SCHEMAS[dataset]) - set(frame.columns))
        errors = [f"Missing required columns: {', '.join(missing_columns)}"] if missing_columns else []
        for column in NUMERIC[dataset]:
            if column in frame: frame[column] = pd.to_numeric(frame[column], errors="coerce")
        if dataset == "orders" and "order_date" in frame:
            frame["order_date"] = pd.to_datetime(frame["order_date"], errors="coerce")
        missing = {key:int(value) for key,value in frame.isna().sum().items() if value}
        if missing: errors.append(f"Missing or invalid values detected in {len(missing)} columns")
        duplicates = int(frame.duplicated().sum())
        if duplicates: errors.append(f"{duplicates} duplicate rows detected")
        validation = FileValidation(file_name=file_name,dataset=dataset,rows=len(frame),columns=list(frame.columns),missing_values=missing,duplicates=duplicates,status="INVALID" if missing_columns or missing else "VALID",errors=errors)
        if missing_columns: return [], validation
        frame = frame.drop_duplicates().where(pd.notna(frame), None)
        if dataset == "orders": frame["order_date"] = frame["order_date"].map(lambda value: value.isoformat() if value is not None else None)
        return frame.to_dict(orient="records"), validation

    async def read_upload(self, upload: UploadFile, dataset: str):
        return self.read(await upload.read(), upload.filename or f"{dataset}.xlsx", dataset)

    def read_sample(self, dataset: str):
        path=self.sample_dir / f"{dataset}.xlsx"
        return self.read(path, path.name, dataset)

excel_service = ExcelService()
