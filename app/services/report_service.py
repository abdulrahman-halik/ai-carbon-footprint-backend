from __future__ import annotations

import csv
import io
from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Tuple

from app.models.emission_model import EmissionModel
from app.models.energy_model import EnergyModel
from app.models.goal_model import GoalModel
from app.models.water_model import WaterModel


def _period_window(period: str) -> Tuple[datetime, datetime, datetime, datetime]:
    now = datetime.utcnow()
    if period == "monthly":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        previous_end = start
        previous_start = (start - timedelta(days=1)).replace(day=1)
        return start, now, previous_start, previous_end

    if period == "yearly":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        previous_start = start.replace(year=start.year - 1)
        previous_end = start
        return start, now, previous_start, previous_end

    raise ValueError("period must be 'monthly' or 'yearly'")


def _filter_records(records: Iterable[dict], start: datetime, end: datetime) -> List[dict]:
    filtered = []
    for record in records:
        record_date = record.get("date") or record.get("created_at")
        if isinstance(record_date, datetime) and start <= record_date < end:
            filtered.append(record)
    return filtered


def _sum_values(records: Iterable[dict]) -> float:
    return round(sum(float(record.get("value", 0.0) or 0.0) for record in records), 2)


def _category_breakdown(records: Iterable[dict]) -> Dict[str, float]:
    summary: Dict[str, float] = {}
    for record in records:
        category = str(record.get("category") or record.get("energy_type") or "General")
        summary[category] = round(summary.get(category, 0.0) + float(record.get("value", 0.0) or 0.0), 2)
    return dict(sorted(summary.items(), key=lambda item: item[0]))


async def build_report_summary(user: dict, period: str) -> Dict[str, object]:
    start, end, previous_start, previous_end = _period_window(period)
    user_id = str(user["_id"])

    emissions = _filter_records(await EmissionModel.find_by_user_id(user_id), start, end)
    previous_emissions = _filter_records(await EmissionModel.find_by_user_id(user_id), previous_start, previous_end)
    energy_logs = _filter_records(await EnergyModel.find_by_user_id(user_id), start, end)
    water_logs = _filter_records(await WaterModel.find_by_user_id(user_id), start, end)
    goals = list(GoalModel.get_collection().find({"user_id": user_id, "is_active": True}))

    total_emissions = _sum_values(emissions)
    previous_total_emissions = _sum_values(previous_emissions)
    carbon_saved = round(max(previous_total_emissions - total_emissions, 0.0), 2)

    return {
        "period": period,
        "generated_at": datetime.utcnow().isoformat(),
        "member": (user.get("full_name") or "Eco Member").split("@")[0],
        "totals": {
            "emissions": total_emissions,
            "energy_usage": _sum_values(energy_logs),
            "water_usage": _sum_values(water_logs),
            "carbon_saved": carbon_saved,
            "active_goals": len(goals),
        },
        "counts": {
            "emission_records": len(emissions),
            "energy_records": len(energy_logs),
            "water_records": len(water_logs),
        },
        "breakdown": {
            "emissions": _category_breakdown(emissions),
            "energy": _category_breakdown(energy_logs),
            "water": _category_breakdown(water_logs),
        },
    }


def _build_csv(summary: Dict[str, object]) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["period", summary["period"]])
    writer.writerow(["generated_at", summary["generated_at"]])
    writer.writerow([])
    writer.writerow(["metric", "value"])
    for key, value in summary["totals"].items():
        writer.writerow([key, value])
    writer.writerow([])
    writer.writerow(["record_type", "count"])
    for key, value in summary["counts"].items():
        writer.writerow([key, value])
    writer.writerow([])
    writer.writerow(["breakdown_group", "category", "value"])
    for group, values in summary["breakdown"].items():
        for category, value in values.items():
            writer.writerow([group, category, value])
    return buffer.getvalue().encode("utf-8")


def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_simple_pdf(lines: List[str]) -> bytes:
    content_lines = ["BT", "/F1 12 Tf", "50 780 Td", "14 TL"]
    first = True
    for line in lines:
        text = _escape_pdf_text(line)
        if first:
            content_lines.append(f"({_escape_pdf_text(line)}) Tj")
            first = False
        else:
            content_lines.append(f"T* ({text}) Tj")
    content_lines.append("ET")
    content_stream = "\n".join(content_lines).encode("utf-8")

    objects = []
    objects.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    objects.append(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
    objects.append(b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n")
    objects.append(f"4 0 obj << /Length {len(content_stream)} >> stream\n".encode("utf-8") + content_stream + b"\nendstream endobj\n")
    objects.append(b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj)
    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)}\n".encode("utf-8"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("utf-8"))
    pdf.extend(
        f"trailer << /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF".encode("utf-8")
    )
    return bytes(pdf)


def _build_pdf(summary: Dict[str, object]) -> bytes:
    totals = summary["totals"]
    lines = [
        f"Sustainability Report - {summary['period'].title()}",
        f"Generated: {summary['generated_at']}",
        f"Member: {summary['member']}",
        "",
        f"Total emissions: {totals['emissions']} kg CO2e",
        f"Energy usage: {totals['energy_usage']}",
        f"Water usage: {totals['water_usage']}",
        f"Carbon saved vs previous period: {totals['carbon_saved']} kg CO2e",
        f"Active goals: {totals['active_goals']}",
    ]
    return _build_simple_pdf(lines)


async def generate_report_download(user: dict, period: str, export_format: str) -> Tuple[bytes, str, str]:
    export_format = export_format.lower()
    if export_format not in {"csv", "pdf"}:
        raise ValueError("format must be 'csv' or 'pdf'")

    summary = await build_report_summary(user, period)
    if export_format == "csv":
        filename = f"{period}-sustainability-report.csv"
        return _build_csv(summary), filename, "text/csv; charset=utf-8"

    filename = f"{period}-sustainability-report.pdf"
    return _build_pdf(summary), filename, "application/pdf"