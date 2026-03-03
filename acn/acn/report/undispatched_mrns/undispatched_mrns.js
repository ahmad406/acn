// Copyright (c) 2026, Ahmad Sayyed and contributors

frappe.query_reports["Undispatched MRNs"] = {
    filters: [

        {
            fieldname: "customer",
            label: "Customer",
            fieldtype: "Link",
            options: "Customer",
            reqd: 0
        },

        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            reqd: 1,
        },

        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            reqd: 1,
        }

    ]
};