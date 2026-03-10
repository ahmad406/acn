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
        setTimeout(() => {
            cur_frm.remove_custom_button('Delivery Note', 'Get Items From');
            cur_frm.remove_custom_button('Sales Order', 'Get Items From');
            cur_frm.remove_custom_button('Quotation', 'Get Items From');
            cur_frm.remove_custom_button('Timesheet', 'Get Items From');
        }, 500);
        if (frm.is_new()) {
            if (frm.doc.items) {
                if (cur_frm.doc.items[0].delivery_note) {
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
            }
            frm.refresh_field

        }
    },

    validate(frm) {
        set_po_from_customer_dc(frm);
    },
    onload: function (frm) {
        setTimeout(() => {
            cur_frm.remove_custom_button('Delivery Note', 'Get Items From');
            cur_frm.remove_custom_button('Sales Order', 'Get Items From');
            cur_frm.remove_custom_button('Quotation', 'Get Items From');
            cur_frm.remove_custom_button('Timesheet', 'Get Items From');

        }, 200);
    }
})


function set_po_from_customer_dc(frm) {

    if (!frm.doc.items || !frm.doc.items.length) return;

    let row = frm.doc.items[0];

    if (!row.customer_dc_id) return;

    frappe.db.get_value(
        "Customer DC",
        row.customer_dc_id,
        ["customer_order_no", "customer_order_date"]
    ).then(r => {

        if (!r.message) return;

        frm.set_value("po_no", r.message.customer_order_no);
        frm.set_value("po_date", r.message.customer_order_date);
    });
}