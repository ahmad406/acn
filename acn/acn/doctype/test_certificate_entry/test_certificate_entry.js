// Copyright (c) 2025, Ahmad Sayyed and contributors
// For license information, please see license.txt

frappe.ui.form.on("Test Certificate entry", {
	refresh(frm) {

	},
    job_card_id:function(frm){
        frappe.call({
            method: "get_details",
			doc: cur_frm.doc,
            callback: function(r) {
                if (r.message) {
                   cur_frm.refresh()
                }
            }
        });
    }
});
