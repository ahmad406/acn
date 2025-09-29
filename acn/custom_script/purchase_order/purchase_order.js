frappe.ui.form.on('Purchase Order', {
    refresh: function (frm) {
        // Hide/Show submit button

        // Add custom buttons only when doc is submitted
        if (frm.doc.open_order && frm.doc.reopen === 1) {

            frm.add_custom_button(__('Re-Close Order'), function () {
                frappe.call({
                    method: "acn.custom_script.purchase_order.purchase_order.reopen_order",
                    args: { name: frm.doc.name, docstatus: 1 }, // keep as submitted
                    callback: function (r) {
                        if (r.message) {
                            frappe.msgprint(r.message);
                            frm.reload_doc();
                        }
                    }
                });
            });
        }
        if (frm.doc.open_order && frm.doc.docstatus == 1) {
            frm.add_custom_button(__('Reopen Order'), function () {
                frappe.call({
                    method: "acn.custom_script.purchase_order.purchase_order.reopen_order",
                    args: { name: frm.doc.name, docstatus: 0 }, // set back to draft
                    callback: function (r) {
                        if (r.message) {
                            frappe.msgprint(r.message);
                            frm.reload_doc();
                        }
                    }
                });
            });
        }

    
}
});
