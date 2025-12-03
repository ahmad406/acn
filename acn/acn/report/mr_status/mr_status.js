// Copyright (c) 2025, Ahmad Sayyed and contributors
// For license information, please see license.txt

frappe.query_reports["MR Status"] = {
    "filters": [
		        {
            "fieldname": "company",
            "label": "Company",
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1
        },
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "reqd": 1
        },
        {
            "fieldname": "customer",
            "label": "Customer",
            "fieldtype": "Link",
            "options": "Customer",
            "reqd": 0
        },
        {
            "fieldname": "customer_dc",
            "label": "Customer DC",
            "fieldtype": "Link",
            "options": "Customer DC",
            "reqd": 0
        },
          {
            "fieldname": "furnace_code",
            "label": "Furnace Code",
            "fieldtype": "Link",
            "options": "Furnace",
            "reqd": 0
        }
    ]
};


