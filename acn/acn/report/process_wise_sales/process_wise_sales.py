import frappe
from frappe.utils import flt


def execute(filters=None):

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {
            "label": "Process",
            "fieldname": "process",
            "fieldtype": "Data",
            "width": 400,
        },
        {
            "label": "Qty Dispatched (Nos)",
            "fieldname": "qty_nos",
            "fieldtype": "Float",
            "width": 240,
        },
        {
            "label": "Qty Dispatched (Kgs)",
            "fieldname": "qty_weight",
            "fieldtype": "Float",
            "width": 240,
        },
        {
            "label": "Sales Gross Amount (Excluding GST)",
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 300,
        },
    ]


def get_data(filters):

    conditions = ""
    values = {}

    if filters.get("from_date"):
        conditions += " AND si.posting_date >= %(from_date)s"
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions += " AND si.posting_date <= %(to_date)s"
        values["to_date"] = filters.get("to_date")

    data = frappe.db.sql(
        f"""
        SELECT
            sii.process_name AS process,

            SUM(sii.d_qty_in_nos) AS qty_nos,
            SUM(sii.d_qty_in_kgs) AS qty_weight,

            SUM(sii.amount) AS amount

        FROM `tabSales Invoice Item` sii
        INNER JOIN `tabSales Invoice` si
            ON si.name = sii.parent

        WHERE
            si.docstatus = 1
            {conditions}

        GROUP BY sii.process_name
        ORDER BY sii.process_name
        """,
        values,
        as_dict=True,
    )

    return data