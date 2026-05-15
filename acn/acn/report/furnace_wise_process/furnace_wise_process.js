frappe.query_reports["Furnace Wise Process"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_end(),
			reqd: 1,
		},
	],

	after_datatable_render: function (datatable) {
		$(datatable.wrapper).find('.dt-cell--col-0').hide();
	},

	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (!data) return value;

		const label = data.process_label;
		const fieldname = column.fieldname;

		// Subheader row (KGS/UNITS/HRS/VALUE labels) — muted grey
		if (label === "") {
			value = `<span style="color:#888; font-weight:600;">${value}</span>`;
			return value;
		}

		// Process rows — green background for non-zero data cells
		if (fieldname !== "process_label") {
			if (value && value !== "0.0" && value !== "00:00:00" && value !== "") {
				value = `<span style="background-color:#90EE90; padding:2px 4px; border-radius:3px;">${value}</span>`;
			}
		}

		// Process label column — teal/dark green like screenshot
		if (fieldname === "process_label") {
			value = `<span style="background-color:#2e8b57; color:#fff; padding:2px 6px; border-radius:3px; font-weight:600;">${value}</span>`;
		}

		return value;
	},
};	