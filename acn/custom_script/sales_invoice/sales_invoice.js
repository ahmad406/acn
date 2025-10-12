frappe.ui.form.on('Sales Invoice', {

    // customer: function (frm) {
    //     frm.clear_table('document_enclosed_for_dispatch');
    //     if (frm.doc.customer) {
    //         frappe.db.get_doc('Customer wise documents enclosed', frm.doc.customer)
    //             .then(source_doc => {

    //                 (source_doc.documents_enclosed || []).forEach(row => {
    //                     let new_row = frm.add_child('document_enclosed_for_dispatch');
    //                     new_row.document_name = row.document_name;

    //                 });

    //             })
    //             .catch(err => {
    //                 frappe.msgprint(__('Could not fetch documents: ' + err.message));
    //             });
    //     }
    //     frm.refresh_field('document_enclosed_for_dispatch');
    // },
    refresh: function (frm) {
        if (frm.is_new()) {
            if (frm.doc.items) {
                frappe.db.get_doc('Delivery Note', cur_frm.doc.items[0].delivery_note)
                    .then(source_doc => {

                        (source_doc.document_enclosed_for_dispatch || []).forEach(row => {
                            let new_row = frm.add_child('document_enclosed_for_dispatch');
                            new_row.document_name = row.document_name;

                        });

                    })
                    .catch(err => {
                        frappe.msgprint(__('Could not fetch documents: ' + err.message));
                    });
            }
            frm.refresh_field

        }

    }
})