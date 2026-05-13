// Copyright (c) 2026, Ahmad Sayyed and contributors
// For license information, please see license.txt
frappe.query_reports["Commitment List"] = {

	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
		},
	],

	onload: function(report) {

		report.page.add_inner_button(
			__("Export With Summary"),
			function () {

				const filters = report.get_values();

				const query = new URLSearchParams({
					cmd: "acn.acn.report.commitment_list.commitment_list.export_with_summary",
					filters: JSON.stringify(filters)
				});

				window.location.href =
					"/api/method?" + query.toString();
			}
		);
	
}
};