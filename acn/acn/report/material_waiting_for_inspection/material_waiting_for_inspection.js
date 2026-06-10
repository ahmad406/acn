// Copyright (c) 2026, Ahmad Sayyed and contributors
// For license information, please see license.txt

frappe.query_reports["Material Waiting For Inspection"] = {
    filters: [
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date"
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date"
        },
        {
            fieldname: "internal_process",
            label: "Internal Process",
            fieldtype: "Link",
            options: "Internal Process",
            get_query: () => {
                return {
                    filters: {
                        internal_process_for: "Lab Inspection"
                    }
                };
            }
        },
        {
            fieldname: "process_status",
            label: "Process Status",
            fieldtype: "Select",
            options: "\nProcessed\nNot Processed"
        }
    ]
};
