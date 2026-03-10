frappe.query_reports["MRN Work-in Progress Status"] = {
    filters: [
        {
            fieldname: "mrn_no",
            label: "MRN No",
            fieldtype: "Link",
            options: "Customer DC"
        }
    ]
};