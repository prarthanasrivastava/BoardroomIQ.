from __future__ import annotations

from dataclasses import asdict, is_dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from boardroomiq.core.pipeline import run_boardroom_analysis, run_flexible_boardroom_analysis
from boardroomiq.utils.data_loader import read_sample_data


class AnalyzeRequest(BaseModel):
    question: str = "Why did revenue drop this quarter and what should we do?"


def to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return to_jsonable(asdict(value))
    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    return value


def clean_dataset_name(filename: str, fallback: str) -> str:
    stem = Path(filename).stem.strip().lower().replace(" ", "_")
    return stem or fallback


async def parse_uploads(files: list[UploadFile]) -> dict[str, pd.DataFrame]:
    data: dict[str, pd.DataFrame] = {}
    for index, file in enumerate(files, start=1):
        contents = await file.read()
        if not contents:
            continue

        suffix = Path(file.filename or "").suffix.lower()
        dataset_name = clean_dataset_name(file.filename or "", f"dataset_{index}")

        try:
            if suffix == ".csv":
                data[dataset_name] = pd.read_csv(BytesIO(contents))
            elif suffix in {".xlsx", ".xls"}:
                sheets = pd.read_excel(BytesIO(contents), sheet_name=None)
                if len(sheets) == 1:
                    data[dataset_name] = next(iter(sheets.values()))
                else:
                    for sheet_name, frame in sheets.items():
                        clean_sheet = str(sheet_name).strip().lower().replace(" ", "_")
                        data[f"{dataset_name}_{clean_sheet}"] = frame
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type for {file.filename}. Upload CSV, XLSX, or XLS files.",
                )
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Could not parse {file.filename}: {exc}") from exc

    if not data:
        raise HTTPException(status_code=400, detail="Upload at least one non-empty CSV or Excel file.")
    return data


app = FastAPI(
    title="BoardroomIQ API",
    description="Evidence-based multi-agent business intelligence API.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze/sample")
def analyze_sample(payload: AnalyzeRequest) -> dict[str, Any]:
    report = run_boardroom_analysis(payload.question, read_sample_data())
    return to_jsonable(report)


@app.post("/api/analyze/upload")
async def analyze_upload(
    question: str = Form("What insights can you find from this business data?"),
    files: list[UploadFile] = File(...),
) -> dict[str, Any]:
    data = await parse_uploads(files)
    report = run_flexible_boardroom_analysis(question, data)
    return to_jsonable(report)
