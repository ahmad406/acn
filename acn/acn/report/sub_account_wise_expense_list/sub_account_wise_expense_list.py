import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    processed_data = process_data(data)
    return columns, processed_data

def get_columns():
    return [
        {"label": "Account", "fieldname": "account", "fieldtype": "Link", "options": "Account", "width": 320},
        {"label": "Sub Account", "fieldname": "sub_account", "fieldtype": "Data", "width": 260},
        {"label": "Total Debit Amount", "fieldname": "debit_amount", "fieldtype": "Currency", "width": 220},
    ]

def get_data(filters):
    conditions = ["IFNULL(sub_account, '') != ''"]
    if filters.get("company"):
        conditions.append("company = %(company)s")
    if filters.get("from_date"):
        conditions.append("posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("posting_date <= %(to_date)s")
    if filters.get("account"):
        conditions.append("account = %(account)s")
    if filters.get("sub_account"):
        conditions.append("sub_account = %(sub_account)s")
    if filters.get("cost_center"):
        conditions.append("cost_center = %(cost_center)s")

    where_clause = " AND ".join(conditions)
    query = f"""
        SELECT
            company,
            account,
            sub_account,
            SUM(debit) as debit_amount
        FROM
            `tabGL Entry`
        WHERE
            {where_clause if where_clause else "1=1"}
        GROUP BY
            company, account, sub_account
        ORDER BY
            company, account, sub_account
    """
    return frappe.db.sql(query, filters, as_dict=True)

def process_data(data):
    if not data:
        return []
    
    processed_data = []
    current_account = None
    account_total = 0
    grand_total = 0
    
    for row in data:
        if current_account != row.account:
            if current_account is not None:
                processed_data.append({
                     "account":current_account,
                    "sub_account": "<strong>Sub Total</strong>",
                    "debit_amount": account_total,
                })
            
            current_account = row.account
            account_total = 0
        
        processed_data.append(row)
        account_total += flt(row.debit_amount)
        grand_total += flt(row.debit_amount)
    
    if current_account is not None:
        processed_data.append({
            "account":current_account,
            "sub_account": "<strong>Total</strong>",
            "debit_amount": account_total,
        })
    
    processed_data.append({
        "account": "",
        "sub_account": "<strong>Grand Total</strong>",
        "debit_amount": grand_total,
    })
    
    return processed_data