# Copyright (c) 2026, Ahmad Sayyed and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_data(filters):

    conditions = ""

    if filters.get("company"):
        conditions += " AND dc.company = '{0}' ".format(filters.get("company"))

    if filters.get("customer_dc"):
        conditions += " AND dc.name = '{0}' ".format(filters.get("customer_dc"))

    if filters.get("customer"):
        conditions += " AND dc.customer = '{0}' ".format(filters.get("customer"))

    if filters.get("from_date") and filters.get("to_date"):
        conditions += """
            AND dc.tran_date BETWEEN '{0}' AND '{1}'
        """.format(filters.get("from_date"), filters.get("to_date"))

    query = f"""
        SELECT
            dc.customer AS `Party Name`,
            dc.tran_date AS `MRN Date`,
            dc.name AS `MRN No`,
            jc.job_card_id AS `Job Card ID`,
            dci.customer_dc_no AS `Party DC No`,
            dci.process_name AS `Process`,
            dci.item_name AS `Item`,
            dci.part_no AS `Part Number`,
            dci.material AS `Material`,
            dci.qty_nos AS `Rec.Qty-Nos`,
            dci.qty_kgs AS `Rec.Qty-Kgs`,

            dn.posting_date AS `Despatch Date`,
            dn.name AS `Despatch No.`,
            dn.ewaybill AS `e-Way Bill No.`,

            dni.d_qty_in_nos AS `Despatch Qty-Nos`,
            dni.d_qty_in_kgs AS `Despatch Qty-Kgs`,

            inv.invoice_date AS `Invoice Date`,
            inv.invoice_no AS `Invoice No.`,
            inv.irn AS `IRN`,

            (
                dci.qty_nos -
                IFNULL(dispatch_total.total_nos, 0)
            ) AS `Pending Qty-Nos`,

            (
                dci.qty_kgs -
                IFNULL(dispatch_total.total_kgs, 0)
            ) AS `Pending Qty-Kgs`

        FROM `tabCustomer DC` dc

        LEFT JOIN `tabCustomer DC child` dci
            ON dci.parent = dc.name

        -- ✅ Aggregate Job Card (prevents duplication)
        LEFT JOIN (
            SELECT
                customer_dc_id,
                part_no,
                MAX(job_card_id) AS job_card_id
            FROM `tabJob Card details`
            GROUP BY customer_dc_id, part_no
        ) jc
            ON jc.customer_dc_id = dc.name
            AND jc.part_no = dci.part_no

        LEFT JOIN `tabDelivery Note Item` dni
            ON dni.customer_dc_id = dc.name
            AND dni.part_no = dci.part_no

        LEFT JOIN `tabDelivery Note` dn
            ON dn.name = dni.parent
            AND dn.docstatus = 1

        -- ✅ Aggregate Invoice (prevents duplication)
        LEFT JOIN (
            SELECT
                sii.delivery_note,
                MAX(si.posting_date) AS invoice_date,
                MAX(si.name) AS invoice_no,
                MAX(si.irn) AS irn
            FROM `tabSales Invoice Item` sii
            INNER JOIN `tabSales Invoice` si
                ON si.name = sii.parent
                AND si.docstatus = 1
            GROUP BY sii.delivery_note
        ) inv
            ON inv.delivery_note = dn.name

        -- ✅ Aggregate Dispatch Totals (fast pending calc)
        LEFT JOIN (
            SELECT
                dni2.customer_dc_id,
                dni2.part_no,
                SUM(dni2.d_qty_in_nos) AS total_nos,
                SUM(dni2.d_qty_in_kgs) AS total_kgs
            FROM `tabDelivery Note Item` dni2
            INNER JOIN `tabDelivery Note` dn2
                ON dn2.name = dni2.parent
                AND dn2.docstatus = 1
            GROUP BY dni2.customer_dc_id, dni2.part_no
        ) dispatch_total
            ON dispatch_total.customer_dc_id = dc.name
            AND dispatch_total.part_no = dci.part_no

        WHERE 1=1
        {conditions}

        ORDER BY dc.tran_date ASC, dn.posting_date ASC
    """

    return frappe.db.sql(query, as_dict=True)


def get_columns():

    return [

        {"label": "Party Name", "fieldname": "Party Name", "fieldtype": "Data", "width": 220},
        {"label": "MRN Date", "fieldname": "MRN Date", "fieldtype": "Date", "width": 120},
        {"label": "MRN No", "fieldname": "MRN No", "fieldtype": "Data", "width": 170},
        {"label": "Job Card ID", "fieldname": "Job Card ID", "fieldtype": "Data", "width": 150},
        {"label": "Party DC No.", "fieldname": "Party DC No", "fieldtype": "Data", "width": 130},

        {"label": "Process", "fieldname": "Process", "fieldtype": "Data", "width": 220},
        {"label": "Item", "fieldname": "Item", "fieldtype": "Data", "width": 200},
        {"label": "Part Number", "fieldname": "Part Number", "fieldtype": "Data", "width": 150},
        {"label": "Material", "fieldname": "Material", "fieldtype": "Data", "width": 130},

        {"label": "Rec.Qty-Nos", "fieldname": "Rec.Qty-Nos", "fieldtype": "Float", "width": 140},
        {"label": "Rec.Qty-Kgs", "fieldname": "Rec.Qty-Kgs", "fieldtype": "Float", "width": 140},

        {"label": "Despatch Date", "fieldname": "Despatch Date", "fieldtype": "Date", "width": 130},
        {"label": "Despatch No.", "fieldname": "Despatch No.", "fieldtype": "Data", "width": 170},
        {"label": "e-Way Bill No.", "fieldname": "e-Way Bill No.", "fieldtype": "Data", "width": 160},

        {"label": "Despatch Qty-Nos", "fieldname": "Despatch Qty-Nos", "fieldtype": "Float", "width": 160},
        {"label": "Despatch Qty-Kgs", "fieldname": "Despatch Qty-Kgs", "fieldtype": "Float", "width": 160},

        {"label": "Invoice Date", "fieldname": "Invoice Date", "fieldtype": "Date", "width": 130},
        {"label": "Invoice No.", "fieldname": "Invoice No.", "fieldtype": "Data", "width": 170},
        {"label": "IRN", "fieldname": "IRN", "fieldtype": "Data", "width": 250},

        {"label": "Pending Qty-Nos", "fieldname": "Pending Qty-Nos", "fieldtype": "Float", "width": 170},
        {"label": "Pending Qty-Kgs", "fieldname": "Pending Qty-Kgs", "fieldtype": "Float", "width": 170},
    ]