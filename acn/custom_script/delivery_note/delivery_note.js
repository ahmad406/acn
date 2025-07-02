frappe.ui.form.on('Delivery Note', {
    setup: function (frm) {
        console.log("yeys")
        cur_frm.set_query("customer_dc_id", "items", function (frm, cdt, cdn) {
            var child = locals[cdt][cdn];
            return {
                query: 'acn.custom_script.delivery_note.delivery_note.get_customer_dc',

            }
        });
        cur_frm.set_query("part_no", "items", function (frm, cdt, cdn) {
            var child = locals[cdt][cdn];
            return {
                query: 'acn.custom_script.delivery_note.delivery_note.get_part_no',
                filters: { "customer_dc_id": child.customer_dc_id }

            }
        });
    },
    customer: function (frm) {
        frm.clear_table('document_enclosed_for_dispatch');
        if (frm.doc.customer) {
            frappe.db.get_doc('Customer wise documents enclosed', frm.doc.customer)
                .then(source_doc => {

                    (source_doc.documents_enclosed || []).forEach(row => {
                        let new_row = frm.add_child('document_enclosed_for_dispatch');
                        new_row.document_name = row.document_name;

                    });

                })
                .catch(err => {
                    frappe.msgprint(__('Could not fetch documents: ' + err.message));
                });
        }
        frm.refresh_field('document_enclosed_for_dispatch');
    }
})