// Copyright (c) 2025, Ahmad Sayyed and contributors
// For license information, please see license.txt

frappe.ui.form.on("Test Certificate entry", {
	refresh(frm) {

	},
    setup(frm) {
        cur_frm.set_query("lab_inspection_id", function (frm) {
			return {
				 query: 'acn.acn.doctype.test_certificate_entry.test_certificate_entry.lab_inspection',

			}	
		});
         cur_frm.set_query("job_card_id", function (frm) {
			return {
				 query: 'acn.acn.doctype.test_certificate_entry.test_certificate_entry.job_card_process',
                 filters: {"lab_inspection":cur_frm.doc.lab_inspection_id}

			}	
		});
    },
    lab_inspection_id:function(frm){
cur_frm.set_value("job_card_id",undefined)
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

