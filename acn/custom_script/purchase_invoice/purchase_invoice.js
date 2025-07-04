frappe.ui.form.on("Purchase Invoice", {
    refresh: function(frm) {
	console.log("wokring")
        if (frm.doc.is_new() && frm.doc.payment_terms_template) {
            let posting_date = frm.doc.posting_date || frm.doc.transaction_date;

            frappe.call({
                method: "erpnext.controllers.accounts_controller.get_payment_terms",
                args: {
                    terms_template: frm.doc.payment_terms_template,
                    posting_date: posting_date,
                    grand_total: frm.doc.rounded_total || frm.doc.grand_total,
                    base_grand_total: frm.doc.base_rounded_total || frm.doc.base_grand_total,
                    bill_date: frm.doc.bill_date
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value("payment_schedule", r.message);

                        // Optional: Refresh child table
                        frm.refresh_field("payment_schedule");
                    }
                }
            });
        }
    }
});
