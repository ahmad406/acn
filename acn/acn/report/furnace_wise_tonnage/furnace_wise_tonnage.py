import frappe
from frappe import _
from datetime import datetime
import calendar


def execute(filters=None):
    filters = filters or {}

    month = int(filters.get("month") or datetime.now().month)
    year = int(filters.get("year") or datetime.now().year)

    total_days = calendar.monthrange(year, month)[1]

    # Fetch all furnace codes from Furnace master
    furnaces = frappe.get_all("Furnace", fields=["name"], order_by="name asc")
    furnace_codes = [f["name"] for f in furnaces]

    # ----------------------------------------------------------------
    # Build columns
    # ----------------------------------------------------------------
    columns = [
        {
            "label": _("FURNACE"),
            "fieldname": "furnace_label",
            "fieldtype": "Data",
            "width": 160,
        }
    ]
    for fc in furnace_codes:
        columns.append({
            "label": _(fc),
            "fieldname": frappe.scrub(fc),
            "fieldtype": "Data",
            "width": 110,
        })

    # ----------------------------------------------------------------
    # Fetch sum of planned_qty_in_kgs from child table grouped by
    # parent's furnace_code and execution_date
    # ----------------------------------------------------------------
    month_start = f"{year}-{month:02d}-01"
    month_end = f"{year}-{month:02d}-{total_days:02d}"

    raw = frappe.db.sql(
        """
        SELECT
            jel.furnace_code,
            jel.execution_date,
            SUM(pj.planned_qty_in_kgs) AS total_kgs
        FROM
            `tabJob Execution Logsheet` jel
        INNER JOIN
            `tabJob Execution Logsheet child` pj ON pj.parent = jel.name
        WHERE
            jel.execution_date IS NOT NULL
            AND jel.execution_date >= %(month_start)s
            AND jel.execution_date <= %(month_end)s
            AND pj.planned_qty_in_kgs IS NOT NULL
        GROUP BY
            jel.furnace_code,
            jel.execution_date
        """,
        {"month_start": month_start, "month_end": month_end},
        as_dict=True,
    )

    # ----------------------------------------------------------------
    # Aggregate tonnage: data[day][furnace_code] = total tonnes
    # ----------------------------------------------------------------
    data = {day: {fc: 0.0 for fc in furnace_codes} for day in range(1, total_days + 1)}

    for row in raw:
        fc = row["furnace_code"]
        if fc not in furnace_codes:
            continue

        exec_date = row["execution_date"]
        if isinstance(exec_date, str):
            exec_date = datetime.strptime(exec_date, "%Y-%m-%d").date()

        day_num = exec_date.day
        if day_num not in data:
            continue

        # Convert kgs to tonnes
        tonnes = float(row["total_kgs"] or 0) / 1000.0
        data[day_num][fc] += tonnes

    # ----------------------------------------------------------------
    # Build rows
    # ----------------------------------------------------------------
    result = []

    # Static "KGS" subheader row
    kgs_row = {"furnace_label": "KGS"}
    for fc in furnace_codes:
        kgs_row[frappe.scrub(fc)] = "KGS"
    result.append(kgs_row)

    # Day rows
    col_totals = {fc: 0.0 for fc in furnace_codes}

    for day in range(1, total_days + 1):
        row = {"furnace_label": str(day)}
        for fc in furnace_codes:
            tonnes = data[day].get(fc, 0.0)
            col_totals[fc] += tonnes
            row[frappe.scrub(fc)] = f"{tonnes:.2f}"
        result.append(row)

    # TOTAL TONNAGE row
    total_row = {"furnace_label": "TOTAL TONNAGE"}
    for fc in furnace_codes:
        total_row[frappe.scrub(fc)] = f"{col_totals[fc]:.2f}"
    result.append(total_row)

    return columns, result