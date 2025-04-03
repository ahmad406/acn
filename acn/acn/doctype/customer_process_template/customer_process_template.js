frappe.ui.form.on("Customer Process template", {
    process_type: function(frm) {
        if (!frm.doc.process_type) {
            return;
        }

        frappe.call({
            method: "get_parameter",
            doc: frm.doc,
            callback: function(r) {
                frm.dirty()
                frm.refresh_fields();
            }
        });
    },

     setup: function(frm) {
        frm.fields_dict["customer_requirements"].grid.get_field("process_parameter").get_query = function(doc, cdt, cdn) {
            return {
                query: "acn.acn.doctype.customer_process_template.customer_process_template.get_param",
                filters: { "process_type": frm.doc.process_type || "" }
            };
        };
    }
});

