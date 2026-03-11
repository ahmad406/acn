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
            "customer_dc",
            "customer_name",
            "item_name"
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
                jps.internal_process_for,
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
                "process_for":p.internal_process_for,
                "nos": p.planned_qty_in_nos or 0,
                "kgs": p.planned_qty_in_kgs or 0
            })

    lot_rows = frappe.get_all(
        "Sequence Lot wise Internal Process",
        filters={"parent": ["in", jc_ids]},
        fields=["parent", "lot_no", "internal_process"],
        order_by="lot_no asc"
    )

    lot_map = {}

    for r in lot_rows:
        lot_map.setdefault(r.parent, []).append(r)
    

    executed_map = {}

    if jc_ids:
        executed_data = frappe.db.sql("""
            SELECT
                jel.name AS executed_id,
                jel.job_plan_id,
                jel.internal_process,
                jec.job_card_id,
                jec.part_no,
                jec.planned_qty_in_nos,
                jec.planned_qty_in_kgs
            FROM `tabJob Execution Logsheet` jel
            JOIN `tabJob Execution Logsheet child` jec
                ON jec.parent = jel.name
            WHERE jec.job_card_id IN %(jc_ids)s
        """, {"jc_ids": jc_ids}, as_dict=True)

        for e in executed_data:
            key = (e.job_card_id, e.part_no, e.internal_process, e.job_plan_id) 

            executed_map[key] = {
                "executed_id": e.executed_id,
                "nos": e.planned_qty_in_nos or 0,
                "kgs": e.planned_qty_in_kgs or 0
            }   

    lab_map = {}

    if jc_ids:
        lab_data = frappe.db.sql("""
            SELECT
                lie.name AS executed_id,
                lie.job_plan_id,
                iqd.job_card_id,
                iqd.part_no,
                iqd.accepted_qty_in_nos,
                iqd.accepted_qty_in_kgs
            FROM `tabLab Inspection Entry` lie
            JOIN `tabInspection Qty Details` iqd
                ON iqd.parent = lie.name
            WHERE iqd.job_card_id IN %(jc_ids)s
        """, {"jc_ids": jc_ids}, as_dict=True)
    
        for l in lab_data:
            key = (l.job_card_id, l.part_no, l.job_plan_id)
    
            lab_map[key] = {
                "executed_id": l.executed_id,
                "nos": l.accepted_qty_in_nos or 0,
                "kgs": l.accepted_qty_in_kgs or 0
            }

    for jc in job_cards:

        dispatch = dispatch_map.get((jc.customer_dc, jc.part_no), {})

        desp_nos = dispatch.get("desp_nos", 0)
        desp_kgs = dispatch.get("desp_kgs", 0)

        # Parent Row (Dropdown)
        data.append({
            "mrn_no": f"<b>{jc.customer_dc}</b>",
            "customer_name": f"<b>{jc.customer_name}</b>",
            "item_name": f"<b>{jc.item_name}</b>",
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
            "customer_name": "",
            "item_name": "",
            "part_no": "",
            "mrn_no":"",
            "jc_no": "<b>Lot</b>",
            "process": "<b>Internal Process</b>",
            "qty_nos": "<b>Planned ID / Nos / Kgs</b>",
            "qty_kgs": "<b>Executed ID / Nos / Kgs</b>",
            "desp_nos": "",
            "desp_kgs": "",
            "indent": 1
        })

        child_rows = lot_map.get(jc.name, [])

        for ch in child_rows:

            planned_list = planned_map.get((jc.name, jc.part_no, ch.internal_process), [])
            
            max_rows = max(len(planned_list), 1)
            
            for i in range(max_rows):
            
                planned_text = ""
                executed_text = ""
            
                if i < len(planned_list):
                    p = planned_list[i]
                    planned_text = f"{p['planned_id']} / {p['nos']} / {p['kgs']}"

                    exec_key = (
                        jc.name,
                        jc.part_no,
                        ch.internal_process,
                        p["planned_id"]
                    )

                    e = None

                    if p["process_for"] == "Lab Inspection":
                        lab_key = (
                            jc.name,
                            jc.part_no,
                            p["planned_id"]
                        )
                        e = lab_map.get(lab_key)

                    else:
                        exec_key = (
                            jc.name,
                            jc.part_no,
                            ch.internal_process,
                            p["planned_id"]
                        )
                        e = executed_map.get(exec_key)

                    if e:
                        executed_text = f"{e['executed_id']} / {e['nos']} / {e['kgs']}"
            
                data.append({
                    "customer_name": "",
                    "item_name": "",
                    "part_no": "",
                    "mrn_no": "",
                    "jc_no": ch.lot_no if i == 0 else "",
                    "process": ch.internal_process if i == 0 else "",
                    "qty_nos": planned_text,
                    "qty_kgs": executed_text,
                    "desp_nos": "",
                    "desp_kgs": "",
                    "indent": 1 if i == 0 else 2
                })

    return columns, data


def get_columns():
    return [
        {"label": "Customer Name", "fieldname": "customer_name", "width": 250},
        {"label": "Part Name", "fieldname": "item_name", "width": 160},
        {"label": "Part No.", "fieldname": "part_no", "width": 160},
        {"label": "MRN No.", "fieldname": "mrn_no", "width": 160},
        {"label": "JC No.", "fieldname": "jc_no", "width": 180},
        {"label": "Process", "fieldname": "process", "width": 250},
        {"label": "Qty Nos", "fieldname": "qty_nos", "width": 280},
        {"label": "Qty Kgs", "fieldname": "qty_kgs", "width": 280},
        {"label": "Desp Nos", "fieldname": "desp_nos", "width": 130},
        {"label": "Desp Kgs", "fieldname": "desp_kgs", "width": 130},
    ]