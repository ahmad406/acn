import frappe
from frappe.utils import getdate


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {"label": "Customer Name", "fieldname": "customer_name", "width": 250},
        {"label": "MRN Date", "fieldname": "tran_date", "fieldtype": "Date", "width": 120},
        {"label": "MRN No", "fieldname": "mrn_no", "width": 200},

        {"label": "Party DC No", "fieldname": "party_dc_no", "width": 150},
        {"label": "Process", "fieldname": "process", "width": 220},
        {"label": "Item Name", "fieldname": "item_name", "width": 200},
        {"label": "Part Number", "fieldname": "part_number", "width": 180},

        {"label": "Received Qty (Nos)", "fieldname": "received_qty_nos",
         "fieldtype": "Float", "width": 150},

        {"label": "Received Qty (Kgs)", "fieldname": "received_qty_kgs",
         "fieldtype": "Float", "width": 150},

        {"label": "Pending Qty (Nos)", "fieldname": "pending_qty_nos",
         "fieldtype": "Float", "width": 150},

        {"label": "Pending Qty (Kgs)", "fieldname": "pending_qty_kgs",
         "fieldtype": "Float", "width": 150},
    ]

def get_data(filters):

    conditions = ""

    if filters.get("customer"):
        conditions += " AND dc.customer = %(customer)s"

    if filters.get("from_date"):
        conditions += " AND dc.tran_date >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " AND dc.tran_date <= %(to_date)s"

    query = f"""
        SELECT
            dc.customer_name,
            dc.tran_date,
            dc.name AS mrn_no,

            dcc.customer_dc_no AS party_dc_no,
            dcc.process_name AS process,
            dcc.item_name,
            dcc.part_no AS part_number,

            dcc.qty_nos AS received_qty_nos,
            dcc.qty_kgs AS received_qty_kgs,

            (IFNULL(dcc.qty_nos,0) - IFNULL(sii.dispatched_nos,0)) AS pending_qty_nos,
            (IFNULL(dcc.qty_kgs,0) - IFNULL(sii.dispatched_kgs,0)) AS pending_qty_kgs

        FROM `tabCustomer DC` dc

        INNER JOIN `tabCustomer DC child` dcc
            ON dcc.parent = dc.name

        -- Aggregate dispatched qty
        LEFT JOIN (
            SELECT
                customer_dc_id,
                part_no,
                SUM(IFNULL(d_qty_in_nos,0)) AS dispatched_nos,
                SUM(IFNULL(d_qty_in_kgs,0)) AS dispatched_kgs
            FROM `tabSales Invoice Item`
            WHERE docstatus = 1
            GROUP BY customer_dc_id, part_no
        ) sii
            ON sii.customer_dc_id = dc.name
            AND sii.part_no = dcc.part_no

        WHERE
            dc.docstatus = 1
            AND (
                (IFNULL(dcc.qty_nos,0) - IFNULL(sii.dispatched_nos,0)) > 0
                OR
                (IFNULL(dcc.qty_kgs,0) - IFNULL(sii.dispatched_kgs,0)) > 0
            )
            {conditions}

        ORDER BY dc.tran_date DESC, dc.name DESC
    """

    return frappe.db.sql(query, filters, as_dict=True)