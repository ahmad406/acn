// Copyright (c) 2026, Ahmad Sayyed and contributors
// For license information, please see license.txt

frappe.query_reports["Customer Wise Process Wise Sales"] = {
	tree: true,
	name_field: "process",
	parent_field: "parent_customer",
	initial_depth: 1,
	filters: [
		{
			fieldname: "from_date",
			label: "From Date",
			fieldtype: "Date",
			reqd: 1
		},
		{
			fieldname: "to_date",
			label: "To Date",
			fieldtype: "Date",
			reqd: 1
		},
		{
			fieldname: "customer",
			label: "Customer",
			fieldtype: "Link",
			options: "Customer"
		}
	]
	,
	  formatter: function(value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        // Make customer total row bold
        if (data && data.is_customer_total) {
            value = `<span style="font-weight:800;">${value}</span>`;
        }

        return value;
    }
};
