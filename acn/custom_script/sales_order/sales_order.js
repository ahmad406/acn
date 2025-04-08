frappe.ui.form.on('Sales Order', {
	refresh: function(frm) {
		// frappe.msgprint("Sales Order Refresh Triggered");
	},

});


frappe.ui.form.on('Sales Order Item', {
	part_no: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];

		if (row.part_no && frm.doc.customer) {
			frappe.call({
                method: "acn.custom_script.sales_order.sales_order.get_process_rate",
				args: {
					part_no: row.part_no,
					customer: frm.doc.customer
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, "custom_rate_uom", r.message.rate_uom);
					}
				}
			});
		}
	},
	custom_qty_in_nos: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.custom_qty_in_nos) {
			frappe.model.set_value(cdt, cdn, "qty", row.custom_qty_in_nos);
		}
	},
	custom_qty_in_kgs: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.custom_qty_in_nos) {
			frappe.model.set_value(cdt, cdn, "qty", row.custom_qty_in_kgs);
		}
	}
});
