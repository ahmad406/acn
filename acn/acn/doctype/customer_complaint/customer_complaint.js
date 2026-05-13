frappe.ui.form.on("Customer Complaint", {

	refresh(frm) {

		frm.set_query("part_no", function () {

			if (!frm.doc.customer_dc) {
				frappe.throw("Please select Customer DC first");
			}

			return {
				query: "acn.acn.doctype.customer_complaint.customer_complaint.get_part_no",
				filters: {
					customer_dc: frm.doc.customer_dc
				}
			};
		});
	},

	customer_dc(frm) {

		frm.set_value("part_no", null);

		frm.set_value("item_code", null);
		frm.set_value("item_name", null);
		frm.set_value("customer", null);
		frm.set_value("customer_dc_no", null);
		frm.set_value("invoice_no", null);
		frm.set_value("material", null);
		frm.set_value("process_type", null);
		frm.set_value("total_qty_nos", null);
		frm.set_value("total_qty_kgs", null);
	},

	part_no(frm) {

		if (!frm.doc.customer_dc || !frm.doc.part_no) {
			return;
		}

		frappe.call({
			method: "acn.acn.doctype.customer_complaint.customer_complaint.get_part_details",
			args: {
				customer_dc: frm.doc.customer_dc,
				part_no: frm.doc.part_no
			},
			callback(r) {

				if (!r.message) return;

				let d = r.message;

				frm.set_value("item_code", d.item_code);
				frm.set_value("item_name", d.item_name);
				frm.set_value("customer", d.customer);
				frm.set_value("customer_dc_no", d.customer_dc_no);
				frm.set_value("invoice_no", d.invoice_no);
				frm.set_value("material", d.material);
				frm.set_value("process_type", d.process_type);
				frm.set_value("total_qty_nos", d.total_qty_nos);
				frm.set_value("total_qty_kgs", d.total_qty_kgs);
			}
		});
	}
});