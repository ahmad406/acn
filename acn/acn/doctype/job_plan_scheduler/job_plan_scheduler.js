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
				 filters: {"furnace_process":cur_frm.doc.furnace_process}

			}	
		});
		cur_frm.set_query("job_card_id","job_card_details", function (frm) {
			return {
				 query: 'acn.acn.doctype.job_plan_scheduler.job_plan_scheduler.get_job_card',
				 filters: {"internal_process":cur_frm.doc.internal_process}

			}	
		});

	},
	internal_process(frm) {
		frappe.call({
            method: "get_internal_process_details",
			doc: cur_frm.doc,
            callback: function(r) {
                if (r.message) {
                   cur_frm.refresh()
                }
            }
        });
	},
	furnace_code(frm) {
		frappe.call({
			method: "get_furnace_code_details",
			doc: cur_frm.doc,
			callback: function(r) {
				if (r.message) {
				   cur_frm.refresh()
				}
			}
		});
	}
});



