// Copyright (c) 2025, Ahmad Sayyed and contributors
// For license information, please see license.txt

frappe.query_reports["Sub Account wise Expense List"] = {
	 "filters": [
        {
            "fieldname": "company",
            "label": "Company",
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 1,
            "default": frappe.defaults.get_user_default("Company")
        },
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "account",
            "label": "Account",
            "fieldtype": "Link",
            "options": "Account"
        },
        {
            "fieldname": "sub_account",
            "label": "Sub Account",
            "fieldtype": "Data"
        }
    ]
};