import frappe
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Data", "width": 250},
        {"label": "Territory", "fieldname": "territory", "fieldtype": "Data", "width": 100},
        {"label": "Market Segment", "fieldname": "market_segment", "fieldtype": "Data", "width": 100},
        {"label": "Process", "fieldname": "process", "fieldtype": "Data", "width": 300},
        {"label": "Qty (Nos)", "fieldname": "qty_nos", "fieldtype": "Float", "width": 150},
        {"label": "Qty (Kgs)", "fieldname": "qty_kgs", "fieldtype": "Float", "width": 150},
        {"label": "Amount Excl GST", "fieldname": "amount", "fieldtype": "Currency", "width": 200},
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

    rows = frappe.db.sql(
        f"""
        SELECT
            si.customer,
            c.territory,
            c.market_segment,
            sii.process_name AS process,
            SUM(sii.d_qty_in_nos) AS qty_nos,
            SUM(sii.d_qty_in_kgs) AS qty_kgs,
            SUM(sii.base_net_amount) AS amount
        FROM `tabSales Invoice Item` sii
        INNER JOIN `tabSales Invoice` si
            ON si.name = sii.parent
        LEFT JOIN `tabCustomer` c
            ON c.name = si.customer
        WHERE
            si.docstatus = 1
            AND si.is_return = 0
            {conditions}
        GROUP BY
            si.customer,
            c.territory,
            c.market_segment,
            sii.process_name
        ORDER BY
            si.customer,
            sii.process_name
        """,
        values,
        as_dict=True,
    )

    data = []
    current_customer = None
    total_nos = 0
    total_kgs = 0
    total_amount = 0
    territory = ""
    market_segment = ""

    for r in rows:

        if current_customer != r.customer:

            # finalize previous customer total row
            if current_customer is not None:
                data.append({
                    "customer": f"{current_customer} Total",
                    "territory": "",
                    "market_segment": "",
                    "process": "<b>TOTAL</b>",
                    "qty_nos": flt(total_nos),
                    "qty_kgs": flt(total_kgs),
                    "amount": flt(total_amount),
                    "bold": 1,
                })

            # reset
            total_nos = 0
            total_kgs = 0
            total_amount = 0
            current_customer = r.customer
            territory = r.territory or ""
            market_segment = r.market_segment or ""

        # accumulate
        total_nos += flt(r.qty_nos)
        total_kgs += flt(r.qty_kgs)
        total_amount += flt(r.amount)

        # detail row
        data.append({
            "customer": r.customer,
            "territory": r.territory or "",
            "market_segment": r.market_segment or "",
            "process": r.process,
            "qty_nos": flt(r.qty_nos),
            "qty_kgs": flt(r.qty_kgs),
            "amount": flt(r.amount),
        })

    # finalize last customer total
    if current_customer is not None:
        data.append({
            "customer": f"{current_customer} Total",
            "territory": "",
            "market_segment": "",
            "process": "<b>TOTAL</b>",
            "qty_nos": flt(total_nos),
            "qty_kgs": flt(total_kgs),
            "amount": flt(total_amount),
            "bold": 1,
        })

    return data