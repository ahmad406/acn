frappe.query_reports["Furnace Wise Tonnage"] = {
	filters: [
		{
			fieldname: "month",
			label: __("Month"),
			fieldtype: "Select",
			options: [
				{ value: 1,  label: __("January") },
				{ value: 2,  label: __("February") },
				{ value: 3,  label: __("March") },
				{ value: 4,  label: __("April") },
				{ value: 5,  label: __("May") },
				{ value: 6,  label: __("June") },
				{ value: 7,  label: __("July") },
				{ value: 8,  label: __("August") },
				{ value: 9,  label: __("September") },
				{ value: 10, label: __("October") },
				{ value: 11, label: __("November") },
				{ value: 12, label: __("December") },
			],
			default: String(parseInt(frappe.datetime.get_today().split("-")[1])),
			reqd: 1,
		},
		{
			fieldname: "year",
			label: __("Year"),
			fieldtype: "Select",
			options: (function () {
				let currentYear = parseInt(frappe.datetime.get_today().split("-")[0]);
				let years = [];
				for (let y = currentYear - 5; y <= currentYear + 1; y++) {
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

		// TOTAL TONNAGE row — orange background
		if (label === "TOTAL TONNAGE") {
			value = `<b>${value}</b>`;
			if (column.fieldname !== "furnace_label") {
				value = `<span style="background-color:#f4a460; padding:2px 6px; border-radius:3px;">${value}</span>`;
			}
		}

		// Day rows — green for non-zero values
		if (!isNaN(parseInt(label)) && column.fieldname !== "furnace_label") {
			if (value && value !== "0.00") {
				value = `<span style="background-color:#90EE90; padding:2px 6px; border-radius:3px;">${value}</span>`;
			}
		}

		// KGS subheader row — muted
		if (label === "KGS") {
			value = `<span style="color:#888; font-weight:600;">${value}</span>`;
		}

		return value;
	},
};