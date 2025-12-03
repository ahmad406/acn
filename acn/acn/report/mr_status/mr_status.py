# Copyright (c) 2025, Ahmad Sayyed and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_data(filters):

    # ----------------------------
    #  Dynamic conditions
    # ----------------------------
    cond_customer_dc = ""
    cond_date = ""
    cond_furnace = ""

    if filters.get("customer_dc"):
        cond_customer_dc = " AND dc.name = '{0}' ".format(filters.get("customer_dc"))

    if filters.get("from_date") and filters.get("to_date"):
        cond_date = " AND dc.tran_date BETWEEN '{0}' AND '{1}' ".format(
            filters.get("from_date"), filters.get("to_date")
        )

    if filters.get("furnace_code"):
        cond_furnace = " AND jp.furnace_code = '{0}' ".format(filters.get("furnace_code"))

    # ----------------------------
    #  MAIN QUERY
    # ----------------------------
    query = """
        SELECT  
            dc.name AS `Customer DC ID`,
            dc.customer AS `Customer Name`,
            dc.sales_order_no AS `Sales Order No`,
            dci.part_no AS `Part No`,
            dci.item_name AS `Item Name`,
            dci.process_name AS `Process Name`,
            dci.material,
            dci.customer_dc_no AS `Customer DC No`,
            dc.tran_date AS `Customer DC Date`,
            dci.qty_kgs AS `QTY KGs`,
            dci.qty_nos AS `QTY NOs`,

            jp.name AS `Plan ID`,
            jp.planned_date,
             jp.furnace_code,
            jp.internal_process AS `Internal Process`,
            jp.internal_process_for,
            jpi.planned_qty_in_nos AS `Planned Qty-Nos`,
            jpi.planned_qty_in_kgs AS `Planned Qty-Kgs`,
            jpi.job_card_id AS `Job Card ID`,

            CASE WHEN lie.name IS NULL THEN jel.name END AS `Execution No`,
            CASE WHEN lie.name IS NULL THEN jel.execution_date END AS `Execution Date`,
             CASE WHEN lie.name IS NULL THEN jel.actual_start_date_time END AS `actual_start_date_time`,
                CASE WHEN lie.name IS NULL THEN jel.actual_end_date_time END AS `actual_end_date_time`,
                CASE 
                WHEN lie.name IS NULL 
                    AND jel.actual_start_date_time IS NOT NULL
                    AND jel.actual_end_date_time IS NOT NULL
                THEN TIMEDIFF(jel.actual_end_date_time, jel.actual_start_date_time)
            END AS cycle_time,
            CASE WHEN lie.name IS NULL THEN jpi.planned_qty_in_nos END AS `Executed Qty-Nos`,
            CASE WHEN lie.name IS NULL THEN jpi.planned_qty_in_kgs END AS `Executed Qty-Kgs`,

            CASE WHEN lie.name IS NOT NULL THEN lie.name END AS `Inspection No`,
                CASE WHEN lie.name IS NOT NULL THEN lie.inspection_date END AS `inspection_date`,
            CASE WHEN lie.name IS NOT NULL THEN jpi.planned_qty_in_nos END AS `Inspected Qty-Nos`,
            CASE WHEN lie.name IS NOT NULL THEN jpi.planned_qty_in_kgs END AS `Inspected Qty-Kgs`,

            CASE WHEN lie.name IS NOT NULL AND jp.internal_process LIKE '%FINAL%' THEN tc.name END AS `TC No`,
             CASE  WHEN lie.name IS NOT NULL AND jp.internal_process LIKE '%FINAL%' THEN tc.date END AS `TC Date`,

            CASE WHEN lie.name IS NOT NULL AND jp.internal_process LIKE '%FINAL%' THEN dn.dispatch_no END AS `Dispatch No`,
                    CASE 
        WHEN lie.name IS NOT NULL AND jp.internal_process LIKE '%FINAL%' THEN dn_parent.posting_date
    END AS `dn_date`,
    CASE 
        WHEN lie.name IS NOT NULL AND jp.internal_process LIKE '%FINAL%' THEN dn_parent.ewaybill
    END AS `ewaybill`,

            CASE WHEN lie.name IS NOT NULL AND jp.internal_process LIKE '%FINAL%' THEN dn.dispatch_qty_nos END AS `Dispatch Qty-Nos`,
            CASE WHEN lie.name IS NOT NULL AND jp.internal_process LIKE '%FINAL%' THEN dn.dispatch_qty_kgs END AS `Dispatch Qty-Kgs`,
            CASE WHEN lie.name IS NOT NULL AND jp.internal_process LIKE '%FINAL%' THEN si.invoice_no END AS `Invoice No`,
                CASE 
        WHEN lie.name IS NOT NULL AND jp.internal_process LIKE '%FINAL%' THEN si_parent.posting_date
    END AS `si_date`,

            CASE 
                WHEN lie.name IS NOT NULL 
                    AND jp.internal_process LIKE '%FINAL%'
                    AND tc.name IS NOT NULL
                THEN (dci.qty_nos - IFNULL(dn.dispatch_qty_nos,0))
            END AS `Pending Qty-Nos`,

            CASE 
                WHEN lie.name IS NOT NULL 
                    AND jp.internal_process LIKE '%FINAL%'
                    AND tc.name IS NOT NULL
                THEN (dci.qty_kgs - IFNULL(dn.dispatch_qty_kgs,0))
            END AS `Pending Qty-Kgs`

        FROM `tabJob Plan Scheduler` jp

        LEFT JOIN `tabJob Card details` jpi
            ON jpi.parent = jp.name

        LEFT JOIN `tabCustomer DC` dc
            ON dc.name = jpi.customer_dc_id

        LEFT JOIN `tabCustomer DC child` dci
            ON dci.parent = dc.name
            AND dci.part_no = jpi.part_no
            AND dci.item_name = jpi.item_name

        LEFT JOIN `tabJob Execution Logsheet` jel
            ON jel.job_plan_id = jp.name

        LEFT JOIN `tabLab Inspection Entry` lie
            ON lie.job_plan_id = jp.name

        LEFT JOIN `tabInspection Qty Details` liei
            ON liei.parent = lie.name
            AND liei.item_name = jpi.item_name

        LEFT JOIN `tabTest Certificate entry` tc
            ON tc.customer_dc_id = dc.name
            AND tc.job_card_id = jpi.job_card_id
            AND tc.docstatus = 1

        LEFT JOIN (
            SELECT parent, customer_dc_id, part_no,
                MAX(parent) AS dispatch_no,
                SUM(d_qty_in_nos) AS dispatch_qty_nos,
                SUM(d_qty_in_kgs) AS dispatch_qty_kgs
            FROM `tabDelivery Note Item`
            GROUP BY customer_dc_id, part_no
        ) dn ON dn.customer_dc_id = dc.name
            AND dn.part_no = dci.part_no
        LEFT JOIN `tabDelivery Note` dn_parent
    ON dn_parent.name = dn.dispatch_no

        LEFT JOIN (
            SELECT customer_dc_id, part_no,
                MAX(parent) AS invoice_no
            FROM `tabSales Invoice Item`
            GROUP BY customer_dc_id, part_no
        ) si ON si.customer_dc_id = dc.name
            AND si.part_no = dci.part_no

            LEFT JOIN `tabSales Invoice` si_parent
    ON si_parent.name = si.invoice_no

        WHERE 1=1
        {cond_date}
        {cond_customer_dc}
        {cond_furnace}

        GROUP BY jp.name, jpi.item_name, jpi.part_no, jp.internal_process
        ORDER BY dci.part_no, jp.name
    """.format(
        cond_date=cond_date,
        cond_customer_dc=cond_customer_dc,
        cond_furnace=cond_furnace
    )

    return frappe.db.sql(query, as_dict=True)


def get_columns():
    columns = [

        {"label": "Party Name", "fieldname": "Customer Name", "fieldtype": "Data", "width": 300},
        {"label": "MRN Date", "fieldname": "Customer DC Date", "fieldtype": "Date", "width": 150},
        {"label": "MRN No", "fieldname": "Customer DC ID", "fieldtype": "Data", "width": 180},
        {"label": "Party DC No.", "fieldname": "Customer DC No", "fieldtype": "Data", "width": 120},

        {"label": "Process", "fieldname": "Process Name", "fieldtype": "Data", "width": 140},
        {"label": "Item", "fieldname": "Item Name", "fieldtype": "Data", "width": 180},
        {"label": "Part Number", "fieldname": "Part No", "fieldtype": "Data", "width": 140},
        {"label": "Material", "fieldname": "material", "fieldtype": "Data", "width": 120},

        {"label": "Rec.Qty-Nos", "fieldname": "QTY NOs", "fieldtype": "Float", "width": 120},
        {"label": "Rec.Qty-Kgs", "fieldname": "QTY KGs", "fieldtype": "Float", "width": 120},

        {"label": "Internal Process", "fieldname": "Internal Process", "fieldtype": "Data", "width": 200},
        {"label": "Internal Process for", "fieldname": "internal_process_for", "fieldtype": "Data", "width": 180},

        {"label": "Planned Date", "fieldname": "planned_date", "fieldtype": "Date", "width": 150},
        {"label": "Planned No.", "fieldname": "Plan ID", "fieldtype": "Data", "width": 180},
        {"label": "Furnace", "fieldname": "furnace_code", "fieldtype": "Data", "width": 120},

        {"label": "Planned Qty-Nos", "fieldname": "Planned Qty-Nos", "fieldtype": "Float", "width": 180},
        {"label": "Planned Qty-Kgs", "fieldname": "Planned Qty-Kgs", "fieldtype": "Float", "width": 180},

        {"label": "Executed Date", "fieldname": "Execution Date", "fieldtype": "Date", "width": 150},
        {"label": "Executed No.", "fieldname": "Execution No", "fieldtype": "Data", "width": 180},

        {"label": "Start Date", "fieldname": "actual_start_date_time", "fieldtype": "Datetime", "width": 180},
        {"label": "End Date", "fieldname": "actual_end_date_time", "fieldtype": "Datetime", "width": 180},
        {"label": "Cycle Time", "fieldname": "cycle_time", "fieldtype": "Data", "width": 140},

        {"label": "Executed Qty-Nos", "fieldname": "Executed Qty-Nos", "fieldtype": "Float", "width": 140},
        {"label": "Executed Qty-Kgs", "fieldname": "Executed Qty-Kgs", "fieldtype": "Float", "width": 140},

        {"label": "Inpected Date", "fieldname": "inspection_date", "fieldtype": "Date", "width": 140},
        {"label": "Inpected No.", "fieldname": "Inspection No", "fieldtype": "Data", "width": 160},
        {"label": "Inpected Qty-Nos", "fieldname": "Inspected Qty-Nos", "fieldtype": "Float", "width": 160},
        {"label": "Inpected Qty-Kgs", "fieldname": "Inspected Qty-Kgs", "fieldtype": "Float", "width": 160},

        {"label": "TC Date", "fieldname": "TC Date", "fieldtype": "Date", "width": 180}, 
        {"label": "TC No.", "fieldname": "TC No", "fieldtype": "Data", "width": 160},
        {"label": "Job Card ID", "fieldname": "Job Card ID", "fieldtype": "Data", "width": 160},

        {"label": "Despatch Date", "fieldname": "dl_date", "fieldtype": "Date", "width": 160}, 
        {"label": "Despatch No.", "fieldname": "Dispatch No", "fieldtype": "Data", "width": 180},
        {"label": "e-Way Bill No.", "fieldname": "ewaybill", "fieldtype": "Data", "width": 150},
        {"label": "Despatch Qty-Nos", "fieldname": "Dispatch Qty-Nos", "fieldtype": "Float", "width": 150},
        {"label": "Despatch Qty-Kgs", "fieldname": "Dispatch Qty-Kgs", "fieldtype": "Float", "width": 150},

        {"label": "Invoice Date", "fieldname": "si_Date", "fieldtype": "Date", "width": 180},  
        {"label": "Invoice No.", "fieldname": "Invoice No", "fieldtype": "Data", "width": 180},

        {"label": "Pending Qty-Nos", "fieldname": "Pending Qty-Nos", "fieldtype": "Float", "width": 140},
        {"label": "Pending Qty-Kgs", "fieldname": "Pending Qty-Kgs", "fieldtype": "Float", "width": 140},
    ]

    return columns
