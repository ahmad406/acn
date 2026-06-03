frappe.ui.form.on('CAPA', {
    refresh(frm) {
        frm.set_query("customer_complaint_id", function () {
            return {
                filters: [
                    ["Customer Complaint", "capa", "=", 1],
                    ["Customer Complaint", "capa_no", "is", "not set"],
                    ["Customer Complaint", "docstatus", "=", 1],
                    ["Customer Complaint", "customer", "=", frm.doc.customer]
                ]
            };
        });
    },

    customer_complaint_id: function(frm) {

        if (!frm.doc.customer_complaint_id) return;

        frappe.db.get_doc("Customer Complaint", frm.doc.customer_complaint_id)
            .then(cc => {

                if (!cc.customer_dc || !cc.part_no) return;

                frappe.db.get_list("Job Card for process", {
                    filters: {
                        customer_dc: cc.customer_dc,
                        part_no: cc.part_no
                    },
                    fields: ["name", "customer_req"],
                    limit: 1
                }).then(res => {

                    if (res && res.length) {

                        frm.set_value(
                            "customer_requirement",
                            res[0].customer_req || ""
                        );

                    } else {

                        frm.set_value("customer_requirement", "");

                    }
                });
            });
    }
});