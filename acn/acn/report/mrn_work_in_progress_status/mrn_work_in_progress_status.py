import frappe

def execute(filters=None):
    columns = get_columns()
    data = []

    filters_cond = {}

    if filters.get("mrn_no"):
        filters_cond["customer_dc"] = filters.get("mrn_no")

    job_cards = frappe.get_all(
        "Job Card for process",
        filters=filters_cond,
        fields=[
            "name",
            "part_no",
            "process_name",
            "qty_in_nos",
            "qty_in_kgs",
            "customer_dc"
        ],
         order_by="name asc"
    )

    dispatch_map = {}

    dispatch_data = frappe.db.sql("""
        SELECT 
            customer_dc_id,
            part_no,
            SUM(d_qty_in_nos) AS desp_nos,
            SUM(d_qty_in_kgs) AS desp_kgs
        FROM `tabSales Invoice Item`
        WHERE docstatus = 1
        GROUP BY customer_dc_id, part_no
    """, as_dict=True)
    
    for d in dispatch_data:
        dispatch_map[(d.customer_dc_id, d.part_no)] = {
            "desp_nos": d.desp_nos or 0,
            "desp_kgs": d.desp_kgs or 0
        }

    # Collect job card ids
    jc_ids = [jc.name for jc in job_cards]

    planned_map = {}

    if jc_ids:
        planned_data = frappe.db.sql("""
            SELECT
                jps.name AS planned_id,
                jps.internal_process,
                jcd.job_card_id,
                jcd.part_no,
                jcd.planned_qty_in_nos,
                jcd.planned_qty_in_kgs
            FROM `tabJob Plan Scheduler` jps
            JOIN `tabJob Card details` jcd
                ON jcd.parent = jps.name
            WHERE jcd.job_card_id IN %(jc_ids)s
        """, {"jc_ids": jc_ids}, as_dict=True)

        for p in planned_data:
            key = (p.job_card_id, p.part_no, p.internal_process)

            if key not in planned_map:
                planned_map[key] = []
            
            planned_map[key].append({
                "planned_id": p.planned_id,
                "nos": p.planned_qty_in_nos or 0,
                "kgs": p.planned_qty_in_kgs or 0
            })


    for jc in job_cards:

        dispatch = dispatch_map.get((jc.customer_dc, jc.part_no), {})

        desp_nos = dispatch.get("desp_nos", 0)
        desp_kgs = dispatch.get("desp_kgs", 0)

        # Parent Row (Dropdown)
        data.append({
            "mrn_no": f"<b>{jc.customer_dc}</b>",
            "part_no": f"<b>{jc.part_no}</b>",
            "jc_no": f"<b>{jc.name}</b>",
            "process": f"<b>{jc.process_name}</b>",
            "qty_nos": f"<b>{jc.qty_in_nos}</b>",
            "qty_kgs": f"<b>{jc.qty_in_kgs}</b>",
            "desp_nos": f"<b>{desp_nos}</b>",
            "desp_kgs": f"<b>{desp_kgs}</b>",
            "indent": 0
        })

        # Child Header
        data.append({
            "part_no": "",
            "jc_no": "<b>Lot</b>",
            "process": "<b>Internal Process</b>",
            "qty_nos": "<b>Planned ID / Nos / Kgs</b>",
            "qty_kgs": "<b>Executed ID / Nos / Kgs</b>",
            "desp_nos": "",
            "desp_kgs": "",
            "indent": 1
        })

        child_rows = frappe.get_all(
            "Sequence Lot wise Internal Process",
            filters={"parent": jc.name},
            fields=["lot_no", "internal_process"],
            order_by="lot_no asc"
        )

        for ch in child_rows:

            planned_list = planned_map.get((jc.name, jc.part_no, ch.internal_process), [])

            planned_text = ""
            
            if planned_list:
                rows = []
                for p in planned_list:
                    rows.append(f"{p['planned_id']} / {p['nos']} / {p['kgs']}")
                planned_text = "<br>".join(rows)

            data.append({
                "part_no": "",
                "jc_no": ch.lot_no,
                "process": ch.internal_process,
                "qty_nos": planned_text,
                "qty_kgs": "",
                "desp_nos": "",
                "desp_kgs": "",
                "indent": 1
            })

    return columns, data


def get_columns():
    return [
        {"label": "Part No", "fieldname": "part_no", "width": 220},
        {"label": "MRN No", "fieldname": "mrn_no", "width": 160},
        {"label": "JC No", "fieldname": "jc_no", "width": 180},
        {"label": "Process", "fieldname": "process", "width": 250},
        {"label": "Qty Nos", "fieldname": "qty_nos", "width": 200},
        {"label": "Qty Kgs", "fieldname": "qty_kgs", "width": 200},
        {"label": "Desp Nos", "fieldname": "desp_nos", "width": 130},
        {"label": "Desp Kgs", "fieldname": "desp_kgs", "width": 130},
    ]