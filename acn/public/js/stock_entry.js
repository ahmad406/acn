frappe.ui.form.on('Stock Entry', {
    update_bill_info(frm) {
        show_update_bill_info_dialog(frm);
    }
});

function show_update_bill_info_dialog(frm) {
    const d = new frappe.ui.Dialog({
        title: __('Update Bill From Info'),
        fields: [
            {
                fieldname: 'bill_from_address',
                label: __('Bill From Address'),
                fieldtype: 'Link',
                options: 'Address',
                reqd: 1,
            },
        ],
        primary_action_label: __('Update'),
        primary_action(values) {
            frappe.call({
                method: 'acn.custom_script.stock_entry.stock_entry.update_bill_from_info',
                args: {
                    stock_entry: frm.doc.name,
                    bill_from_address: values.bill_from_address,
                },
                callback(r) {
                    if (r.message) {
                        frappe.show_alert({ message: __('Bill From info updated'), indicator: 'green' });
                        d.hide();
                        frm.reload_doc();
                    }
                },
            });
        },
    });
    d.show();
}