import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": _("Planning ID"), "fieldname": "planning_id", "fieldtype": "Link", "options": "Job Plan Scheduler", "width": 150},
        {"label": _("Inspection"), "fieldname": "inspection", "fieldtype": "Data", "width":200},
        {"label": _("Planning Date"), "fieldname": "planning_date", "fieldtype": "Date", "width": 120},

        {"label": _("MRN No"), "fieldname": "mrn_no", "fieldtype": "Data", "width": 150},
        {"label": _("Job Card No"), "fieldname": "job_card_no", "fieldtype": "Data", "width": 180},
        {"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 200},

        {"label": _("Item Description"), "fieldname": "item_description", "fieldtype": "Data", "width": 200},
        {"label": _("Part Number"), "fieldname": "part_number", "fieldtype": "Data", "width": 140},

        {"label": _("Material"), "fieldname": "material", "fieldtype": "Data", "width": 120},
        {"label": _("Process"), "fieldname": "process", "fieldtype": "Data", "width": 160},

        {"label": _("Qty (Nos)"), "fieldname": "qty_nos", "fieldtype": "Float", "width": 120},
        {"label": _("Qty (Kgs)"), "fieldname": "qty_kgs", "fieldtype": "Float", "width": 120},

        {"label": _("Shift"), "fieldname": "shift", "fieldtype": "Data", "width": 100},
        {"label": _("Person Name"), "fieldname": "person_name", "fieldtype": "Data", "width": 160},
        {"label": _("Job Loading Plan Date"), "fieldname": "date", "fieldtype": "Datetime", "width":200},
        {"label": _("TC No."), "fieldname": "tc_no", "fieldtype": "Link", "options": "Test Certificate entry", "width": 180},
        {"label": _("Previous Internal Process"), "fieldname": "previous_internal_process", "fieldtype": "Data", "width": 220},
        {"label": _("Previous Process Status"), "fieldname": "previous_process_status", "fieldtype": "Data", "width": 180},
        {"label": _("Checked Date"), "fieldname": "checked_date", "fieldtype": "Date", "width": 160},
        {"label": _("Checked By (User)"), "fieldname": "checked_by", "fieldtype": "Data", "width":200},
        {"label": _("Reason For Delay In Checking"), "fieldname": "reason", "fieldtype": "Data", "width":500},
    ]


def get_data(filters):
    conditions = ""

    if filters.get("from_date") and filters.get("to_date"):
        conditions += """
            AND DATE(jps.job_loading_plan_date)
            BETWEEN %(from_date)s AND %(to_date)s
        """

    if filters.get("internal_process"):
        conditions += """
            AND jps.internal_process = %(internal_process)s
        """

    internal_process_for = filters.get("internal_process_for", "Lab Inspection")

    data = frappe.db.sql(f"""
    SELECT
        jps.name AS planning_id,
        jps.internal_process AS inspection,
        DATE(jps.job_loading_plan_date) AS planning_date,

        jcd.customer_dc_id AS mrn_no,
        jcd.job_card_id AS job_card_no,
        jcd.customer_name AS customer_name,

        jcd.item_name AS item_description,
        jcd.part_no AS part_number,

        jcd.material AS material,
        jcd.process_name AS process,

        jcd.planned_qty_in_nos AS qty_nos,
        jcd.planned_qty_in_kgs AS qty_kgs,

        jps.shift AS shift,
        jps.lab_inspection_by AS person_name,
        jps.job_loading_plan_date AS date,

        DATE(lie.actual_start_date_time) AS checked_date,
        lie.checked_by AS checked_by,
        lie.tc_no AS tc_no,

        lie.reason_for_delay_in_checking AS reason

        FROM `tabJob Plan Scheduler` jps

        JOIN `tabJob Card details` jcd
            ON jcd.parent = jps.name

        LEFT JOIN (
            SELECT 
                lie.name,
                lie.job_plan_id,
                lie.reason_for_delay_in_checking,
                lie.actual_start_date_time,
                tce.checked_by,
                tce.name AS tc_no
            FROM `tabLab Inspection Entry` lie
            LEFT JOIN `tabTest Certificate entry` tce
                ON tce.lab_inspection_id = lie.name
            WHERE lie.docstatus < 2
        ) lie ON lie.job_plan_id = jps.name

        WHERE 
            jps.docstatus = 1
            AND (%(internal_process_for)s = '' 
                 OR LOWER(jps.internal_process_for) = LOWER(%(internal_process_for)s))
            {conditions}

        ORDER BY jps.job_loading_plan_date DESC, jps.name
        """, {
            "from_date": filters.get("from_date"),
            "to_date": filters.get("to_date"),
            "internal_process_for": internal_process_for,
            "internal_process": filters.get("internal_process") or "",
        }, as_dict=1)


    for row in data:

        previous_process = ""

        sequence_rows = frappe.get_all(
            "Sequence Lot wise Internal Process",
            filters={
                "parent": row.job_card_no
            },
            fields=[
                "idx",
                "internal_process"
            ],
            order_by="idx asc"
        )

        current_index = None

        for i, seq in enumerate(sequence_rows):
            if (seq.internal_process or "").strip().lower() == (row.inspection or "").strip().lower():
                current_index = i
                break

        # previous row process
        if current_index is not None and current_index > 0:
            previous_process = sequence_rows[current_index - 1].internal_process

        row["previous_internal_process"] = previous_process or ""

        # default status
        row["previous_process_status"] = "Not Processed"

        if previous_process:

            processed = frappe.db.sql("""
                SELECT jels.name
                FROM `tabJob Execution Logsheet child` jelsc
                INNER JOIN `tabJob Execution Logsheet` jels
                    ON jels.name = jelsc.parent
                WHERE
                    jels.docstatus = 1
                    AND jels.internal_process = %s
                    AND jelsc.job_card_id = %s
                LIMIT 1
            """, (previous_process, row.job_card_no))
        
            if processed:
                row["previous_process_status"] = "Processed"

    # ── process_status filter (applied after loop since value is computed) ──
    process_status = filters.get("process_status")
    if process_status:
        data = [r for r in data if r.get("previous_process_status") == process_status]

    return data