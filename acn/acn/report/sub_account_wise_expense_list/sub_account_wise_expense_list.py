# Copyright (c) 2025, Ahmad Sayyed and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Account", "fieldname": "account", "fieldtype": "Link", "options": "Account", "width": 180},
        {"label": "Sub Account", "fieldname": "sub_account", "fieldtype": "Data", "width": 200},
        {"label": "Total Debit Amount", "fieldname": "debit_amount", "fieldtype": "Currency", "width": 150},
    ]

def get_data(filters):
    conditions = []

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

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT
            company,
            account,
            sub_account,
            SUM(debit) as debit_amount
        FROM
            `tabGL Entry`
        WHERE sub_account is not null
            {where_clause if where_clause else "1=1"}
        GROUP BY
            company, account, sub_account
        ORDER BY
            company, account, sub_account
    """

    return frappe.db.sql(query, filters, as_dict=True)
