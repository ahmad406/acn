frappe.ui.form.on("Purchase Invoice", {
     validate: function (frm) {
        if (frm.doc.naming_series!='WR-.FY.-'){
            cur_frm.set_value("subitem",[])
        }
     },
    refresh: function (frm) {

        // console.log("wokring")
        if (frm.is_new() && frm.doc.payment_terms_template) {
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
                callback: function (r) {
                    if (r.message) {
                        frm.set_value("payment_schedule", r.message);

                        // Optional: Refresh child table
                        frm.refresh_field("payment_schedule");
                    }
                }
            });
        }
        
        if (frm.doc.docstatus === 0 ) {
            frm.add_custom_button(__('Subcontract Delivery Note'), function () {
                erpnext.utils.map_current_doc({
                    method: "acn.acn.doctype.subcontract_delivery_note.subcontract_delivery_note.make_purchase_invoice_from_subcontract_dn",
                    source_doctype: "Subcontract Delivery Note",
                    target: frm,
                    date_field: "posting_date",
                    setters: {
                        subcontractor: frm.doc.supplier,
                        company: frm.doc.company
                    },
                    get_query_filters: {
                        docstatus: 1,
                        Subcontractor: frm.doc.supplier,
                        company: frm.doc.company
                    }
                });
            }, __("Get Items From"));
        }


    }
});
