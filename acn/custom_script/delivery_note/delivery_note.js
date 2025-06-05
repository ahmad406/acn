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
    } 

})