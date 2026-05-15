import frappe
from frappe import _
from datetime import datetime


def execute(filters=None):
    filters = filters or {}

    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    if not from_date or not to_date:
        frappe.throw(_("Please select From Date and To Date"))

    # Fetch all furnace codes
    furnaces = frappe.get_all("Furnace", fields=["name"], order_by="name asc")
    furnace_codes = [f["name"] for f in furnaces]

    # Fetch all internal processes
    processes = frappe.get_all("Internal Process", fields=["name"], order_by="name asc")
    process_names = [p["name"] for p in processes]

    # ----------------------------------------------------------------
    # Build columns — every sub-col labelled "GCF-1 KGS", "GCF-1 UNITS" etc.
    # ----------------------------------------------------------------
    columns = [
        {
            "label": _("FURNACE"),
            "fieldname": "process_label",
            "fieldtype": "Data",
            "width": 260,
        }
    ]
    for fc in furnace_codes:
        fc_scrub = frappe.scrub(fc)
        columns += [
            {
                "label": _(f"{fc}"),
                "fieldname": f"{fc_scrub}__kgs",
                "fieldtype": "Data",
                "width": 100,
            },
            {
                "label": _(f"{fc}"),
                "fieldname": f"{fc_scrub}__units",
                "fieldtype": "Data",
                "width": 100,
            },
            {
                "label": _(f"{fc}"),
                "fieldname": f"{fc_scrub}__hrs",
                "fieldtype": "Data",
                "width": 100,
            },
            {
                "label": _(f"{fc}"),
                "fieldname": f"{fc_scrub}__value",
                "fieldtype": "Data",
                "width": 120,
            },
        ]

    # ----------------------------------------------------------------
    # 1. KGS — sum planned_qty_in_kgs from production_jobs child table
    # ----------------------------------------------------------------
    kgs_raw = frappe.db.sql(
        """
        SELECT
            jel.furnace_code,
            jel.internal_process,
            SUM(pj.planned_qty_in_kgs) AS total_kgs
        FROM
            `tabJob Execution Logsheet` jel
        INNER JOIN
            `tabJob Execution Logsheet child` pj ON pj.parent = jel.name
        WHERE
            jel.execution_date IS NOT NULL
            AND jel.execution_date >= %(from_date)s
            AND jel.execution_date <= %(to_date)s
            AND pj.planned_qty_in_kgs IS NOT NULL
        GROUP BY
            jel.furnace_code,
            jel.internal_process
        """,
        {"from_date": from_date, "to_date": to_date},
        as_dict=True,
    )

    kgs_data = {p: {fc: 0.0 for fc in furnace_codes} for p in process_names}
    for row in kgs_raw:
        fc = row["furnace_code"]
        proc = row["internal_process"]
        if fc in furnace_codes and proc in kgs_data:
            kgs_data[proc][fc] += float(row["total_kgs"] or 0)

    # ----------------------------------------------------------------
    # 2. UNITS — energy_end_reading - energy_start_reading
    # ----------------------------------------------------------------
    units_raw = frappe.db.sql(
        """
        SELECT
            furnace_code,
            internal_process,
            SUM(
                CAST(COALESCE(energy_end_reading, 0) AS DECIMAL(20,4)) -
                CAST(COALESCE(energy_start_reading, 0) AS DECIMAL(20,4))
            ) AS total_units
        FROM
            `tabJob Execution Logsheet`
        WHERE
            execution_date IS NOT NULL
            AND execution_date >= %(from_date)s
            AND execution_date <= %(to_date)s
        GROUP BY
            furnace_code,
            internal_process
        """,
        {"from_date": from_date, "to_date": to_date},
        as_dict=True,
    )

    units_data = {p: {fc: 0.0 for fc in furnace_codes} for p in process_names}
    for row in units_raw:
        fc = row["furnace_code"]
        proc = row["internal_process"]
        if fc in furnace_codes and proc in units_data:
            val = float(row["total_units"] or 0)
            if val > 0:
                units_data[proc][fc] += val

    # ----------------------------------------------------------------
    # 3. HRS — actual_end_date_time - actual_start_date_time
    # ----------------------------------------------------------------
    hrs_raw = frappe.db.sql(
        """
        SELECT
            furnace_code,
            internal_process,
            actual_start_date_time,
            actual_end_date_time
        FROM
            `tabJob Execution Logsheet`
        WHERE
            actual_start_date_time IS NOT NULL
            AND actual_end_date_time IS NOT NULL
            AND actual_start_date_time >= %(from_date)s
            AND actual_start_date_time <= %(to_date_end)s
        """,
        {
            "from_date": from_date + " 00:00:00",
            "to_date_end": to_date + " 23:59:59",
        },
        as_dict=True,
    )

    hrs_data = {p: {fc: 0 for fc in furnace_codes} for p in process_names}
    for row in hrs_raw:
        fc = row["furnace_code"]
        proc = row["internal_process"]
        if fc not in furnace_codes or proc not in hrs_data:
            continue

        start_dt = row["actual_start_date_time"]
        end_dt = row["actual_end_date_time"]

        if isinstance(start_dt, str):
            start_dt = datetime.strptime(start_dt, "%Y-%m-%d %H:%M:%S")
        if isinstance(end_dt, str):
            end_dt = datetime.strptime(end_dt, "%Y-%m-%d %H:%M:%S")

        secs = (end_dt - start_dt).total_seconds()
        if secs > 0:
            hrs_data[proc][fc] += int(secs)

    def secs_to_hms(seconds):
        seconds = int(seconds)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    # ----------------------------------------------------------------
    # Build result rows
    # ----------------------------------------------------------------
    result = []

    # Subheader row — just KGS / UNITS / HRS / VALUE (RS.) without furnace
    # (furnace code is already in column header above)
    subheader = {"process_label": ""}
    for fc in furnace_codes:
        fc_scrub = frappe.scrub(fc)
        subheader[f"{fc_scrub}__kgs"] = "KGS"
        subheader[f"{fc_scrub}__units"] = "UNITS"
        subheader[f"{fc_scrub}__hrs"] = "HRS"
        subheader[f"{fc_scrub}__value"] = "VALUE (RS.)"
    result.append(subheader)

    # One row per internal process
    for proc in process_names:
        row = {"process_label": proc}
        for fc in furnace_codes:
            fc_scrub = frappe.scrub(fc)
            kgs = kgs_data[proc].get(fc, 0.0)
            units = units_data[proc].get(fc, 0.0)
            hrs_secs = hrs_data[proc].get(fc, 0)

            row[f"{fc_scrub}__kgs"] = f"{kgs:.1f}"
            row[f"{fc_scrub}__units"] = f"{units:.1f}"
            row[f"{fc_scrub}__hrs"] = secs_to_hms(hrs_secs)
            row[f"{fc_scrub}__value"] = ""  # blank for now
        result.append(row)

    return columns, result