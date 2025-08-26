frappe.ui.form.on('Sales Order', {
	refresh: function(frm) {
		console.log("Sales Order Refresh Triggered");
	},
	setup: function(frm) {
		frm.fields_dict['items'].grid.get_field('custom_part_no').get_query = function(doc, cdt, cdn) {
			var child = locals[cdt][cdn];
			return {
				query: 'acn.custom_script.sales_order.sales_order.get_part_no',
				filters: {
					"customer": cur_frm.doc.customer
				}
	
			}
        };

		
			// $(frm.wrapper).on("grid-row-render", function (e, grid_row) {
			// 	if (
			// 		in_list(["Sales Order Item"], grid_row.doc.doctype)
			// 	) {
			// 		let cl = grid_row.columns_list;
			// 		if (grid_row.doc.custom_rate_uom == "Kgs") {
						
			// 			if ('custom_qty_in_nos' in grid_row.columns) {
			// 				cl[grid_row.columns.custom_qty_in_nos.column_index].df.read_only = 1;
			// 			}
			// 			if ('custom_qty_in_kgs' in grid_row.columns) {
			// 				cl[grid_row.columns.custom_qty_in_kgs.column_index].df.read_only = 0;
			// 			}
			// 		}
			// 		if (grid_row.doc.custom_rate_uom == "Nos") {
			// 			if ('custom_qty_in_kgs' in grid_row.columns) {
			// 				cl[grid_row.columns.custom_qty_in_kgs.column_index].df.read_only = 1;
			// 			}
			// 			if ('custom_qty_in_nos' in grid_row.columns) {
			// 				cl[grid_row.columns.custom_qty_in_nos.column_index].df.read_only = 0;
			// 			}
			// 		}
			// 		if (grid_row.doc.custom_rate_uom == "Minimum") {
			// 			if ('custom_qty_in_kgs' in grid_row.columns) {
			// 				cl[grid_row.columns.custom_qty_in_kgs.column_index].df.read_only = 1;
			// 			}
			// 			if ('custom_qty_in_nos' in grid_row.columns) {
			// 				cl[grid_row.columns.custom_qty_in_nos.column_index].df.read_only = 1;
			// 			}
			// 		}
			// 	}
	
	
			// });

	}

});


frappe.ui.form.on('Sales Order Item', {
	custom_part_no: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];

		if (row.custom_part_no && frm.doc.customer) {
			frappe.call({
                method: "acn.custom_script.sales_order.sales_order.get_process_rate",
				args: {
					part_no: row.custom_part_no,
					customer: frm.doc.customer
				},
				callback: function(r) {
					console.log(r)
					if (r.message) {

						frappe.model.set_value(cdt, cdn, "custom_rate_uom", r.message.rate_uom);
						// frappe.model.set_value(cdt, cdn, "item_code", r.message.item_code);
						row.custom_process_type =  r.message.process_type
						row.custom_process_name =  r.message.process_name
						row.custom_material =  r.message.material
						row.custom_rate_uom =  r.message.rate_uom
						row.custom_customer_process_ref_no =  r.message.customer_ref
						if(cur_frm.doc.docstatus==0){
							frappe.model.set_value(cdt, cdn, "item_code", r.message.item_code);

							if (r.message.rate_uom=="Minimum") {
								frappe.model.set_value(cdt, cdn, "qty",1);
							}
							setTimeout(() => {
								
								frappe.model.set_value(cdt, cdn, "rate", r.message.process_rate);
							}, 900);
						}
						if(cur_frm.doc.docstatus==1){
							row.item_code=r.message.item_code
							row.item_name=r.message.item_name
						}
					
						cur_frm.refresh()

					}
				}
			});
		}
	},
	custom_qty_in_nos: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.custom_rate_uom=="Nos") {
			frappe.model.set_value(cdt, cdn, "qty", row.custom_qty_in_nos);
		}
	},
	custom_qty_in_kgs: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.custom_rate_uom=="Kgs") {
			frappe.model.set_value(cdt, cdn, "qty", row.custom_qty_in_kgs);

		}
	}
});
