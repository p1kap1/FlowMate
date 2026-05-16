import json
import os
from datetime import date, datetime
from typing import Optional

from config import RECORDS_FILE


def _load() -> list[dict]:
    if not os.path.exists(RECORDS_FILE):
        return []
    with open(RECORDS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _save(records: list[dict]) -> None:
    os.makedirs(os.path.dirname(RECORDS_FILE), exist_ok=True)
    with open(RECORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def add_record(date_str: str, description: str, time_spent: float, category: str) -> dict:
    records = _load()
    new_id = max((r.get("id", 0) for r in records), default=0) + 1
    record = {
        "id": new_id,
        "date": date_str,
        "description": description,
        "time_spent": time_spent,
        "category": category,
        "created_at": datetime.now().isoformat(),
    }
    records.append(record)
    _save(records)
    return record


def list_by_date(date_str: Optional[str] = None) -> list[dict]:
    records = _load()
    if date_str:
        records = [r for r in records if r["date"] == date_str]
    records.sort(key=lambda r: r["date"], reverse=True)
    return records


def list_by_date_range(start_date: str, end_date: str) -> list[dict]:
    records = _load()
    result = [r for r in records if start_date <= r["date"] <= end_date]
    result.sort(key=lambda r: r["date"])
    return result


def search_keywords(keywords: str) -> list[dict]:
    records = _load()
    terms = [kw.strip().lower() for kw in keywords.split(",") if kw.strip()]
    matched = []
    for r in records:
        text = f"{r['description']} {r['category']}".lower()
        if any(term in text for term in terms):
            matched.append(r)
    matched.sort(key=lambda r: r["date"], reverse=True)
    return matched


def all_records() -> list[dict]:
    records = _load()
    records.sort(key=lambda r: r["date"], reverse=True)
    return records
