frappe.ui.form.on('Delivery Note', {
    setup: function (frm) {
        console.log("parent")

        cur_frm.set_query("customer_dc_id", "items", function (frm, cdt, cdn) {
            var child = locals[cdt][cdn];
            return {
                query: 'acn.custom_script.delivery_note.delivery_note.get_customer_dc',
                filters: {
                    "customer": cur_frm.doc.customer
                }


            }
        });
        cur_frm.set_query("part_no", "items", function (frm, cdt, cdn) {
            var child = locals[cdt][cdn];
            return {
                query: 'acn.custom_script.delivery_note.delivery_note.get_part_no',
                filters: { "customer_dc": child.customer_dc_id }

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

frappe.ui.form.on('Delivery Note Item', {
    d_qty_in_nos: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];

        if (d.d_qty_in_nos > d.balance_qty_in_nos) {
            frappe.msgprint(__('Delivery quantity cannot be more than balance quantity. It has been reset to the allowed limit.'));
            d.d_qty_in_nos = d.balance_qty_in_nos;

            d.d_qty_in_kgs = d.balance_qty_in_kgs;

            frm.refresh_field("items");
        } else {

            if (d.balance_qty_in_nos && d.balance_qty_in_kgs) {

                d.d_qty_in_kgs = (d.d_qty_in_nos / d.balance_qty_in_nos) * d.balance_qty_in_kgs;

            }
        }
        setTimeout(() => {


            if (d.rate_uom == "Nos") {

                frappe.model.set_value(cdt, cdn, "qty", d.d_qty_in_nos);
            }
            if (d.rate_uom == "Kgs") {
                frappe.model.set_value(cdt, cdn, "qty", d.d_qty_in_kgs);


            }
            if (d.rate_uom == "Minimum") {
                frappe.model.set_value(cdt, cdn, "qty", 1);


            }

            frm.refresh_field("items");
        }, 500);


    },
    customer_dc_id: function (frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        child.part_no = undefined
    },
    part_no: function (frm, cdt, cdn) {
        frappe.flags.dont_fetch_price_list_rate = true;

        var child = locals[cdt][cdn];

        // Ensure customer_dc_id exists
        if (!child.customer_dc_id) return;

        frappe.call({
            method: 'acn.custom_script.delivery_note.delivery_note.get_part_no_details',
            args: {
                part_no: child.part_no,
                customer_dc: child.customer_dc_id
            },
            callback: function (r) {
                if (r.message) {
                    console.log(r.message);
                    child.item_code = r.message.item_code
                    child.item_name = r.message.item_name
                    child.process_type = r.message.process_type
                    child.rate_uom = r.message.rate_uom
                    child.customer_process_ref = r.message.customer_process_ref_no
                    child.customer_dc_date = r.message.customer_dc_date
                    child.commitment = r.message.commitment_date
                 
                    child.d_qty_in_kgs = r.message.balance_qty_kgs
                    child.d_qty_in_nos = r.message.balance_qty_nos
                    child.balance_qty_in_kgs = r.message.balance_qty_kgs
                    child.balance_qty_in_nos = r.message.balance_qty_nos
                    child.uom = r.message.uom

                    child.customer_ref_no = r.message.customer_ref_no
                    child.customer_dc_no = r.message.customer_dc_no

                    child.so_date = r.message.so_date
                    child.process_name = r.message.process_name


                    setTimeout(() => {
                        console.log(r.message.balance_qty_nos)
                        if (child.rate_uom == "Nos") {

                            frappe.model.set_value(cdt, cdn, "qty", r.message.balance_qty_nos);
                        }
                        if (child.rate_uom == "Kgs") {
                            frappe.model.set_value(cdt, cdn, "qty", r.message.balance_qty_kgs);

                        }
                        if (child.rate_uom == "Minimum") {
                            frappe.model.set_value(cdt, cdn, "qty", 1);

                        }
                         frappe.model.set_value(cdt, cdn, "rate", r.message.rate);

                    }, 600);












                    // Example: Update other fields in this child row
                    // child.description = r.message.description;
                    // child.qty = r.message.qty;
                    // Refresh the row
                    frm.refresh_field('items');
                } else {
                    frappe.msgprint(__('No details found for this part number.'));
                }
            }
        });
    }
});
