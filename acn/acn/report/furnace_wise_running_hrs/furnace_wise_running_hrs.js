frappe.query_reports["Furnace Wise Running Hrs"] = {
	filters: [
		{
			fieldname: "month",
			label: __("Month"),
			fieldtype: "Select",
			options: [
				{ value: 1, label: __("January") },
				{ value: 2, label: __("February") },
				{ value: 3, label: __("March") },
				{ value: 4, label: __("April") },
				{ value: 5, label: __("May") },
				{ value: 6, label: __("June") },
				{ value: 7, label: __("July") },
				{ value: 8, label: __("August") },
				{ value: 9, label: __("September") },
				{ value: 10, label: __("October") },
				{ value: 11, label: __("November") },
				{ value: 12, label: __("December") },
			],
			default: String(frappe.datetime.get_today().split("-")[1] | 0),
			reqd: 1,
		},
		{
			fieldname: "year",
			label: __("Year"),
			fieldtype: "Select",
			options: (function () {
				let currentYear = parseInt(frappe.datetime.get_today().split("-")[0]);
				let years = [];
				for (let y = currentYear - 10; y <= currentYear + 1; y++) {
					years.push({ value: y, label: String(y) });
				}
				return years;
			})(),
			default: frappe.datetime.get_today().split("-")[0],
			reqd: 1,
		},
	],

	after_datatable_render: function (datatable) {
		$(datatable.wrapper).find('.dt-cell--col-0').hide();
	},

	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (!data) return value;

		const label = data.furnace_label;

		// Bold + dark background for summary rows
		const summaryRows = [
			"TOTAL RUNNING HOURS",
			"TOTAL IDLE TIME",
			"TOTAL HOURS",
			"FURNACE UTILISATION IN %",
		];

		if (summaryRows.includes(label)) {
			value = `<b>${value}</b>`;
			if (column.fieldname !== "furnace_label") {
				// Orange background for summary data cells (matches screenshot)
				value = `<span style="background-color:#f4a460; padding:2px 6px; border-radius:3px;">${value}</span>`;
			}
		}

		// Green background for day rows (data cells only)
		if (!isNaN(parseInt(label)) && column.fieldname !== "furnace_label") {
			// Check if non-zero time
			if (value && value !== "00:00:00") {
				value = `<span style="background-color:#90EE90; padding:2px 6px; border-radius:3px;">${value}</span>`;
			}
		}

		// Grey / muted for the HRS subheader row
		if (label === "HRS") {
			value = `<span style="color:#888; font-weight:600;">${value}</span>`;
		}

		return value;
	},
};