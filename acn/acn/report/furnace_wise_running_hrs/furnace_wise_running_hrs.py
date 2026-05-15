import frappe
from frappe import _
from datetime import datetime, timedelta
import calendar


def execute(filters=None):
    filters = filters or {}

    month = int(filters.get("month") or datetime.now().month)
    year = int(filters.get("year") or datetime.now().year)

    # Total days in selected month
    total_days = calendar.monthrange(year, month)[1]
    # Total hours in month
    total_hours_in_month = total_days * 24

    # Fetch all furnace codes from Furnace master
    furnaces = frappe.get_all(
        "Furnace",
        fields=["name"],
        order_by="name asc"
    )
    furnace_codes = [f["name"] for f in furnaces]

    # ----------------------------------------------------------------
    # Build columns
    # ----------------------------------------------------------------
    columns = [
        {
            "label": _("FURNACE"),
            "fieldname": "furnace_label",
            "fieldtype": "Data",
            "width": 220,
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
    # Fetch all Job Execution Logsheets for this month in one query
    # ----------------------------------------------------------------
    month_start = f"{year}-{month:02d}-01 00:00:00"
    month_end_day = total_days
    month_end = f"{year}-{month:02d}-{month_end_day:02d} 23:59:59"

    raw = frappe.db.sql(
        """
        SELECT
            furnace_code,
            actual_start_date_time,
            actual_end_date_time
        FROM
            `tabJob Execution Logsheet`
        WHERE
            actual_start_date_time IS NOT NULL
            AND actual_end_date_time IS NOT NULL
            AND actual_start_date_time <= %(month_end)s
            AND actual_end_date_time >= %(month_start)s
        """,
        {"month_start": month_start, "month_end": month_end},
        as_dict=True,
    )

    # ----------------------------------------------------------------
    # Aggregate running seconds: data[day][furnace_code] = total_seconds
    # We attribute time to whichever calendar day the running falls into.
    # If a job spans midnight we split it proportionally per day.
    # ----------------------------------------------------------------
    # data[day_number] = {furnace_code: seconds}
    data = {day: {fc: 0 for fc in furnace_codes} for day in range(1, total_days + 1)}

    for row in raw:
        fc = row["furnace_code"]
        if fc not in furnace_codes:
            continue

        start_dt = row["actual_start_date_time"]
        end_dt = row["actual_end_date_time"]

        if isinstance(start_dt, str):
            start_dt = datetime.strptime(start_dt, "%Y-%m-%d %H:%M:%S")
        if isinstance(end_dt, str):
            end_dt = datetime.strptime(end_dt, "%Y-%m-%d %H:%M:%S")

        # Clamp to month boundaries
        month_start_dt = datetime(year, month, 1, 0, 0, 0)
        month_end_dt = datetime(year, month, total_days, 23, 59, 59)
        start_dt = max(start_dt, month_start_dt)
        end_dt = min(end_dt, month_end_dt)

        if end_dt <= start_dt:
            continue

        # Walk through each day this job touches
        cursor = start_dt
        while cursor < end_dt:
            day_num = cursor.day
            day_end = datetime(cursor.year, cursor.month, cursor.day, 23, 59, 59)
            effective_end = min(end_dt, day_end)
            seconds = (effective_end - cursor).total_seconds()
            if day_num in data:
                data[day_num][fc] = data[day_num].get(fc, 0) + seconds
            # Move to start of next day
            cursor = datetime(cursor.year, cursor.month, cursor.day) + timedelta(days=1)

    # ----------------------------------------------------------------
    # Helper: seconds → "HH:MM:SS"
    # ----------------------------------------------------------------
    def secs_to_hms(seconds):
        seconds = int(seconds)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    # ----------------------------------------------------------------
    # Build rows
    # ----------------------------------------------------------------
    result = []

    # Static "HRS" subheader row (mirrors the image)
    hrs_row = {"furnace_label": "HRS"}
    for fc in furnace_codes:
        hrs_row[frappe.scrub(fc)] = "HRS"
    result.append(hrs_row)

    # Day rows
    col_totals = {fc: 0 for fc in furnace_codes}  # total seconds per furnace

    for day in range(1, total_days + 1):
        row = {"furnace_label": str(day)}
        for fc in furnace_codes:
            secs = data[day].get(fc, 0)
            col_totals[fc] += secs
            row[frappe.scrub(fc)] = secs_to_hms(secs)
        result.append(row)

    # TOTAL RUNNING HOURS row
    total_run_row = {"furnace_label": "TOTAL RUNNING HOURS"}
    for fc in furnace_codes:
        total_run_row[frappe.scrub(fc)] = secs_to_hms(col_totals[fc])
    result.append(total_run_row)

    # TOTAL IDLE TIME row
    total_idle_row = {"furnace_label": "TOTAL IDLE TIME"}
    month_total_secs = total_hours_in_month * 3600
    for fc in furnace_codes:
        idle = month_total_secs - col_totals[fc]
        total_idle_row[frappe.scrub(fc)] = secs_to_hms(max(idle, 0))
    result.append(total_idle_row)

    # TOTAL HOURS row
    total_hours_row = {"furnace_label": "TOTAL HOURS"}
    for fc in furnace_codes:
        total_hours_row[frappe.scrub(fc)] = secs_to_hms(month_total_secs)
    result.append(total_hours_row)

    # FURNACE UTILISATION IN % row
    util_row = {"furnace_label": "FURNACE UTILISATION IN %"}
    for fc in furnace_codes:
        if month_total_secs > 0:
            pct = (col_totals[fc] / month_total_secs) * 100
            util_row[frappe.scrub(fc)] = f"{pct:.2f}%"
        else:
            util_row[frappe.scrub(fc)] = "0%"
    result.append(util_row)

    return columns, result