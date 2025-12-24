// Copyright (c) 2025, Ahmad Sayyed and contributors
// For license information, please see license.txt

frappe.ui.form.on("Job Plan Scheduler", {
	setup(frm) {

		cur_frm.set_query("internal_process", function (frm) {
			return {
				query: 'acn.acn.doctype.job_plan_scheduler.job_plan_scheduler.get_internal_process',
				//  filters: {"project":cur_frm.doc.project,"start_date":cur_frm.doc.planned_start_date}

			}
		});
		cur_frm.set_query("furnace_code", function (frm) {
			return {
				query: 'acn.acn.doctype.job_plan_scheduler.job_plan_scheduler.furnace_code',
				filters: { "furnace_process": cur_frm.doc.furnace_process }

			}
		});
		cur_frm.set_query("furnace_code", "parameters_with_acceptance_criteria", function (frm) {
			return {
				query: 'acn.acn.doctype.job_plan_scheduler.job_plan_scheduler.furnace_code',
				filters: { "furnace_process": cur_frm.doc.furnace_process }

			}
		});
		cur_frm.set_query("job_card_id", "job_card_details", function (frm) {
			    let selected_job_cards = (cur_frm.doc.job_card_details || [])
        .map(d => d.job_card_id)
        .filter(Boolean);

			return {
				query: 'acn.acn.doctype.job_plan_scheduler.job_plan_scheduler.get_job_card',
				filters: { 
					"internal_process": cur_frm.doc.internal_process,
					  "exclude_job_cards": selected_job_cards
				 }

			}
		});



		// $(frm.wrapper).on("grid-row-render", function (e, grid_row) {
		// 	if (in_list(["Job Card details"], grid_row.doc.doctype)) {
		// 		if (grid_row) {
		// 			let cl = grid_row.columns
		// 			if (grid_row.doc.lot_no == 1) {
		// 				if ('planned_qty_in_kgs' in cl) { grid_row.columns_list[cl.planned_qty_in_kgs.column_index].df.read_only = 0 }
		// 				if ('planned_qty_in_nos' in cl) { grid_row.columns_list[cl.planned_qty_in_nos.column_index].df.read_only = 0 }

		// 			}
		// 			else {
		// 				if ('planned_qty_in_kgs' in cl) { grid_row.columns_list[cl.planned_qty_in_kgs.column_index].df.read_only = 1 }
		// 				if ('planned_qty_in_nos' in cl) { grid_row.columns_list[cl.planned_qty_in_nos.column_index].df.read_only = 1 }

		// 			}

		// 		}
		// 	}
		// });

	},
	internal_process(frm) {
		if (frm.doc.internal_process) {

			frappe.call({
				method: "get_internal_process_details",
				doc: cur_frm.doc,
				callback: function (r) {
					if (r.message) {
						cur_frm.refresh()
						cur_frm.dirty()
					}
				}
			});
		}
	},
	calculate_end_datetime(frm) {
		frappe.call({
			method: "calculated_end",
			doc: cur_frm.doc,
			callback: function (r) {
				if (r.message) {
					cur_frm.refresh()
					cur_frm.dirty()
				}
			}
		});
	},
	update_job_paramenters: function (frm) {
		frappe.call({
			method: "update_job_card_table",
			doc: cur_frm.doc,
			callback: function (r) {
				if (r.message) {
					cur_frm.refresh()
					cur_frm.dirty()

				}
			}
		});

	}
	// furnace_code(frm) {
	// 	frappe.call({
	// 		method: "get_furnace_code_details",
	// 		doc: cur_frm.doc,
	// 		callback: function(r) {
	// 			if (r.message) {
	// 			   cur_frm.refresh()
	// 			}
	// 		}
	// 	});
	// }
});

frappe.ui.form.on("Job Card details", {
	job_card_id: function (frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		frappe.call({
			method: "get_job_details",
			args: {
				"row": d
			},
			doc: cur_frm.doc,
			callback: function (r) {
				// if (r.message) {
				cur_frm.refresh();
				// }
			}
		});
	},
	planned_qty_in_nos: function (frm, cdt, cdn) {
		var d = locals[cdt][cdn];

		if (d.planned_qty_in_nos > d.balance_plan_qty_in_nos) {
			frappe.msgprint(__('Planned quantity cannot be more than balance quantity. It has been reset to the allowed limit.'));
			d.planned_qty_in_nos = d.balance_plan_qty_in_nos;
			d.planned_qty_in_kgs = d.balance_plan_qty_in_kgs;
			frm.refresh_field("job_card_details");
		} else {
			if (d.balance_plan_qty_in_nos && d.balance_plan_qty_in_kgs) {
				d.planned_qty_in_kgs = (d.planned_qty_in_nos / d.balance_plan_qty_in_nos) * d.balance_plan_qty_in_kgs;
				frm.refresh_field("job_card_details");
			}
		}
	}


});


