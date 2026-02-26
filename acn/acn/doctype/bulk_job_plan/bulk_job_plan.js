frappe.ui.form.on("Bulk Job Plan", {

    setup(frm) {

        frm.set_query("internal_process", () => {
            return {
                query: "acn.acn.doctype.job_plan_scheduler.job_plan_scheduler.get_internal_process"
            }
        });

        frm.set_query("job_card_id", () => {
            return {
                query: "acn.acn.doctype.bulk_job_plan.bulk_job_plan.get_job_card_bulk"
            }
        });

        frm.set_query("customer", () => {
            return {
                query: "acn.acn.doctype.bulk_job_plan.bulk_job_plan.get_active_customers"
            }
        });
        frm.set_query("furnace_code", "bulk_planning", function (doc, cdt, cdn) {

            let row = locals[cdt][cdn];

            return {
                query: "acn.acn.doctype.job_plan_scheduler.job_plan_scheduler.furnace_code",
                filters: {
                    furnace_process: row.furnace_process
                }
            };
        });

        frm.set_query("mrn_no", () => {
            return {
                query: "acn.acn.doctype.bulk_job_plan.bulk_job_plan.get_active_mrn"
            }
        });

    },

    refresh(frm) {

        if (frm.doc.docstatus === 1) {
            frm.get_field("fetch_data").$input.prop("disabled", true);
        }
    },

    download(frm) {
        download_bulk_grid(frm);
    },

    fetch_data(frm) {

        frappe.call({
            method: "acn.acn.doctype.bulk_job_plan.bulk_job_plan.get_bulk_data",
            args: {
                internal_process: frm.doc.internal_process,
                customer: frm.doc.customer,
                job_card: frm.doc.job_card_id,
                mrn_no: frm.doc.mrn_no,
            },
            freeze: true,
            callback(r) {

                frm.clear_table("bulk_planning");

                (r.message || []).forEach(d => {
                    let row = frm.add_child("bulk_planning", d);
                });

                frm.refresh_field("bulk_planning");

                frappe.show_alert({
                    message: "Data loaded successfully",
                    indicator: "green"
                });
            }
        });
    },

});



frappe.ui.form.on("Bulk Planning", {

    bulk_planning_add(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        row.plan_qty_in_nos = row.balance_plan_qty_in_nos;
        row.plan_qty_in_kgs = row.balance_plan_qty_in_kgs;

        toggle_planned_checkbox(row);


        frm.refresh_field("bulk_planning");
    },


    plan_qty_in_nos(frm, cdt, cdn) {

        let d = locals[cdt][cdn];

        if (d.plan_qty_in_nos > d.balance_plan_qty_in_nos) {
            frappe.msgprint("Plan Qty cannot exceed balance");

            d.plan_qty_in_nos = d.balance_plan_qty_in_nos;
            d.plan_qty_in_kgs = d.balance_plan_qty_in_kgs;
        }
        else if (d.balance_plan_qty_in_nos && d.balance_plan_qty_in_kgs) {

            d.plan_qty_in_kgs =
                (d.plan_qty_in_nos / d.balance_plan_qty_in_nos)
                * d.balance_plan_qty_in_kgs;
        }

        toggle_planned_checkbox(d);

        frm.refresh_field("bulk_planning");
    },

    plan_qty_in_kgs(frm, cdt, cdn) {

        let d = locals[cdt][cdn];

        toggle_planned_checkbox(d);

        frm.refresh_field("bulk_planning");
    }

});



function download_bulk_grid(frm) {

    let rows = frm.doc.bulk_planning || [];

    if (!rows.length) {
        frappe.msgprint("No rows to download");
        return;
    }

    // get child table meta dynamically
    let meta = frappe.get_meta("Bulk Planning");

    // take only real fields (skip layout fields)
    let fields = meta.fields.filter(f =>
        !["Column Break", "Section Break", "Button"].includes(f.fieldtype)
    );

    // headers = labels
    let headers = fields.map(f => f.label);

    let csv = [];
    csv.push(headers.join(","));

    rows.forEach(row => {

        let line = fields.map(f => {

            let val = row[f.fieldname];

            if (val === undefined || val === null) val = "";

            // escape commas
            val = String(val).replace(/,/g, " ");

            return val;
        });

        csv.push(line.join(","));
    });

    let blob = new Blob([csv.join("\n")], {
        type: "text/csv;charset=utf-8;"
    });

    let link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `Bulk_Planning_${frm.doc.name || "Draft"}.csv`;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}


function toggle_planned_checkbox(row) {

    let hasNos = flt(row.plan_qty_in_nos) > 0;
    let hasKgs = flt(row.plan_qty_in_kgs) > 0;

    row.planned = (hasNos || hasKgs) ? 1 : 0;
}