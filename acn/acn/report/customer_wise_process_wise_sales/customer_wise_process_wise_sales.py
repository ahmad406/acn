import frappe
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Process", "fieldname": "process", "width": 400},
        {"label": "Qty (Nos)", "fieldname": "qty_nos", "fieldtype": "Float", "width": 200},
        {"label": "Qty (Kgs)", "fieldname": "qty_kgs", "fieldtype": "Float", "width": 200},
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

    if filters.get("customer"):
        conditions += " AND si.customer = %(customer)s"
        values["customer"] = filters.get("customer")

    rows = frappe.db.sql(
        f"""
        SELECT
            si.customer,
            sii.process_name AS process,
            SUM(sii.d_qty_in_nos) AS qty_nos,
            SUM(sii.d_qty_in_kgs) AS qty_kgs,
            SUM(sii.base_net_amount) AS amount
        FROM `tabSales Invoice Item` sii
        INNER JOIN `tabSales Invoice` si
            ON si.name = sii.parent
        WHERE
            si.docstatus = 1
            AND si.is_return = 0
            {conditions}
        GROUP BY
            si.customer,
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
    customer_row_index = None

    # running totals
    total_nos = 0
    total_kgs = 0
    total_amount = 0

    for r in rows:

        # when customer changes → finalize previous totals
        if current_customer != r.customer:

            # update previous customer totals
            if customer_row_index is not None:
                data[customer_row_index]["qty_nos"] = flt(total_nos)
                data[customer_row_index]["qty_kgs"] = flt(total_kgs)
                data[customer_row_index]["amount"] = flt(total_amount)

            # reset totals
            total_nos = 0
            total_kgs = 0
            total_amount = 0

            current_customer = r.customer

            # add customer header row
            data.append({
                "process": current_customer,
                "indent": 0,
                "is_group": 1,
                 "is_customer_total": 1, 
                "qty_nos": 0,
                "qty_kgs": 0,
                "amount": 0,
            })

            customer_row_index = len(data) - 1

        # accumulate totals
        total_nos += flt(r.qty_nos)
        total_kgs += flt(r.qty_kgs)
        total_amount += flt(r.amount)

        # child row
        data.append({
            "process": r.process,
            "qty_nos": flt(r.qty_nos),
            "qty_kgs": flt(r.qty_kgs),
            "amount": flt(r.amount),
            "indent": 1,
        })

    # finalize last customer
    if customer_row_index is not None:
        data[customer_row_index]["qty_nos"] = flt(total_nos)
        data[customer_row_index]["qty_kgs"] = flt(total_kgs)
        data[customer_row_index]["amount"] = flt(total_amount)

    return data