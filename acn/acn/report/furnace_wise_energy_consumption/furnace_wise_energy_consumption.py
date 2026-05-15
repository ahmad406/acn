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
    # Fetch all Job Execution Logsheets for this month using execution_date
    # ----------------------------------------------------------------
    month_start = f"{year}-{month:02d}-01"
    month_end = f"{year}-{month:02d}-{total_days:02d}"

    raw = frappe.db.sql(
        """
        SELECT
            furnace_code,
            execution_date,
            energy_start_reading,
            energy_end_reading
        FROM
            `tabJob Execution Logsheet`
        WHERE
            execution_date IS NOT NULL
            AND energy_start_reading IS NOT NULL
            AND energy_end_reading IS NOT NULL
            AND execution_date >= %(month_start)s
            AND execution_date <= %(month_end)s
        """,
        {"month_start": month_start, "month_end": month_end},
        as_dict=True,
    )

    # ----------------------------------------------------------------
    # Aggregate units: data[day][furnace_code] = total units
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

        units = float(row["energy_end_reading"] or 0) - float(row["energy_start_reading"] or 0)
        if units < 0:
            units = 0  # ignore bad data

        data[day_num][fc] += units

    # ----------------------------------------------------------------
    # Build rows
    # ----------------------------------------------------------------
    result = []

    # Static "UNITS" subheader row
    units_row = {"furnace_label": "UNITS"}
    for fc in furnace_codes:
        units_row[frappe.scrub(fc)] = "UNITS"
    result.append(units_row)

    # Day rows
    col_totals = {fc: 0.0 for fc in furnace_codes}

    for day in range(1, total_days + 1):
        row = {"furnace_label": str(day)}
        for fc in furnace_codes:
            units = data[day].get(fc, 0.0)
            col_totals[fc] += units
            row[frappe.scrub(fc)] = f"{units:.2f}" if units else "0.00"
        result.append(row)

    # TOTAL ENERGY CONSUMPTION row
    total_row = {"furnace_label": "TOTAL ENERGY CONSUMPTION"}
    for fc in furnace_codes:
        total_row[frappe.scrub(fc)] = f"{col_totals[fc]:.2f}"
    result.append(total_row)

    return columns, result