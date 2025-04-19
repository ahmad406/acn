// Copyright (c) 2025, Ahmad Sayyed and contributors
// For license information, please see license.txt

frappe.ui.form.on("Job Execution Logsheet", {
	refresh(frm) {

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
