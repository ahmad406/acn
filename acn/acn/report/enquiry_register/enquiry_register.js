frappe.query_reports["Enquiry Register"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_start(),
            "reqd": 0
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 0
        }
    ],
     onload: function(report) {
        report.page.add_inner_button("Export With Summary", function () {
            const filters = report.get_values();

            const query = new URLSearchParams({
                cmd: "acn.acn.report.enquiry_register.enquiry_register.export_with_summary",
                filters: JSON.stringify(filters)
            });

            window.location.href = "/api/method?" + query.toString();
        });
    },
};