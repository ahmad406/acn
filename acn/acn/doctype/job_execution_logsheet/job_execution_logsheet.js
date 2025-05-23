// Copyright (c) 2025, Ahmad Sayyed and contributors
// For license information, please see license.txt

frappe.ui.form.on("Job Execution Logsheet", {
	refresh(frm) {

	},
    setup(frm) {
        cur_frm.set_query("job_plan_id", function (frm) {
			return {
				 query: 'acn.acn.doctype.job_execution_logsheet.job_execution_logsheet.job_plan',
				 filters: {"internal_process_for":"Production"}

			}	
		});
    },
    job_plan_id:function(frm){
        frappe.call({
            method: "set_job_plan_details",
			doc: cur_frm.doc,
            callback: function(r) {
                if (r.message) {
                   cur_frm.refresh()
                }
            }
        });
    }
});
